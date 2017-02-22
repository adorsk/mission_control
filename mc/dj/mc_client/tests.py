import json
import unittest
from unittest.mock import call, DEFAULT, Mock, patch

from . import mission_control_client


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.base_url = '/base/url/'
        self.patchers = {}
        self.decorate_patchers()
        self.mocks = {key: patcher.start()
                      for key, patcher in self.patchers.items()}
        self.mc_client = mission_control_client.MissionControlClient(
            base_url=self.base_url)

    def decorate_patchers(self):
        self.patchers['requests'] = patch.object(mission_control_client,
                                                 'requests')

    def tearDown(self):
        for patcher in self.patchers.values(): patcher.stop()

class FetchFlowsTestCase(BaseTestCase):
    def test_makes_get(self):
        self.mc_client.fetch_flows()
        expected_url = self.base_url + 'flows/'
        expected_get_call = call(expected_url)
        self.assertEqual(self.mocks['requests'].get.call_args,
                         expected_get_call)

    def test_query_params(self):
        query_params = {'filter1': 'junk'}
        self.mc_client.fetch_flows(query_params=query_params)
        expected_url = self.base_url + 'flows/'
        self.assertEqual(self.mocks['requests'].get.call_args,
                         call(expected_url, query_params))

    def test_handles_populated_response(self):
        flows = [{'uuid': i} for i in range(3)]
        self.mocks['requests'].get.return_value.json.return_value = flows
        fetched_flows = self.mc_client.fetch_flows()
        self.assertEqual(fetched_flows, flows)

    def test_handles_empty_response(self):
        flows = []
        self.mocks['requests'].get.return_value.json.return_value = flows
        fetched_flows = self.mc_client.fetch_flows()
        self.assertEqual(fetched_flows, flows)


class FetchFlowByUUIDTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mc_client.fetch_flows = Mock(return_value=[Mock()])

    def test_wraps_fetch_flows(self):
        uuid = 'some uuid'
        result = self.mc_client.fetch_flow_by_uuid(uuid=uuid)
        self.assertEqual(self.mc_client.fetch_flows.call_args,
                         call(query_params={'uuid': uuid}))
        self.assertEqual(result, self.mc_client.fetch_flows.return_value[0])

class FetchTickableFlowsTestCase(BaseTestCase):
    def test_fetch_tickable_flow_records(self):
        self.mc_client.fetch_flows = Mock()
        self.mc_client.fetch_tickable_flows()
        self.assertEqual(
            self.mc_client.fetch_flows.call_args, 
            call(query_params={'claimed': False, 'tickable': True}))

class ClaimFlowsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.uuids = [i for i in range(3)]

    def test_makes_post(self):
        self.mc_client.claim_flows(uuids=self.uuids)
        expected_url = self.base_url + 'claim_flows/'
        expected_post_call = call(expected_url, json={'uuids': self.uuids})
        self.assertEqual(self.mocks['requests'].post.call_args,
                         expected_post_call)

    def test_handles_populated_response(self):
        self.mocks['requests'].post.return_value.json.return_value = {
            _uuid: True for _uuid in self.uuids
        }
        result = self.mc_client.claim_flows(uuids=self.uuids)
        expected_result = {_uuid: True for _uuid in self.uuids}
        self.assertEqual(result, expected_result)

    def test_handles_empty_response(self):
        self.mocks['requests'].post.return_value.json.return_value = {}
        result = self.mc_client.claim_flows(uuids=self.uuids)
        expected_result = {}
        self.assertEqual(result, expected_result)

class UpdateFlowsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.updates_by_uuid = {
            'uuid_%s' % i: {'key1': 'value1', 'key2': 'value2'}
            for i in range(3)
        }

    def test_makes_patch_calls(self):
        self.mc_client.update_flows(updates_by_uuid=self.updates_by_uuid)
        expected_patch_calls = [
            call(self.base_url + 'flows/' + _uuid + '/', json=updates_for_uuid)
            for _uuid, updates_for_uuid in self.updates_by_uuid.items()
        ]
        self.assertEqual(
            sorted(self.mocks['requests'].patch.call_args_list,
                   key=lambda _call_as_pair: _call_as_pair[0][0]),
            sorted(expected_patch_calls,
                   key=lambda _call_as_triple: _call_as_triple[1][0]))

    def test_returns_combined_patch_results(self):
        self.mocks['requests'].patch.return_value.json.return_value = {}
        result = self.mc_client.update_flows(
            updates_by_uuid=self.updates_by_uuid)
        expected_result = {_uuid: {} for _uuid in  self.updates_by_uuid}
        self.assertEqual(result, expected_result)

class CreateFlowTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.flow = {'data': 'some data'}
        self.mocks['requests'].post.return_value.status_code = 200

    def test_makes_post_call(self):
        self.mc_client.create_flow(flow=self.flow)
        self.assertEqual(self.mocks['requests'].post.call_args,
                         call(self.base_url + 'flows/', json=self.flow))

    def test_returns_post_result(self):
        mock_result = {'some': 'result'}
        self.mocks['requests'].post.return_value.json.return_value = \
                mock_result
        result = self.mc_client.create_flow(flow=self.flow)
        self.assertEqual(result, mock_result)


class FetchJobsTestCase(BaseTestCase):
    def test_makes_get(self):
        self.mc_client.fetch_jobs()
        expected_url = self.base_url + 'jobs/'
        expected_get_call = call(expected_url)
        self.assertEqual(self.mocks['requests'].get.call_args,
                         expected_get_call)

    def test_query_params(self):
        query_params = {'filter1': 'junk'}
        self.mc_client.fetch_jobs(query_params=query_params)
        expected_url = self.base_url + 'jobs/'
        self.assertEqual(self.mocks['requests'].get.call_args,
                         call(expected_url, query_params))

    def test_handles_populated_response(self):
        jobs = [{'uuid': i} for i in range(3)]
        self.mocks['requests'].get.return_value.json.return_value = jobs
        fetched_jobs = self.mc_client.fetch_jobs()
        self.assertEqual(fetched_jobs, jobs)

    def test_handles_empty_response(self):
        jobs = []
        self.mocks['requests'].get.return_value.json.return_value = jobs
        fetched_jobs = self.mc_client.fetch_jobs()
        self.assertEqual(fetched_jobs, jobs)

class FetchClaimableJobsTest(BaseTestCase):
    def test_calls_fetch_jobs_with_query_params(self):
        with patch.multiple(self.mc_client, fetch_jobs=DEFAULT):
            self.mc_client.fetch_claimable_jobs()
            self.assertEqual(
                self.mc_client.fetch_jobs.call_args,
                call(query_params={'status': 'PENDING'}))

class FetchJobByUUIDTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mc_client.fetch_jobs = Mock(return_value=[Mock()])

    def test_wraps_fetch_jobs(self):
        uuid = 'some uuid'
        result = self.mc_client.fetch_job_by_uuid(uuid=uuid)
        self.assertEqual(self.mc_client.fetch_jobs.call_args,
                         call(query_params={'uuid': uuid}))
        self.assertEqual(result, self.mc_client.fetch_jobs.return_value[0])

class ClaimJobsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.uuids = [i for i in range(3)]

    def test_makes_post(self):
        self.mc_client.claim_jobs(uuids=self.uuids)
        expected_url = self.base_url + 'claim_jobs/'
        expected_post_call = call(expected_url, json={'uuids': self.uuids})
        self.assertEqual(self.mocks['requests'].post.call_args,
                         expected_post_call)

    def test_handles_populated_response(self):
        self.mocks['requests'].post.return_value.json.return_value = {
            _uuid: True for _uuid in self.uuids
        }
        result = self.mc_client.claim_jobs(uuids=self.uuids)
        expected_result = {_uuid: True for _uuid in self.uuids}
        self.assertEqual(result, expected_result)

    def test_handles_empty_response(self):
        self.mocks['requests'].post.return_value.json.return_value = {}
        result = self.mc_client.claim_jobs(uuids=self.uuids)
        expected_result = {}
        self.assertEqual(result, expected_result)

class UpdateJobsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.updates_by_uuid = {
            'uuid_%s' % i: {'key1': 'value1', 'key2': 'value2'}
            for i in range(3)
        }

    def test_makes_patch_calls(self):
        self.mc_client.update_jobs(updates_by_uuid=self.updates_by_uuid)
        expected_patch_calls = [
            call(self.base_url + 'jobs/' + _uuid + '/',
                 json=self.mc_client.format_job_kwargs(updates_for_uuid))
            for _uuid, updates_for_uuid in self.updates_by_uuid.items()
        ]
        self.assertEqual(
            sorted(self.mocks['requests'].patch.call_args_list,
                   key=lambda _call_as_pair: _call_as_pair[0][0]),
            sorted(expected_patch_calls,
                   key=lambda _call_as_triple: _call_as_triple[1][0]))

    def test_returns_combined_patch_results(self):
        self.mocks['requests'].patch.return_value.json.return_value = {}
        result = self.mc_client.update_jobs(
            updates_by_uuid=self.updates_by_uuid)
        expected_result = {_uuid: {} for _uuid in  self.updates_by_uuid}
        self.assertEqual(result, expected_result)

class CreateJobTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.job_kwargs = {'data': 'some data'}
        self.mocks['requests'].post.return_value.status_code = 200

    def test_makes_post_call(self):
        self.mc_client.create_job(job_kwargs=self.job_kwargs)
        self.assertEqual(
            self.mocks['requests'].post.call_args,
            call(self.base_url + 'jobs/', json={
                **self.job_kwargs,
                'data': json.dumps(self.job_kwargs['data']),
            })
        )

    def test_returns_post_result(self):
        mock_result = {'some': 'result'}
        self.mocks['requests'].post.return_value.json.return_value = \
                mock_result
        result = self.mc_client.create_job(job_kwargs=self.job_kwargs)
        self.assertEqual(result, mock_result)

class FlushTestCase(BaseTestCase):
    def test_gets_flush_endpoint(self):
        result = self.mc_client.flush_mc_db()
        expected_url = self.base_url + 'flush/'
        self.assertEqual(self.mocks['requests'].get.call_args,
                         call(expected_url))
        self.assertEqual(
            result,
            self.mocks['requests'].get.return_value.json.return_value)

if __name__ == '__main__':
    unittest.main()

