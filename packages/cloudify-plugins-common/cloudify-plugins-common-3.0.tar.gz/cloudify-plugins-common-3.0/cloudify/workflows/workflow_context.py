########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

__author__ = 'dank'


import copy
import uuid
import importlib

import celery


from cloudify.manager import get_node_instance, update_node_instance, \
    update_execution_status, get_rest_client, get_bootstrap_context
from cloudify.workflows.tasks import (RemoteWorkflowTask,
                                      LocalWorkflowTask,
                                      NOPLocalWorkflowTask,
                                      DEFAULT_TOTAL_RETRIES,
                                      DEFAULT_RETRY_INTERVAL)
from cloudify.workflows.tasks_graph import TaskDependencyGraph
from cloudify.logs import (CloudifyWorkflowLoggingHandler,
                           CloudifyWorkflowNodeLoggingHandler,
                           init_cloudify_logger,
                           send_workflow_event,
                           send_workflow_node_event)


class CloudifyWorkflowRelationshipInstance(object):
    """A node instance relationship instance"""

    def __init__(self, ctx, node_instance, relationship_instance):
        """
        :param ctx: a CloudifyWorkflowContext instance
        :param node_instance: a CloudifyWorkflowNodeInstance instance
        :param relationship_instance: A relationship dict from a NodeInstance
               instance (of the rest client model)
        """
        self.ctx = ctx
        self.node_instance = node_instance
        self._relationship_instance = relationship_instance
        self._relationship = node_instance.node.get_relationship(
            relationship_instance['target_name'])

    @property
    def target_id(self):
        """The relationship target node id"""
        return self._relationship_instance.get('target_id')

    @property
    def target_node_instance(self):
        """The relationship target node WorkflowContextNodeInstance instance"""
        return self.ctx.get_node_instance(self.target_id)

    @property
    def relationship(self):
        return self._relationship

    def execute_source_operation(self, operation, kwargs=None):
        """
        Execute a node relationship source operation

        :param operation: The node relationship operation
        :param kwargs: optional kwargs to be passed to the called operation
        """
        return self.ctx._execute_operation(
            operation,
            node_instance=self.node_instance,
            related_node_instance=self.target_node_instance,
            operations=self.relationship.source_operations,
            kwargs=kwargs)

    def execute_target_operation(self, operation, kwargs=None):
        """
        Execute a node relationship target operation

        :param operation: The node relationship operation
        :param kwargs: optional kwargs to be passed to the called operation
        """
        return self.ctx._execute_operation(
            operation,
            node_instance=self.target_node_instance,
            related_node_instance=self.node_instance,
            operations=self.relationship.target_operations,
            kwargs=kwargs)


class CloudifyWorkflowRelationship(object):
    """A node relationship"""

    def __init__(self, ctx, node, relationship):
        """
        :param ctx: a CloudifyWorkflowContext instance
        :param node: a CloudifyWorkflowNode instance
        :param relationship: a relationship dict from a Node instance (of the
               rest client mode)
        """
        self.ctx = ctx
        self.node = node
        self._relationship = relationship

    @property
    def target_id(self):
        """The relationship target node id"""
        return self._relationship.get('target_id')

    @property
    def target_node(self):
        """The relationship target node WorkflowContextNode instance"""
        return self.ctx.get_node(self.target_id)

    @property
    def source_operations(self):
        """The relationship source operations"""
        return self._relationship.get('source_operations', {})

    @property
    def target_operations(self):
        """The relationship target operations"""
        return self._relationship.get('target_operations', {})


class CloudifyWorkflowNodeInstance(object):
    """A plan node instance"""

    def __init__(self, ctx, node, node_instance):
        """
        :param ctx: a CloudifyWorkflowContext instance
        :param node: a CloudifyWorkflowContextNode instance
        :param node_instance: a NodeInstance (rest client response model)
        """
        self.ctx = ctx
        self._node = node
        self._node_instance = node_instance
        self._relationship_instances = {
            relationship_instance['target_id']:
            CloudifyWorkflowRelationshipInstance(self.ctx,
                                                 self,
                                                 relationship_instance)
            for relationship_instance in node_instance.relationships
        }
        # adding the node instance to the node instances map
        node._node_instances[self.id] = self

        self._logger = None

    def set_state(self, state, runtime_properties=None):
        """
        Set the node state

        :param state: The node state
        :return: the state set
        """
        def set_state_task():
            node_state = get_node_instance(self.id)
            node_state.state = state
            if runtime_properties is not None:
                node_state.runtime_properties.update(runtime_properties)
            update_node_instance(node_state)
            return node_state
        return self.ctx.local_task(
            local_task=set_state_task,
            node=self,
            info=state)

    def get_state(self):
        """
        Get the node state

        :return: The node state
        """
        def get_state_task():
            return get_node_instance(self.id).state
        return self.ctx.local_task(
            local_task=get_state_task,
            node=self)

    def send_event(self, event, additional_context=None):
        """
        Sends a workflow node event to RabbitMQ

        :param event: The event
        :param additional_context: additional context to be added to the
               context
        """
        def send_event_task():
            send_workflow_node_event(ctx=self,
                                     event_type='workflow_node_event',
                                     message=event,
                                     additional_context=additional_context)
        return self.ctx.local_task(
            local_task=send_event_task,
            node=self,
            info=event)

    def execute_operation(self, operation, kwargs=None):
        """
        Execute a node operation

        :param operation: The node operation
        :param kwargs: optional kwargs to be passed to the called operation
        """
        return self.ctx._execute_operation(operation=operation,
                                           node_instance=self,
                                           operations=self.node.operations,
                                           kwargs=kwargs)

    @property
    def id(self):
        """The node instance id"""
        return self._node_instance.id

    @property
    def node_id(self):
        """The node id (this instance is an instance of that node)"""
        return self._node_instance.node_id

    @property
    def relationships(self):
        """The node relationships"""
        return self._relationship_instances.itervalues()

    @property
    def node(self):
        return self._node

    @property
    def logger(self):
        """A logger for this workflow node"""
        if self._logger is None:
            self._logger = self._init_cloudify_logger()
        return self._logger

    def _init_cloudify_logger(self):
        logger_name = self.id if self.id is not None \
            else 'cloudify_workflow_node'
        handler = CloudifyWorkflowNodeLoggingHandler(self)
        return init_cloudify_logger(handler, logger_name)


class CloudifyWorkflowNode(object):
    """A plan node instance"""

    def __init__(self, ctx, node):
        """
        :param ctx: a CloudifyWorkflowContext instance
        :param node: a Node instance (rest client response model)
        """
        self.ctx = ctx
        self._node = node
        self._relationships = {
            relationship['target_id']: CloudifyWorkflowRelationship(
                self.ctx, self, relationship)
            for relationship in node.relationships}
        self._node_instances = {}

    @property
    def id(self):
        """The node id"""
        return self._node.id

    @property
    def type(self):
        """The node type"""
        return self._node.type

    @property
    def type_hierarchy(self):
        """The node type hierarchy"""
        return self._node.type_hierarchy

    @property
    def properties(self):
        """The node properties"""
        return self._node.properties

    @property
    def plugins_to_install(self):
        """
        The plugins to install in this node. (Only relevant for host nodes)
        """
        return self._node.get('plugins_to_install', [])

    @property
    def relationships(self):
        """The node relationships"""
        return self._relationships.itervalues()

    @property
    def operations(self):
        """The node operations"""
        return self._node.operations

    @property
    def instances(self):
        """The node instances"""
        return self._node_instances.itervalues()

    def get_relationship(self, target_id):
        """Get a node relationship by its target id"""
        return self._relationships.get(target_id)


class CloudifyWorkflowContext(object):
    """A context used in workflow operations"""

    def __init__(self, ctx):
        """
        :param ctx: a cloudify_context workflow dict
        """
        self._context = ctx

        rest = get_rest_client()
        rest_nodes = rest.nodes.list(self.deployment_id)
        rest_node_instances = rest.node_instances.list(self.deployment_id)

        self._nodes = {node.id: CloudifyWorkflowNode(self, node) for
                       node in rest_nodes}
        self._node_instances = {
            instance.id: CloudifyWorkflowNodeInstance(
                self, self._nodes[instance.node_id], instance)
            for instance in rest_node_instances}

        self._logger = None

        self._internal = CloudifyWorkflowContextInternal(self)

    def graph_mode(self):
        """
        Switch the workflow context into graph mode
        :return: A task dependency graph instance
        """
        if next(self.internal.task_graph.tasks_iter(), None) is not None:
            raise RuntimeError('Cannot switch to graph mode when tasks have'
                               'already been executed')

        self.internal.graph_mode = True
        return self.internal.task_graph

    @property
    def internal(self):
        return self._internal

    @property
    def nodes(self):
        """The plan node instances"""
        return self._nodes.itervalues()

    @property
    def deployment_id(self):
        """The deployment id"""
        return self._context.get('deployment_id')

    @property
    def blueprint_id(self):
        """The blueprint id"""
        return self._context.get('blueprint_id')

    @property
    def execution_id(self):
        """The execution id"""
        return self._context.get('execution_id')

    @property
    def workflow_id(self):
        """The workflow id"""
        return self._context.get('workflow_id')

    @property
    def logger(self):
        """A logger for this workflow"""
        if self._logger is None:
            self._logger = self._init_cloudify_logger()
        return self._logger

    def _init_cloudify_logger(self):
        logger_name = self.workflow_id if self.workflow_id is not None \
            else 'cloudify_workflow'
        handler = CloudifyWorkflowLoggingHandler(self)
        return init_cloudify_logger(handler, logger_name)

    def send_event(self, event, event_type='workflow_stage',
                   args=None,
                   additional_context=None):
        """
        Sends a workflow event to RabbitMQ

        :param event: The event
        :param event_type: The event type
        :param args: additional arguments that may be added to the message
        :param additional_context: additional context to be added to the
               context
        """

        def send_event_task():
            send_workflow_event(ctx=self,
                                event_type=event_type,
                                message=event,
                                args=args,
                                additional_context=additional_context)
        return self.local_task(
            local_task=send_event_task,
            info=event)

    def get_node(self, node_id):
        """
        Get a node by its id

        :param node_id: The node id
        :return: a CloudifyWorkflowNode instance for the node or None if
                 not found
        """
        return self._nodes.get(node_id)

    def get_node_instance(self, node_instance_id):
        """
        Get a node by its id

        :param node_instance_id: The node instance id
        :return: a CloudifyWorkflowNode instance for the node or None if
                 not found
        """
        return self._node_instances.get(node_instance_id)

    def _execute_operation(self,
                           operation,
                           node_instance,
                           operations,
                           related_node_instance=None,
                           kwargs=None):
        kwargs = kwargs or {}
        node = node_instance.node
        rest_node = node._node
        rest_node_instance = node_instance._node_instance
        op_struct = operations.get(operation)
        if op_struct is None:
            return NOPLocalWorkflowTask()
        plugin_name = op_struct['plugin']
        operation_mapping = op_struct['operation']
        operation_properties = op_struct.get('properties', node.properties)
        task_queue = 'cloudify.management'
        if rest_node.plugins[plugin_name]['agent_plugin'] == 'true':
            task_queue = rest_node_instance.host_id
        elif rest_node.plugins[plugin_name]['manager_plugin'] == 'true':
            task_queue = self.deployment_id
        task_name = '{0}.{1}'.format(plugin_name, operation_mapping)

        node_context = {
            'node_id': node_instance.id,
            'node_name': node_instance.node_id,
            'node_properties': copy.copy(operation_properties),
            'plugin': plugin_name,
            'operation': operation,
            'relationships': [rel.target_id
                              for rel in node_instance.relationships]
        }
        if related_node_instance is not None:
            node_context['related'] = {
                'node_id': related_node_instance.id,
                'node_properties': copy.copy(
                    related_node_instance.node.properties)
            }

        return self.execute_task(task_name,
                                 task_queue=task_queue,
                                 kwargs=kwargs,
                                 node_context=node_context)

    def update_execution_status(self, new_status):
        """
        Updates the execution status to new_status.
        Note that the workflow status gets automatically updated before and
        after its run (whether the run succeeded or failed)
        """
        def update_execution_status_task():
            update_execution_status(self.execution_id, new_status)
        return self.local_task(
            local_task=update_execution_status_task,
            info=new_status)

    def _build_cloudify_context(self,
                                task_id,
                                task_queue,
                                task_name,
                                node_context):
        node_context = node_context or {}
        context = {
            '__cloudify_context': '0.3',
            'task_id': task_id,
            'task_name': task_name,
            'task_target': task_queue,
            'blueprint_id': self.blueprint_id,
            'deployment_id': self.deployment_id,
            'execution_id': self.execution_id,
            'workflow_id': self.workflow_id,
        }
        context.update(node_context)
        return context

    def execute_task(self,
                     task_name,
                     task_queue=None,
                     kwargs=None,
                     node_context=None):
        """
        Execute a task

        :param task_name: the task named
        :param task_queue: the task queue, if None runs the task locally
        :param kwargs: optional kwargs to be passed to the task
        :param node_context: Used internally by node.execute_operation
        """
        kwargs = kwargs or {}
        task_id = str(uuid.uuid4())
        cloudify_context = self._build_cloudify_context(
            task_id,
            task_queue,
            task_name,
            node_context)
        kwargs['__cloudify_context'] = cloudify_context

        if task_queue is None:
            # Local task
            values = task_name.split('.')
            module_name = '.'.join(values[:-1])
            method_name = values[-1]
            module = importlib.import_module(module_name)
            task = getattr(module, method_name)
            return self.local_task(local_task=task,
                                   info=task_name,
                                   kwargs=kwargs,
                                   task_id=task_id)
        else:
            # Remote task
            task = celery.subtask(task_name,
                                  kwargs=kwargs,
                                  queue=task_queue,
                                  immutable=True)
            return self.remote_task(task=task,
                                    cloudify_context=cloudify_context,
                                    task_id=task_id)

    def local_task(self,
                   local_task,
                   node=None,
                   info=None,
                   kwargs=None,
                   task_id=None):
        return self._process_task(
            LocalWorkflowTask(local_task=local_task,
                              workflow_context=self,
                              node=node,
                              info=info,
                              kwargs=kwargs,
                              task_id=task_id,
                              **self.internal.get_task_configuration()))

    def remote_task(self,
                    task,
                    cloudify_context,
                    task_id):
        return self._process_task(
            RemoteWorkflowTask(task=task,
                               cloudify_context=cloudify_context,
                               task_id=task_id,
                               workflow_context=self,
                               **self.internal.get_task_configuration()))

    def _process_task(self, task):
        if self.internal.graph_mode:
            return task
        else:
            self.internal.task_graph.add_task(task)
            return task.apply_async()


class CloudifyWorkflowContextInternal(object):

    def __init__(self, workflow_context):
        self._bootstrap_context = None
        self._graph_mode = False
        # the graph is always created internally for events to work properly
        # when graph mode is turned on this instance is returned to the user.
        self._task_graph = TaskDependencyGraph(workflow_context)

    def get_task_configuration(self):
        bootstrap_context = self._get_bootstrap_context()
        workflows = bootstrap_context.get('workflows', {})
        total_retries = workflows.get('task_retries', DEFAULT_TOTAL_RETRIES)
        retry_interval = workflows.get('task_retry_interval',
                                       DEFAULT_RETRY_INTERVAL)
        return dict(total_retries=total_retries,
                    retry_interval=retry_interval)

    def _get_bootstrap_context(self):
        if self._bootstrap_context is None:
            self._bootstrap_context = get_bootstrap_context()
        return self._bootstrap_context

    @property
    def task_graph(self):
        return self._task_graph

    @property
    def graph_mode(self):
        return self._graph_mode

    @graph_mode.setter
    def graph_mode(self, graph_mode):
        self._graph_mode = graph_mode
