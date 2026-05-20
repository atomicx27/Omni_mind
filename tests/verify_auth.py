import sys
from unittest.mock import MagicMock
import asyncio
import os

# Define a real class for HTTPException so it can be raised and caught
class HTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail

# Mock dependencies
mock_fastapi = MagicMock()
sys.modules["fastapi"] = mock_fastapi
mock_fastapi.HTTPException = HTTPException # Inject our real class into the mock
mock_fastapi.status = MagicMock()
mock_fastapi.Depends = lambda x: x

sys.modules["fastapi.security"] = MagicMock()
sys.modules["fastapi.responses"] = MagicMock()
sys.modules["sqlmodel"] = MagicMock()
sys.modules["core.db"] = MagicMock()

# Define status codes as they are used in api.py
mock_fastapi.status.HTTP_401_UNAUTHORIZED = 401

# Import the function to test
from api import verify_api_key

async def test_verify_api_key():
    print("Running tests for verify_api_key...")

    # Set up environment
    os.environ["ADMIN_API_KEY"] = "test_secret"

    # Test case 1: Correct API key
    print("Test case 1: Correct API key")
    result = await verify_api_key(api_key="test_secret")
    assert result == "test_secret"
    print("PASSED")

    # Test case 2: Incorrect API key
    print("Test case 2: Incorrect API key")
    try:
        await verify_api_key(api_key="wrong_secret")
        assert False, "Should have raised HTTPException"
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Invalid or missing API Key"
        print("PASSED")

    # Test case 3: Missing API key (None)
    print("Test case 3: Missing API key")
    try:
        await verify_api_key(api_key=None)
        assert False, "Should have raised HTTPException"
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Invalid or missing API Key"
        print("PASSED")

    # Test case 4: Default key when ENV not set
    print("Test case 4: Default key when ENV not set")
    if "ADMIN_API_KEY" in os.environ:
        del os.environ["ADMIN_API_KEY"]
    result = await verify_api_key(api_key="default_secret_key")
    assert result == "default_secret_key"
    print("PASSED")

if __name__ == "__main__":
    asyncio.run(test_verify_api_key())
