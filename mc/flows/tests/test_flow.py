from collections import defaultdict
import unittest
from unittest.mock import call, Mock, MagicMock
from uuid import uuid4

from ..flow import Flow


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.flow = Flow()

    def generate_tasks(self, n=3):
        tasks = []
        for i in range(n):
            tasks.append(self.generate_task(key=i))
        return tasks

    def generate_task(self, key=None, **kwargs):
        if key is None: key = str(uuid4())
        task = {'key': key, **kwargs}
        return task

    def _task_list_to_dict(self, task_list):
        return {task['key']: task for task in task_list}

class AddTaskTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.task = self.generate_task(key='task')

    def test_adds_task(self):
        self.assertFalse(self.task['key'] in self.flow.tasks)
        self.flow.add_task(task=self.task)
        self.assertEqual(self.flow.tasks[self.task['key']], self.task)

    def test_returns_task(self):
        result = self.flow.add_task(task=self.task)
        self.assertEqual(result, self.task)

    def test_generates_key_if_unset(self):
        self.flow.generate_key = Mock()
        del self.task['key']
        self.flow.add_task(task=self.task)
        self.assertEqual(self.task['key'],
                         self.flow.generate_key.return_value)

    def test_adds_edges_for_precursors(self):
        precursors = [self.flow.add_task(task=self.generate_task(key=i))
                      for i in range(1)]
        self.task['precursors'] = [precursor['key'] for precursor in precursors]
        self.flow.add_task(task=self.task)
        for precursor in precursors:
            self.assertTrue(self.flow.has_edge(src_key=precursor['key'],
                                               dest_key=self.task['key']))

    def test_adds_edges_for_successor(self):
        successors = [self.flow.add_task(task=self.generate_task(key=i))
                      for i in range(3)]
        self.task['successors'] = [successor['key'] for successor in successors]
        self.flow.add_task(task=self.task)
        for successor in successors:
            self.assertTrue(self.flow.has_edge(src_key=self.task['key'],
                                               dest_key=successor['key']))

class AddEdgeTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.tasks = [
            self.flow.add_task(task=task, add_default_connections=False)
            for task in self.generate_tasks(n=2)
        ]
        self.edge = {'src_key': self.tasks[0]['key'],
                     'dest_key': self.tasks[1]['key']}
        self.expected_edge_key = (self.edge['src_key'], self.edge['dest_key'])

    def test_add_edge(self):
        self.assertFalse(self.expected_edge_key in self.flow._edges)
        self.flow.add_edge(edge=self.edge)
        self.assertEqual(self.flow._edges[self.expected_edge_key], self.edge)

    def test_updates_edges_by_key(self):
        self.assertTrue(self.tasks[0]['key'] not in self.flow._edges_by_key)
        self.assertTrue(self.tasks[1]['key'] not in self.flow._edges_by_key)
        self.flow.add_edge(edge=self.edge)
        self.assertEqual(
            self.flow._edges_by_key[self.edge['src_key']]['outgoing'],
            {self.expected_edge_key: self.edge})
        self.assertEqual(
            self.flow._edges_by_key[self.edge['dest_key']]['incoming'],
            {self.expected_edge_key: self.edge})

class FromFlowSpecTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.flow_spec = {
            'key':'my_key',
            'data': 'some data',
            'status': 'status',
            'tasks': [{'key': 'task_%s' % i} for i in range(3)]
        }
        self.result = Flow.from_flow_spec(flow_spec=self.flow_spec)

    def test_has_expected_key(self):
        self.assertEqual(self.result.key, self.flow_spec['key'])

    def test_has_expected_data(self):
        self.assertEqual(self.result.data, self.flow_spec['data'])

    def test_has_expected_status(self):
        self.assertEqual(self.result.status, self.flow_spec['status'])

    def test_has_expected_tasks(self):
        expected_tasks = {task['key']: task for task in self.flow_spec['tasks']}
        self.assertEqual(
            set(self.result.tasks.keys()),
            (set(expected_tasks.keys()) | {self.flow.ROOT_TASK_KEY})
        )

    def test_has_expected_edges(self):
        expected_key_sequence = (
            [Flow.ROOT_TASK_KEY] 
            + [task['key'] for task in self.flow_spec['tasks']]
        )
        expected_edges = {}
        for i in range(len(expected_key_sequence) - 1):
            src_key = expected_key_sequence[i]
            dest_key = expected_key_sequence[i+1]
            edge_key = (src_key, dest_key)
            edge = {'src_key': src_key, 'dest_key': dest_key}
            expected_edges[edge_key] = edge
        self.assertEqual(self.result._edges, expected_edges)

class FromFlowDictTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.flow_dict = {
            'key':'my_key',
            'data': 'some data',
            'graph': {
                'tasks': {
                    'a': {'key': 'a', 'status': 'COMPLETED'},
                    'b': {'key': 'b', 'status': 'COMPLETED'},
                    'c': {'key': 'c', 'status': 'RUNNING'},
                    'd': {'key': 'd', 'status': 'RUNNING'},
                },
                'edges': [
                    {'src_key': 'ROOT', 'dest_key': 'a'},
                    {'src_key': 'a', 'dest_key': 'b'},
                    {'src_key': 'b', 'dest_key': 'c'},
                    {'src_key': 'b', 'dest_key': 'd'},
                ],
            },
            'status': 'status',
        }
        self.result = Flow.from_flow_dict(flow_dict=self.flow_dict)

    def test_has_expected_key(self):
        self.assertEqual(self.result.key, self.flow_dict['key'])

    def test_has_expected_data(self):
        self.assertEqual(self.result.data, self.flow_dict['data'])

    def test_has_expected_tasks(self):
        expected_tasks = {task['key']: task
                          for task in self.flow_dict['graph']['tasks'].values()}
        self.assertEqual(
            set(self.result.tasks.keys()),
            (set(expected_tasks.keys()) | {self.flow.ROOT_TASK_KEY})
        )

    def test_has_expected_edges(self):
        expected_edges = {}
        for edge in self.flow_dict['graph']['edges']:
            edge_key = (edge['src_key'], edge['dest_key'])
            expected_edges[edge_key] = edge
        self.assertEqual(self.result._edges, expected_edges)

    def test_has_expected_status(self):
        self.assertEqual(self.result.status, self.flow_dict['status'])

class ToFlowDictTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.result = self.flow.to_flow_dict()

    def test_copies_simple_attrs(self):
        actual_values = {attr: self.result.get(attr)
                         for attr in self.flow.SIMPLE_ATTRS}
        expected_values = {attr: getattr(self.flow, attr, None)
                           for attr in self.flow.SIMPLE_ATTRS}
        self.assertEqual(actual_values, expected_values)

    def test_copies_graph(self):
        expected_graph = {
            'tasks': {key: task for key, task in self.flow.tasks.items()},
            'edges': [edge for edge in self.flow._edges.values()],
        }
        self.assertEqual(self.result['graph'], expected_graph)

class GetNearestPendingTasksTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.setup_flow()

    def setup_flow(self):
        self.linear_branches = {
            '1': [
                self.generate_task(key='1.1', status='COMPLETED'),
                self.generate_task(key='1.2', status='PENDING'),
                self.generate_task(key='1.3', status='PENDING')
            ],
            '2': [
                self.generate_task(key='2.1', status='COMPLETED'),
                self.generate_task(key='2.2', status='COMPLETED'),
                self.generate_task(key='2.3', status='PENDING'),
                self.generate_task(key='2.4', status='PENDING'),
            ],
        }
        for branch_tasks in self.linear_branches.values():
            self.add_linear_branch_to_flow(flow=self.flow,
                                           branch_tasks=branch_tasks)

    def add_linear_branch_to_flow(self, flow=None, branch_tasks=None):
        tail = flow.tasks[flow.ROOT_TASK_KEY]
        for task in branch_tasks:
            tail = flow.add_task(task={**task, 'precursors': [tail['key']]})

    def test_get_nearest_tickable_pending_tasks(self):
        expected_nearest_pending_tasks = [self.linear_branches['1'][1],
                                          self.linear_branches['2'][2]]
        def _sans_precursors(tasks): 
            return [{k: v for k, v in task.items() if k is not 'precursors'}
                    for task in tasks]
        self.assertEqual(
            _sans_precursors(self.flow.get_nearest_tickable_pending_tasks()),
            _sans_precursors(expected_nearest_pending_tasks)
        )

class GetSuccessorsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.setup_flow(flow=self.flow)

    def setup_flow(self, flow=None):
        task_1 = self.generate_task(key='1')
        self.flow.add_task(task={**task_1, 'precursors': [flow.ROOT_TASK_KEY]})
        task_1_1 = self.generate_task(key='1_1')
        self.flow.add_task(task={**task_1_1, 'precursors': [task_1['key']]})
        task_1_2 = self.generate_task(key='1_2')
        self.flow.add_task(task={**task_1_2, 'precursors': [task_1['key']]})

    def test_gets_successors(self):
        successors = self.flow.get_successors(task=self.flow.tasks['1'])
        expected_successors = [self.flow.tasks['1_1'], self.flow.tasks['1_2']]
        self.assertEqual(self._task_list_to_dict(successors),
                         self._task_list_to_dict(expected_successors))

class FilterTasksTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_filters(self):
        tasks = defaultdict(list)
        for i in range(4):
            if i % 2: answer = 'yes'
            else: answer = 'no'
            task = self.generate_task(answer=answer)
            tasks[answer].append(task)
            self.flow.add_task(task=task)
        _filter = lambda task: task['answer'] == 'yes'
        result = self.flow.filter_tasks(filters=[_filter])
        expected_result = tasks['yes']
        self.assertEqual(self._task_list_to_dict(result),
                         self._task_list_to_dict(expected_result))

class GetTasksByStatusTestCase(BaseTestCase):
    def test_gets_tasks_by_status(self):
        tasks = defaultdict(list)
        statuses = ['status_%s' % i for i in range(3)]
        for status in statuses:
            for i in range(3):
                task = self.generate_task(status=status)
                tasks[status].append(task)
                self.flow.add_task(task=task)
        for status in statuses:
            result = self.flow.get_tasks_by_status(status=status)
            expected_result = tasks[status]
            self.assertEqual(self._task_list_to_dict(result),
                             self._task_list_to_dict(expected_result))

class HasIncompleteTasksTestCase(BaseTestCase):
    def test_has_incomplete(self):
        self.flow.add_task(task=self.generate_task(status='PENDING'))
        self.assertTrue(self.flow.has_incomplete_tasks())

    def test_does_not_have_incomplete(self):
        self.flow.add_task(task=self.generate_task(status='COMPLETED'))
        self.assertFalse(self.flow.has_incomplete_tasks())

class GetTailTasksTestCase(BaseTestCase):
    def test_gets_tail_tasks(self):
        tail_tasks = [
            self.flow.add_task(task={**self.generate_task(),
                                     'precursors': [self.flow.ROOT_TASK_KEY]})
            for i in range(3)]
        self.assertTrue(self.flow.get_tail_tasks(), tail_tasks)

    def test_handles_flow_with_only_root_task(self):
        self.assertTrue(self.flow.get_tail_tasks(),
                        self.flow.tasks[self.flow.ROOT_TASK_KEY])

class GetRunningTasksTestCase(BaseTestCase):
    def test_dispatches_to_get_tasks_by_status(self):
        self.flow.get_tasks_by_status = MagicMock()
        result = self.flow.get_running_tasks()
        self.assertEqual(self.flow.get_tasks_by_status.call_args,
                         call(status='RUNNING'))
        self.assertEqual(result, self.flow.get_tasks_by_status.return_value)

if __name__ == '__main__':
    unittest.main()
