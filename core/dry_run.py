import hashlib
import os
import json

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

    def create_snapshot(self, target_scope: str) -> str:
        blobs = {}

        if os.path.isfile(target_scope):
            blobs[target_scope] = self.hash_file(target_scope)
        elif os.path.isdir(target_scope):
            for root, _, files in os.walk(target_scope):
                for file in files:
                    filepath = os.path.join(root, file)
                    blobs[filepath] = self.hash_file(filepath)

        snapshot_hash = hashlib.sha256(json.dumps(blobs, sort_keys=True).encode()).hexdigest()
        return snapshot_hash

    def verify_execution(self, target_scope: str, expected_hash: str) -> bool:
        current_hash = self.create_snapshot(target_scope)
        return current_hash == expected_hash
