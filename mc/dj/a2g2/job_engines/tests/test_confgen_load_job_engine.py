import os
import tempfile
import unittest
from unittest.mock import call, Mock

import pybel
from rdkit import Chem
from rdkit.Chem import AllChem

from ..confgen_load_job_engine import ConfgenLoadJobEngine


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = ConfgenLoadJobEngine()

class RunJobDirTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_uploads_parse_results(self):
        self.engine.parse_inputs = Mock()
        self.engine.upload_objects = Mock()
        self.engine.execute_job(job_dir=self.job_dir)
        self.assertEqual(
            self.engine.parse_inputs.call_args,
            call(inputs_dir=os.path.join(self.job_dir, 'raw_data'))
        )
        self.assertEqual(self.engine.upload_objects.call_args,
                         call(objects=self.engine.parse_inputs.return_value))

class ParseJobDirTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.mol = self.generate_mol_w_conformers()
        self.job_dir = self.generate_job_dir()

    def generate_mol_w_conformers(self):
        mol = Chem.AddHs(Chem.MolFromSmiles('Cc1ccccc1'))
        AllChem.EmbedMultipleConfs(mol, numConfs=3)
        return mol

    def generate_job_dir(self):
        job_dir = tempfile.mkdtemp()
        self.generate_raw_data_dir(parent_dir=job_dir)
        return job_dir

    def generate_raw_data_dir(self, parent_dir=None):
        raw_data_dir = os.path.join(parent_dir, 'raw_data')
        os.makedirs(raw_data_dir)
        conformer_file_path = os.path.join(raw_data_dir, 'conformers.sdf')
        with open(conformer_file_path, 'w') as conformer_file:
            writer = Chem.SDWriter(conformer_file)
            for conformer in self.mol.GetConformers():
                writer.write(self.mol, confId=conformer.GetId())
            writer.close()

    def test_generates_chemthings_from_inputs(self):
        chemthings = self.engine.parse_job_dir(self.job_dir,
                                               includes=['raw_data/*'])
        expected_chemthings = self.generate_chemthings_for_mol(mol=self.mol)
        self.assertEqual(self.get_sorted_chemthings(chemthings),
                         self.get_sorted_chemthings(expected_chemthings))

    def generate_chemthings_for_mol(self, mol=None):
        chemthings = [
            self.generate_chemthing_for_conformer(conformer,
                                                  props={'mol_idx': i})
            for i, conformer in enumerate(mol.GetConformers())
        ]
        return chemthings

    def generate_chemthing_for_conformer(self, conformer=None, props=None):
        chemthing = {
            'cml': self.generate_cml_for_conformer(conformer),
            'props': props,
        }
        return chemthing

    def generate_cml_for_conformer(self, conformer=None):
        serialized_conformer = Chem.MolToMolBlock(conformer.GetOwningMol(),
                                                  confId=conformer.GetId())
        pb_mol = pybel.readstring('sdf', serialized_conformer)
        return pb_mol.write('cml')

    def get_sorted_chemthings(self, chemthings):
        return sorted(chemthings, key=lambda cthing: cthing['props']['mol_idx'])

class UploadTestCase(BaseTestCase):
    def test_uploads_chemthings(self):
        self.fail()

    def test_outputs_upload_results(self):
        self.fail()
