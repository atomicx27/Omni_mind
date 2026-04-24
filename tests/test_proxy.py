import pytest
from core.proxy import LLMProviderProxy
import os
import json
import time
from unittest.mock import patch, MagicMock

@patch('redis.Redis')
@patch('time.time')
def test_proxy_rate_limit(mock_time, mock_redis_class):
    mock_redis = MagicMock()
    mock_redis_class.return_value = mock_redis
    mock_time.return_value = 1000.0

    proxy = LLMProviderProxy()

    # Test valid tokens logic
    # First provider: ollama_local (priority 1), 10000 tokens
    # Second provider: ollama_colab (priority 2), 50000 tokens

    # Simulating rate limiting
    def mock_redis_get(key):
        if key == "rate_limit:ollama_local:tokens":
            return "50" # Not enough for requested 100 tokens
        if key == "rate_limit:ollama_colab:tokens":
            return "2000" # Enough tokens
        if key.endswith("last_update"):
            return "1000.0"
        return None

    mock_redis.exists.return_value = True
    mock_redis.get.side_effect = mock_redis_get

    valid_providers = proxy.get_providers(requested_tokens=100)

    assert len(valid_providers) == 1
    assert valid_providers[0]["name"] == "ollama_colab"
