class JobRecordClient(object):
    def __init__(self, mc_dao=None, queue_key=None, use_locks=False):
        """
        Args:
            mc_dao (mc_dao): mc_dao.
            queue_key (str): key for the job queue to use.
            use_locks (bool): if True, create a lock record when creating.
                a job_record. This can be used to add a lock reference to parent
                flows that create jobs.
        """
        self.mc_dao = mc_dao
        self.queue_key = queue_key
        self.use_locks = use_locks

    def create_job_record(self, *args, job_kwargs=None, **kwargs):
        """
        Args:
            job_kwargs (dict): a dictionary of job parameters.

        Returns:
            job_meta (dict): a dictionary of metadata that can be passed to
                get_job_record to retrieve a job.
        """
        job_kwargs = {**(job_kwargs or {}), 'status': 'PENDING'}
        job_record = self.mc_dao.create_item(item_type='Job', kwargs=job_kwargs)
        if self.use_locks:
            parent_key = job_kwargs.get('data', {}).get('parent_key')
            if parent_key:
                self.mc_dao.create_lock(lockee_key=parent_key,
                                        locker_key=job_record['key'])
        job_meta = {'key': job_record['key']}
        return job_meta

    def get_job_record(self, job_meta=None):
        """
        Args:
            job_meta (dict): dictionary of metadata, as per create_job_record.

        Returns:
            job_record (dict): a job_record.
        """
        return self.mc_dao.get_item_by_key(item_type='Job', key=job_meta['key'])

    def claim_job_records(self, *args, **kwargs):
        """
        Returns:
            job_records (dict): a list of job_records.
        """
        return self.mc_dao.claim_queue_items(queue_key=self.queue_key)['items']
    
    def patch_job_records(self, keyed_patches=None):
        """
        Args:
            keyed_patches (dict): a dict in which keys are job_record keys, and
                values are dicts of job_record kwargs.
        Returns:
            job_records (dict): the patched items
        """
        patched = self.mc_dao.patch_items(item_type='Job',
                                          keyed_patches=keyed_patches)
        if self.use_locks:
            locker_keys = [job_key for job_key, patches in keyed_patches.items()
                           if patches.get('status') in {'FAILED', 'COMPLETED'}]
            if locker_keys: self.mc_dao.release_locks(locker_keys=locker_keys)
        return patched
