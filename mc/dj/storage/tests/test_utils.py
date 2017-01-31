import os
import tempfile
import unittest

from .. import utils as storage_utils


class GetStorageBackendTestCase(unittest.TestCase):
    def test_gets_storage_backend(self):
        backend = storage_utils.get_storage_backend()
        self.assertTrue(isinstance(backend, storage_utils.FileSystemBackend))

class FileSystemBackendTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.backend = storage_utils.FileSystemBackend(base_dir=self.tmpdir)

class FileSystemBackendPostTestCase(FileSystemBackendTestCase):
    def test_creates_bytes_at_random_uuid(self):
        byte_data = b'some bytes'
        post_result = self.backend.post(data=byte_data)
        expected_file_path = os.path.join(self.backend.base_dir,
                                          post_result['key'])
        file_contents = open(expected_file_path, 'rb').read()
        self.assertEqual(file_contents, byte_data)

class FileSystemBackendGetTestCase(FileSystemBackendTestCase):
    def test_returns_bytes_at_uuid(self):
        byte_data = b'some bytes'
        post_result = self.backend.post(data=byte_data)
        get_result = self.backend.get(params={'key': post_result['key']})
        self.assertEqual(get_result, {'data': byte_data})