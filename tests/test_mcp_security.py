import os
from unittest.mock import MagicMock
import sys

# Mock fastmcp before importing mcp_server
sys.modules["fastmcp"] = MagicMock()

from mcp_server import _is_path_allowed, allowed_paths

def test_is_path_allowed():
    # Setup
    sandbox_path = allowed_paths[0] # os.path.abspath("./sandbox")

    # 1. Exact match (Should be True)
    assert _is_path_allowed(sandbox_path) is True

    # 2. File in allowed directory (Should be True)
    test_file = os.path.join(sandbox_path, "test.txt")
    assert _is_path_allowed(test_file) is True

    # 3. Path sharing a prefix but not in the directory (Should be False)
    # If sandbox is /.../sandbox, then sandbox_secret is /.../sandbox_secret
    sandbox_secret = sandbox_path + "_secret"
    secret_file = os.path.join(sandbox_secret, "passwords.txt")
    assert _is_path_allowed(secret_file) is False

    # 4. Completely unrelated sensitive path (Should be False)
    assert _is_path_allowed("/etc/passwd") is False

    # 5. Parent directory (Should be False)
    parent_dir = os.path.dirname(sandbox_path)
    assert _is_path_allowed(parent_dir) is False

    # 6. Relative path traversal (should be resolved by abspath)
    traversal_path = os.path.join(sandbox_path, "..", "mcp_server.py")
    assert _is_path_allowed(traversal_path) is False
