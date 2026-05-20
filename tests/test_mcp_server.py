import sys
from unittest.mock import MagicMock

# Mock fastmcp before importing mcp_server
mock_fastmcp = MagicMock()
# mcp = FastMCP("AGS_Server")
# @mcp.tool()
# def read_file...
# mock_fastmcp.FastMCP() returns an instance (another mock)
# instance.tool() returns a decorator (another mock)
# decorator(func) returns the function.
def mock_tool_decorator(*args, **kwargs):
    def decorator(f):
        return f
    return decorator

mock_fastmcp.FastMCP.return_value.tool = mock_tool_decorator
sys.modules["fastmcp"] = mock_fastmcp

import pytest
import mcp_server
from mcp_server import run_shell, _is_path_allowed
from unittest.mock import patch
import subprocess
import os

def test_is_path_allowed():
    # Test allowed paths
    sandbox_path = os.path.abspath("./sandbox")
    tmp_path = os.path.abspath("./tmp")

    assert _is_path_allowed(sandbox_path) is True
    assert _is_path_allowed(tmp_path) is True
    assert _is_path_allowed(os.path.join(sandbox_path, "test.txt")) is True

    # Test disallowed paths
    assert _is_path_allowed("/etc/passwd") is False
    assert _is_path_allowed(os.path.join(sandbox_path, "../../etc/passwd")) is False

def test_run_shell_disallowed_cwd():
    result = run_shell("ls", cwd="/root")
    assert "Error: Access denied to directory /root" in result

def test_run_shell_path_traversal():
    result = run_shell("cat ../etc/passwd")
    assert "Error: Command attempts path traversal or uses absolute paths." in result

def test_run_shell_absolute_path():
    result = run_shell("/usr/bin/id")
    assert "Error: Command attempts path traversal or uses absolute paths." in result

@patch("subprocess.run")
def test_run_shell_success(mock_run):
    mock_run.return_value = MagicMock(stdout="hello", stderr="", returncode=0)
    result = run_shell("echo hello")
    assert "STDOUT:\nhello" in result
    assert "STDERR:\n" in result
    mock_run.assert_called_once_with(
        "echo hello",
        shell=True,
        cwd="./sandbox",
        capture_output=True,
        text=True,
        timeout=60
    )

@patch("subprocess.run")
def test_run_shell_timeout(mock_run):
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="echo hello", timeout=60)
    result = run_shell("echo hello")
    assert "Error: Command timed out" in result

@patch("subprocess.run")
def test_run_shell_exception(mock_run):
    mock_run.side_effect = Exception("Something went wrong")
    result = run_shell("echo hello")
    assert "Error executing command: Something went wrong" in result
