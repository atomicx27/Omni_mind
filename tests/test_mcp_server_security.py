import sys
import os
import subprocess
import shlex

# Mock fastmcp
class MockFastMCP:
    def __init__(self, name):
        pass
    def tool(self):
        def decorator(func):
            return func
        return decorator
    def run(self):
        pass

sys.modules["fastmcp"] = MagicMock = type('Mock', (), {'FastMCP': MockFastMCP})

import mcp_server

def test_run_shell_basic():
    # Should work for simple commands
    result = mcp_server.run_shell("echo hello")
    print(f"DEBUG basic: {result}")
    assert "hello" in result

def test_run_shell_injection():
    # Should NOT work for injection
    result = mcp_server.run_shell("echo hello; ls /")
    print(f"DEBUG injection: {result}")
    assert "hello; ls /" in result
    assert "etc" not in result

def test_run_shell_path_traversal_check():
    # Existing check for ../
    result = mcp_server.run_shell("ls ../")
    print(f"DEBUG traversal: {result}")
    assert "Error: Command attempts path traversal" in result

def test_run_shell_absolute_path_check():
    # Existing check for /
    result = mcp_server.run_shell("/bin/ls")
    print(f"DEBUG absolute: {result}")
    assert "Error: Command attempts path traversal" in result

if __name__ == "__main__":
    try:
        # Ensure sandbox exists for test
        os.makedirs("./sandbox", exist_ok=True)
        test_run_shell_basic()
        test_run_shell_injection()
        test_run_shell_path_traversal_check()
        test_run_shell_absolute_path_check()
        print("All mcp_server tests passed!")
    except Exception as e:
        print(f"Tests failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
