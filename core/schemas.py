from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict, Union
from enum import Enum

class PersonaEnum(str, Enum):
    ITACHI = "itachi"
    MADARA = "madara"
    CHHOTA_BHEEM = "chhota_bheem"
    DORAEMON = "doraemon"
    RIMURU = "rimuru"
    GOKU = "goku"
    NARUTO = "naruto"
    ICHIGO = "ichigo"
    NATSU = "natsu"
    BEN10 = "ben10"

class ActionTierEnum(str, Enum):
    TRIVIAL = "TRIVIAL"
    STANDARD = "STANDARD"
    CRITICAL = "CRITICAL"

class ActionTypeEnum(str, Enum):
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    SHELL_EXEC = "shell_exec"
    API_CALL = "api_call"
    RESEARCH = "research"
    SUMMARIZE = "summarize"
    ESCALATE = "escalate"

class AgentResult(BaseModel):
    model_config = ConfigDict(strict=True)

    task_id: str
    persona: PersonaEnum
    action_tier: ActionTierEnum
    action_type: ActionTypeEnum
    target: str
    payload: Dict[str, Any]
    uncertainty_flags: List[str]
    requires_human: bool
    handoff_to: Optional[PersonaEnum] = None

class BaseHandoff(BaseModel):
    model_config = ConfigDict(strict=True)
    reason: str
    context_str: Optional[str] = None

class NatsuToGokuHandoff(BaseHandoff):
    target_node: str
    mvp_code: str

class NarutoToItachiHandoff(BaseHandoff):
    target_node: str
    fixed_code: str
    error_trace: str

class DoraemonToBen10Handoff(BaseHandoff):
    target_node: str
    api_schema: Dict[str, Any]

class GenericHandoff(BaseHandoff):
    state: Dict[str, Any]

HandoffPayload = Union[NatsuToGokuHandoff, NarutoToItachiHandoff, DoraemonToBen10Handoff, GenericHandoff]
