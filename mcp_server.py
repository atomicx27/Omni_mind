from typing import Dict, Any, List
import os
from fastmcp import FastMCP

mcp = FastMCP("AGS_Server")

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
    """Read contents of a file securely."""
    if not _is_path_allowed(path):
        return f"Error: Access denied to {path}"

    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write contents to a file securely."""
    if not _is_path_allowed(path):
        return f"Error: Access denied to {path}"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return "Success"
    except Exception as e:
        return f"Error writing file: {str(e)}"

if __name__ == "__main__":
    print("Starting FastMCP server with path actuation limits...")
    mcp.run()
