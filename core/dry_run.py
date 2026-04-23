import hashlib
import os
import json
from core.db import ExecutionSnapshot

class SnapshotEngine:
    def __init__(self, db_session):
        self.db = db_session

    def hash_file(self, filepath: str) -> str:
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except FileNotFoundError:
            return ""

    def read_file_content(self, filepath: str) -> str:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return ""
        except UnicodeDecodeError:
            # Skip binary files
            return ""

    def create_snapshot(self, target_scope: str) -> str:
        blobs = {}

        if os.path.isfile(target_scope):
            blobs[target_scope] = {
                "hash": self.hash_file(target_scope),
                "content": self.read_file_content(target_scope)
            }
        elif os.path.isdir(target_scope):
            for root, _, files in os.walk(target_scope):
                for file in files:
                    filepath = os.path.join(root, file)
                    blobs[filepath] = {
                        "hash": self.hash_file(filepath),
                        "content": self.read_file_content(filepath)
                    }

        snapshot_hash = hashlib.sha256(json.dumps(blobs, sort_keys=True).encode()).hexdigest()

        snapshot = ExecutionSnapshot(
            snapshot_hash=snapshot_hash,
            target_scope=target_scope,
            blobs_json=json.dumps(blobs)
        )
        self.db.add(snapshot)
        self.db.commit()

        return snapshot_hash

    def verify_execution(self, target_scope: str, expected_hash: str) -> bool:
        # Don't save this temporary snapshot to DB
        blobs = {}
        if os.path.isfile(target_scope):
             blobs[target_scope] = {
                "hash": self.hash_file(target_scope),
                "content": self.read_file_content(target_scope)
            }
        elif os.path.isdir(target_scope):
            for root, _, files in os.walk(target_scope):
                for file in files:
                    filepath = os.path.join(root, file)
                    blobs[filepath] = {
                        "hash": self.hash_file(filepath),
                        "content": self.read_file_content(filepath)
                    }
        current_hash = hashlib.sha256(json.dumps(blobs, sort_keys=True).encode()).hexdigest()
        return current_hash == expected_hash

    def restore_from_snapshot(self, snapshot_hash: str) -> bool:
        snapshot = self.db.get(ExecutionSnapshot, snapshot_hash)
        if not snapshot:
            return False

        blobs = json.loads(snapshot.blobs_json)

        for filepath, data in blobs.items():
            content = data.get("content", "")
            if content:
                os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

        return True
