from typing import Dict, Any, List
import os
import subprocess
from fastmcp import FastMCP

mcp = FastMCP("AGS_Server")

os.makedirs("./sandbox", exist_ok=True)
os.makedirs("./tmp", exist_ok=True)

allowed_paths = [
    os.path.abspath("./sandbox"),
    os.path.abspath("./tmp")
]

def _is_path_allowed(path: str) -> bool:
    abs_path = os.path.abspath(path)
    for allowed in allowed_paths:
        if abs_path.startswith(allowed):
            return True
    return False

@mcp.tool()
def read_file(path: str) -> str:
    if not _is_path_allowed(path):
        return f"Error: Access denied to {path}"

    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(path: str, content: str) -> str:
    if not _is_path_allowed(path):
        return f"Error: Access denied to {path}"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return "Success"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def run_shell(command: str, cwd: str = "./sandbox") -> str:
    if not _is_path_allowed(cwd):
        return f"Error: Access denied to directory {cwd}"

    if "../" in command or command.startswith("/"):
        return "Error: Command attempts path traversal or uses absolute paths."

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error executing command: {str(e)}"

if __name__ == "__main__":
    print("Starting FastMCP server with path actuation limits...")
    mcp.run()
