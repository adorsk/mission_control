import unittest
from unittest.mock import call, MagicMock, patch

from .. import utils


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.cfg = MagicMock()
        self.houston = MagicMock()
        self.houston.cfg = self.cfg
        self.utils = utils.HoustonUtils(houston=self.houston)

    def mockify_utils_attrs(self, attrs=None):
        for attr in attrs:
            setattr(self.utils, attr, MagicMock())

    def mockify_module_attrs(self, attrs=None, module=utils):
        if not hasattr(self, 'modmocks'):
            self.modmocks = {}
        for attr in attrs:
            patcher = patch.object(module, attr)
            self.addCleanup(patcher.stop)
            self.modmocks[attr] = patcher.start()


class DbTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mockify_module_attrs(attrs=['Db'])
        self.result = self.utils.db

    def test_constructs_db(self):
        self.assertEqual(self.modmocks['Db'].call_args,
                         call(db_uri=self.cfg['MC_DB_URI'], schema=None))

    def test_returns_db(self):
        self.assertEqual(self.result,
                         self.modmocks['Db'].return_value)

    def test_memoizes(self):
        self.assertTrue(self.utils.db is self.result)


class EnsureQueuesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mockify_utils_attrs(attrs=['ensure_queue'])
        self.utils.ensure_queues()

    def test_dispatches_to_submethods(self):
        self.assertEqual(self.utils.ensure_queue.call_args,
                         call(queue_cfg=self.utils.cfg['FLOW_QUEUE']))
        self.assertEqual(self.utils.ensure_queue.call_args,
                         call(queue_cfg=self.utils.cfg['JOB_QUEUE']))


class EnsureQueueTestCase(BaseTestCase):
    def setUp(self):
        self.skipTest('FIX LATER!')
        super().setUp()
        self.mockify_utils_attrs(attrs=['db'])
        self.queue_cfg = MagicMock()

    def _ensure_queue(self):
        self.utils.ensure_queue(queue_cfg=self.queue_cfg)

    def test_returns_if_queue_was_found(self):
        self._ensure_queue()

    def test_creates_queue_if_not_found(self):
        self.utils.db.ItemNotFoundError = Exception
        self.utils.db.get_item_by_key.side_effect = (
            self.utils.db.ItemNotFoundError)
        self._ensure_queue()
        self.assertEqual(
            self.utils.db.create_item.call_args,
            call(item_type='queue',
                 item_kwargs={'key': self.queue_cfg['key'],
                              **self.queue_cfg.get('queue_kwargs', {})})
        )


class FlowRunnerTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mockify_utils_attrs(attrs=['flow_engine', 'flow_record_client',
                                        'job_record_client'])
        self.mockify_module_attrs(attrs=['FlowRunner'])
        self.result = self.utils.flow_runner

    def test_constructs_and_returns_flow_runner(self):
        self.assertEqual(
            self.modmocks['FlowRunner'].call_args,
            call(
                flow_engine=self.utils.flow_engine,
                flow_record_client=self.utils.flow_record_client,
                task_ctx={
                    'mc.flow_record_client': self.utils.flow_record_client,
                    'mc.job_record_client': self.utils.job_record_client,
                }
            )
        )
        self.assertEqual(self.result, self.modmocks['FlowRunner'].return_value)

    def test_memoizes(self):
        self.assertTrue(self.utils.flow_runner is self.result)


class FlowEngineTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mockify_module_attrs(attrs=['FlowEngine'])
        self.result = self.utils.flow_engine

    def test_constructs_and_returns_flow_engine(self):
        self.assertEqual(self.modmocks['FlowEngine'].call_args, call())
        self.assertEqual(self.result, self.modmocks['FlowEngine'].return_value)

    def test_memoizes(self):
        self.assertTrue(self.utils.flow_engine is self.result)


class FlowRecordClientTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mockify_utils_attrs(attrs=['db'])
        self.mockify_module_attrs(attrs=['FlowRecordClient'])
        self.result = self.utils.flow_record_client

    def test_constructs_and_returns_flow_record_client(self):
        self.assertEqual(
            self.modmocks['FlowRecordClient'].call_args,
            call(mc_db=self.utils.db,
                 use_locks=self.utils.cfg.get('USE_LOCKS', True),
                 queue_key=self.utils.cfg['FLOW_QUEUE']['key'])
        )
        self.assertEqual(self.result,
                         self.modmocks['FlowRecordClient'].return_value)

    def test_memoizes(self):
        self.assertTrue(self.utils.flow_record_client is self.result)


class JobRecordClientTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mockify_utils_attrs(attrs=['db'])
        self.mockify_module_attrs(attrs=['JobRecordClient'])
        self.result = self.utils.job_record_client

    def test_constructs_and_returns_job_record_client(self):
        self.assertEqual(
            self.modmocks['JobRecordClient'].call_args,
            call(
                mc_db=self.utils.db,
                use_locks=self.utils.cfg.get('USE_LOCKS', True),
                queue_key=self.utils.cfg['JOB_QUEUE']['key']
            )
        )
        self.assertEqual(self.result,
                         self.modmocks['JobRecordClient'].return_value)

    def test_memoizes(self):
        self.assertTrue(self.utils.job_record_client is self.result)


class JobRunnerTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mockify_utils_attrs(attrs=['job_record_client', 'jobman',
                                        'jobdir_factory'])
        self.mockify_module_attrs(attrs=['JobRunner'])
        self.result = self.utils.job_runner

    def test_constructs_and_returns_job_runner(self):
        self.assertEqual(
            self.modmocks['JobRunner'].call_args,
            call(
                artifact_handler=self.utils.cfg['ARTIFACT_HANDLER'],
                job_record_client=self.utils.job_record_client,
                jobman=self.utils.jobman,
                jobdirs_dir=self.utils.cfg.get('JOBDIRS_DIR', None),
                build_jobdir_fn=self.utils.build_jobdir
            )
        )
        self.assertEqual(self.result, self.modmocks['JobRunner'].return_value)

    def test_memoizes(self):
        self.assertTrue(self.utils.job_runner is self.result)


class JobManTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mockify_module_attrs(attrs=['JobMan'])
        self.result = self.utils.jobman

    def test_constructs_and_returns_jobman(self):
        self.assertEqual(
            self.modmocks['JobMan'].from_cfg.call_args,
            call(cfg=(self.cfg['JOBMAN_CFG']))
        )
        self.assertEqual(self.result,
                         self.modmocks['JobMan'].from_cfg.return_value)

    def test_memoizes(self):
        self.assertTrue(self.utils.jobman is self.result)


class BuildJobdirTestCase(BaseTestCase):
    def setUp(self):
        self.skipTest("RETURN TO THIS LATER!")
        super().setUp()
        self.mockify_module_attrs(attrs=['JobModuleCommandDispatcher'])
        self.args = [MagicMock() for i in range(3)]
        self.kwargs = {'kwarg_%s' % i: MagicMock() for i in range(3)}
        self.result = self.utils.build_jobdir(*self.args, **self.kwargs)

    def test_dispatches_to_job_module_command_dispatcher(self):
        self.assertEqual(self.modmocks['JobModuleCommandDispatcher'].call_args,
                         call())
        self.assertEqual(
            (self.modmocks['JobModuleCommandDispatcher'].return_value
             .build_jobdir.call_args),
            call(*self.args, **self.kwargs)
        )
        self.assertEqual(
            self.result,
            (self.modmocks['JobModuleCommandDispatcher'].return_value
             .build_jobdir.return_value)
        )
