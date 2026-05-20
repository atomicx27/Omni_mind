import sys
from unittest.mock import MagicMock
import types

# Mock pydantic
pydantic_mock = MagicMock()
class BaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    def model_dump(self):
        return self.__dict__

pydantic_mock.BaseModel = BaseModel
pydantic_mock.ConfigDict = MagicMock()
sys.modules['pydantic'] = pydantic_mock

# Mock redis
sys.modules['redis'] = MagicMock()

# Mock sqlmodel
sqlmodel_mock = MagicMock()
sqlmodel_mock.Session = MagicMock()
sys.modules['sqlmodel'] = sqlmodel_mock

# Mock core.schemas
import enum

class PersonaEnum(str, enum.Enum):
    NATSU = "natsu"
    GOKU = "goku"

class ActionTierEnum(str, enum.Enum):
    STANDARD = "STANDARD"

class ActionTypeEnum(str, enum.Enum):
    FILE_WRITE = "file_write"

class AgentResult(BaseModel):
    pass

schemas_mock = types.ModuleType('core.schemas')
schemas_mock.PersonaEnum = PersonaEnum
schemas_mock.ActionTierEnum = ActionTierEnum
schemas_mock.ActionTypeEnum = ActionTypeEnum
schemas_mock.AgentResult = AgentResult
sys.modules['core.schemas'] = schemas_mock

# Mock core.proxy
class LLMProviderProxy:
    def generate_completion(self, model, prompt, system_prompt=""):
        pass

proxy_mock = types.ModuleType('core.proxy')
proxy_mock.LLMProviderProxy = LLMProviderProxy
sys.modules['core.proxy'] = proxy_mock

import pytest
from agents.natsu_goku import NatsuMVP
from unittest.mock import patch
import json

def test_natsu_mvp_success():
    with patch('agents.natsu_goku.LLMProviderProxy.generate_completion') as mock_gen:
        mock_gen.return_value = json.dumps({
            "task_id": "test_1",
            "persona": "natsu",
            "action_tier": "STANDARD",
            "action_type": "file_write",
            "target": "mvp_code",
            "payload": {"code": "print('hello')"},
            "uncertainty_flags": [],
            "requires_human": False
        })

        natsu = NatsuMVP()
        result = natsu.execute("test_1", "Write hello world")

        assert isinstance(result, AgentResult)
        assert result.payload["code"] == "print('hello')"
        assert result.task_id == "test_1"

def test_natsu_mvp_fallback_markdown():
    with patch('agents.natsu_goku.LLMProviderProxy.generate_completion') as mock_gen:
        # Return markdown code block instead of JSON
        mock_gen.return_value = "Here is your code:\n```python\nprint('hello markdown')\n```"

        natsu = NatsuMVP()
        result = natsu.execute("test_1", "Write hello world")

        assert isinstance(result, AgentResult)
        assert result.payload["code"] == "print('hello markdown')"
        assert "Failed to parse LLM response, extracted from raw" in result.uncertainty_flags

def test_natsu_mvp_fallback_raw():
    with patch('agents.natsu_goku.LLMProviderProxy.generate_completion') as mock_gen:
        # Return raw text
        mock_gen.return_value = "print('hello raw')"

        natsu = NatsuMVP()
        result = natsu.execute("test_1", "Write hello world")

        assert isinstance(result, AgentResult)
        assert result.payload["code"] == "print('hello raw')"
        assert "Failed to parse LLM response, extracted from raw" in result.uncertainty_flags

def test_natsu_mvp_fallback_empty():
    with patch('agents.natsu_goku.LLMProviderProxy.generate_completion') as mock_gen:
        # Return empty string
        mock_gen.return_value = ""

        natsu = NatsuMVP()
        result = natsu.execute("test_1", "Write hello world")

        assert isinstance(result, AgentResult)
        assert result.payload["code"] == "# TODO: implement\npass"
        assert "Failed to parse LLM response, extracted from raw" in result.uncertainty_flags
