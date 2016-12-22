import unittest
from unittest.mock import MagicMock

from ..nodes.job_wrapper import JobWrapperNode


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        class TestNode(JobWrapperNode):
            def get_job_input(self):  return {'some': 'input'}
        self.TestNode = TestNode

    def generate_node(self, **node_kwargs):
        return self.TestNode(**node_kwargs)

class InitializationTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.nested_job_state = {
            'status': 'some status',
            'data': {'some': 'data'}
        }
        self.wrapper_node_data = {'_job_node_state': self.nested_job_state}
        self.node = self.generate_node(data=self.wrapper_node_data)

    def test_job_node_has_status_from_state(self):
        self.assertEqual(
            self.node.job_node.status, self.nested_job_state['status'])

    def test_job_node_has_data_from_state_plus_input(self):
        expected_job_node_data = {'input': self.node.get_job_input(),
                                  **self.nested_job_state['data']}
        self.assertEqual(self.node.job_node.data, expected_job_node_data)

class TickTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.node = self.generate_node()
        self.node.job_node = MagicMock()
        self.node.on_job_completed = MagicMock()
        self.node.on_job_failed = MagicMock()

    def test_calls_job_node_tick(self):
        self.node.tick()
        self.assertEqual(self.node.job_node.tick.call_count, 1)

    def test_sets_job_node_state(self):
        self.node.tick()
        expected_job_node_state = {'status': self.node.job_node.status,
                                   'data': self.node.job_node.data}
        self.assertEqual(
            self.node.data['_job_node_state'], expected_job_node_state)

    def test_calls_on_job_completed(self):
        self.node.job_node.status = 'COMPLETED'
        self.node.tick()
        self.assertEqual(self.node.on_job_completed.call_count, 1)

    def test_calls_on_job_failed(self):
        self.node.job_node.status = 'FAILED'
        self.node.tick()
        self.assertEqual(self.node.on_job_failed.call_count, 1)

    def test_propagates_status_otherwise(self):
        self.node.tick()
        self.assertEqual(self.node.status, self.node.job_node.status)

class OnJobCompletedTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.node = self.generate_node()
        self.node.job_node = MagicMock()
        self.node.job_node.data = {'output': 'some output'}
        self.node.on_job_completed()

    def test_copies_job_output_to_node_output(self):
        self.assertEqual(
            self.node.data['output'], self.node.job_node.data['output'])

    def test_sets_status(self):
        self.assertEqual(self.node.status, 'COMPLETED')

class OnJobFailedTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.node = self.generate_node()
        self.node.job_node = MagicMock()
        self.node.job_node.data = {'error': 'some error'}
        self.node.on_job_failed()

    def test_copies_job_error_to_node_error(self):
        self.assertEqual(
            self.node.data['error'], self.node.job_node.data['error'])

    def test_sets_status(self):
        self.assertEqual(self.node.status, 'FAILED')

if __name__ == '__main__':
    unittest.main()
