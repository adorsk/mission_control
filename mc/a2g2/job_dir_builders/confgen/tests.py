import json
import textwrap
import unittest
from unittest.mock import MagicMock

from .confgen import ConfgenJobDirBuilder


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.job = {
            'job_spec': {
                'confgen': {
                    'smiles': 'some smiles'
                }
            }
        }

class TestBuildOdysseyDir(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_passes_expected_dir_spec(self):
        mock_odyssey_builder = MagicMock()
        mock_output_dir = MagicMock()
        ConfgenJobDirBuilder.build_odyssey_dir(
            job=self.job, odyssey_dir_builder=mock_odyssey_builder,
            output_dir=mock_output_dir)
        expected_dir_spec = {
            'job_script_body': textwrap.dedent(
                '''
                set -o errexit
                echo "starting, $(date)"
                source {conda_env_root}/bin/activate {conda_env_root}
                SCRATCH_DIR="/scratch/conformers.$$"
                mkdir -p $SCRATCH_DIR
                python -m {confgen_module} \\
                    --params_file="./confgen.params.json" \\
                    --output_dir="$SCRATCH_DIR"
                cp -r $SCRATCH_DIR ./conformers
                echo "finished, $(date)"
                ''').format(
                    conda_env_root='/n/aagfs01/software/conda_envs/a2g2_env',
                    confgen_module=('a2g2.a2g2_utils.conformer_generators'
                                    '.rdkit_conformer_generator.cmd')
                ),
            'templates': {
                'specs': [
                    {'target': 'confgen.params.json',
                     'content': json.dumps({
                         'smiles': self.job['job_spec']['confgen']['smiles']
                     }, indent=2)}
                ]
            }
        }
        call_kwargs = mock_odyssey_builder.build_dir.call_args[1]
        self.assertEqual(call_kwargs['output_dir'], mock_output_dir)
        for k, v in expected_dir_spec.items():
            self.assertEqual(call_kwargs['dir_spec'][k], v) 