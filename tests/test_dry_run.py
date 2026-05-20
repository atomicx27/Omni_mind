import unittest
import os
import hashlib
import json
import base64
import shutil
import tempfile
from unittest.mock import MagicMock
import sys

# Mock sqlmodel and core.db before importing SnapshotEngine
sys.modules['sqlmodel'] = MagicMock()
mock_db = MagicMock()
sys.modules['core.db'] = mock_db

from core.dry_run import SnapshotEngine

class TestSnapshotEngine(unittest.TestCase):
    def setUp(self):
        self.db_session = MagicMock()
        self.engine = SnapshotEngine(self.db_session)
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_hash_file_exists(self):
        test_file = os.path.join(self.test_dir, "test.txt")
        content = b"hello world"
        with open(test_file, "wb") as f:
            f.write(content)

        expected_hash = hashlib.sha256(content).hexdigest()
        actual_hash = self.engine.hash_file(test_file)

        self.assertEqual(actual_hash, expected_hash)

    def test_hash_file_not_exists(self):
        actual_hash = self.engine.hash_file("non_existent_file.txt")
        self.assertEqual(actual_hash, "")

    def test_read_file_content_exists(self):
        test_file = os.path.join(self.test_dir, "test.txt")
        content = b"hello content"
        with open(test_file, "wb") as f:
            f.write(content)

        expected_content = base64.b64encode(content).decode('utf-8')
        actual_content = self.engine.read_file_content(test_file)

        self.assertEqual(actual_content, expected_content)

    def test_read_file_content_not_exists(self):
        actual_content = self.engine.read_file_content("non_existent_file.txt")
        self.assertEqual(actual_content, "")

    def test_create_snapshot_directory(self):
        file1 = os.path.join(self.test_dir, "file1.txt")
        with open(file1, "wb") as f:
            f.write(b"content1")

        snapshot_hash = self.engine.create_snapshot(self.test_dir)
        self.assertNotEqual(snapshot_hash, "")

        self.db_session.add.assert_called()
        self.db_session.commit.assert_called()

    def test_verify_execution_success(self):
        f1_path = os.path.join(self.test_dir, "f1.txt")
        with open(f1_path, "wb") as f:
            f.write(b"data1")

        blobs = {
            f1_path: {
                "hash": hashlib.sha256(b"data1").hexdigest()
            }
        }

        mock_snapshot = MagicMock()
        mock_snapshot.blobs_json = json.dumps(blobs)
        self.db_session.exec.return_value.first.return_value = mock_snapshot

        self.assertTrue(self.engine.verify_execution(self.test_dir, "some_hash"))

    def test_verify_execution_modified(self):
        f1_path = os.path.join(self.test_dir, "f1.txt")
        with open(f1_path, "wb") as f:
            f.write(b"modified data")

        blobs = {
            f1_path: {
                "hash": hashlib.sha256(b"original data").hexdigest()
            }
        }

        mock_snapshot = MagicMock()
        mock_snapshot.blobs_json = json.dumps(blobs)
        self.db_session.exec.return_value.first.return_value = mock_snapshot

        self.assertFalse(self.engine.verify_execution(self.test_dir, "some_hash"))

    def test_restore_from_snapshot(self):
        f1_path = os.path.join(self.test_dir, "f1.txt")
        content = b"original content"

        blobs = {
            f1_path: {
                "content": base64.b64encode(content).decode('utf-8')
            }
        }

        mock_snapshot = MagicMock()
        mock_snapshot.blobs_json = json.dumps(blobs)
        self.db_session.exec.return_value.first.return_value = mock_snapshot

        success = self.engine.restore_from_snapshot("some_hash")
        self.assertTrue(success)
        self.assertTrue(os.path.exists(f1_path))
        with open(f1_path, "rb") as f:
            self.assertEqual(f.read(), content)

if __name__ == "__main__":
    unittest.main()
