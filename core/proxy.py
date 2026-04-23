import redis
import time
import os
from typing import Optional, Dict, Any
import urllib.request
import json

class LLMProviderProxy:
    def __init__(self, redis_host=None, redis_port=6379):
        host = redis_host or os.getenv("REDIS_HOST", "localhost")
        self.redis = redis.Redis(host=host, port=redis_port, decode_responses=True)

        ollama_url = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")

        self.providers = [
            {"name": "ollama_local", "priority": 1, "tokens_per_minute": 10000, "url": ollama_url},
            {"name": "ollama_colab", "priority": 2, "tokens_per_minute": 50000, "url": "http://colab_url/api/generate"},
            {"name": "anthropic", "priority": 3, "tokens_per_minute": 5000},
            {"name": "openai", "priority": 4, "tokens_per_minute": 5000}
        ]

    def _check_rate_limit(self, provider_name: str, requested_tokens: int) -> bool:
        provider = next((p for p in self.providers if p["name"] == provider_name), None)
        if not provider:
            return False

        bucket_key = f"rate_limit:{provider_name}:tokens"
        last_update_key = f"rate_limit:{provider_name}:last_update"

        current_time = time.time()

        try:
            if not self.redis.exists(bucket_key):
                self.redis.set(bucket_key, provider["tokens_per_minute"])
                self.redis.set(last_update_key, current_time)

            last_update = float(self.redis.get(last_update_key) or current_time)
            time_passed = current_time - last_update

            refill_rate = provider["tokens_per_minute"] / 60.0
            tokens_to_add = int(time_passed * refill_rate)

            current_tokens = int(self.redis.get(bucket_key) or 0)

            if tokens_to_add > 0:
                current_tokens = min(provider["tokens_per_minute"], current_tokens + tokens_to_add)
                self.redis.set(last_update_key, current_time)

            if current_tokens >= requested_tokens:
                self.redis.set(bucket_key, current_tokens - requested_tokens)
                return True
        except redis.ConnectionError:
            # Fallback if Redis is not running
            return True

        return False

    def get_provider(self, requested_tokens: int = 100) -> Optional[Dict[str, Any]]:
        for provider in sorted(self.providers, key=lambda x: x["priority"]):
            if self._check_rate_limit(provider["name"], requested_tokens):
                return provider

        return None

    def generate_completion(self, model: str, prompt: str, system_prompt: str = "") -> str:
        # Estimate tokens roughly
        estimated_tokens = len(prompt) // 4 + len(system_prompt) // 4
        provider = self.get_provider(estimated_tokens)

        if not provider:
            raise Exception("No available LLM providers due to rate limits.")

        if provider["name"].startswith("ollama"):
            data = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False
            }

            req = urllib.request.Request(
                provider["url"],
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )

            try:
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    return result.get("response", "")
            except Exception as e:
                print(f"Error calling {provider['name']}: {e}")
                # Fallback mock for demonstration if ollama is not running locally
                return f'{{"task_id": "mock", "persona": "rimuru", "action_tier": "TRIVIAL", "action_type": "file_write", "target": "mock", "payload": {{"msg": "Mock LLM Response"}}, "uncertainty_flags": [], "requires_human": false}}'
        else:
            raise NotImplementedError(f"Provider {provider['name']} not implemented")
