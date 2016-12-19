import requests
from jobs.models import JobStatuses


class MissionControlJobSpecClient(object):

    Statuses = JobStatuses

    def __init__(self, base_url=None, request_client=None):
        self.base_url = base_url
        self.request_client = request_client or requests

    def fetch_job_specs(self, query_params=None):
        jobs_url = self.base_url + 'jobs/'
        if query_params:
            response = self.request_client.get(jobs_url, query_params)
        else:
            response = self.request_client.get(jobs_url)
        return response.json()

    def fetch_claimable_job_specs(self):
        return self.fetch_job_specs(
            query_params={'status': self.Statuses.Pending.name})

    def claim_job_specs(self, uuids=None):
        claim_jobs_url = self.base_url + 'claim_jobs/'
        response = self.request_client.post(claim_jobs_url, {'uuids': uuids})
        return response.json()

    def update_job_specs(self, updates_by_uuid=None):
        results_by_uuid = {}
        for _uuid, updates_for_uuid in updates_by_uuid.items():
            job_spec_url = self.base_url + 'jobs/' + _uuid + '/'
            response = self.request_client.patch(job_spec_url, updates_for_uuid)
            results_by_uuid[_uuid] = response.json()
        return results_by_uuid