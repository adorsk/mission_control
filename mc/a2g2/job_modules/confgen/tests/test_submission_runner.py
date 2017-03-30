import os
import unittest
from unittest.mock import call, MagicMock, patch

from .. import submission_runner


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.submission = MagicMock()
        self.submission_runner = submission_runner.SubmissionRunner(
            submission=self.submission)

class RunSubmissionTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.submission_runner.create_workdir = MagicMock()
        self.submission_runner.run_workdir = MagicMock()
        self.submission_runner.move_workdir_to_outputs = MagicMock()
        self.expected_workdir_meta = \
                self.submission_runner.create_workdir.return_value
        self.submission_runner.run_submission()

    def test_creates_workdir(self):
        self.assertEqual(self.submission_runner.create_workdir.call_args,
                         call())

    def test_runs_workdir(self):
        self.assertEqual(self.submission_runner.run_workdir.call_args,
                         call(workdir_meta=self.expected_workdir_meta))

    def test_moves_workdir_to_outputs(self):
        self.assertEqual(
            self.submission_runner.move_workdir_to_outputs.call_args,
            call(workdir_meta=self.expected_workdir_meta))

class CreateWorkdirTestCase(BaseTestCase):
    @patch.object(submission_runner, 'WorkdirBuilder')
    def test_dispatches_to_build_workdir(self, MockWorkdirBuilder):
        workdir_meta = self.submission_runner.create_workdir()
        self.assertEqual(
            workdir_meta,
            MockWorkdirBuilder.return_value.build_workdir.return_value)

class RunWorkdirTestCase(BaseTestCase):
    @patch.object(submission_runner, 'os')
    @patch.object(submission_runner, 'subprocess')
    def test_runs_workdir_entrypoint(self, mock_subprocess, mock_os):
        workdir_meta = MagicMock()
        self.submission_runner.run_workdir(workdir_meta=workdir_meta)
        expected_cmd = ['bash', workdir_meta['entrypoint']]
        expected_env = {
            **mock_os.environ,
            'CONFGEN_EXE': self.submission_runner.submission.get(
                'context', {}).get('CONFGEN_EXE')
        }
        self.assertEqual(mock_subprocess.run.call_args,
                         call(expected_cmd, check=True, env=expected_env))

class MoveWorkdirToOutputsTestCase(BaseTestCase):
    @patch.object(submission_runner, 'shutil')
    def test_moves_workdir_to_outputs(self, mock_shutil):
        workdir_meta = MagicMock()
        expected_src = workdir_meta['dir']
        expected_dest = os.path.join(self.submission['outputs']['dir'],
                                     'confgen')
        self.submission_runner.move_workdir_to_outputs(
            workdir_meta=workdir_meta)
        self.assertEqual(mock_shutil.move.call_args,
                         call(expected_src, expected_dest))
