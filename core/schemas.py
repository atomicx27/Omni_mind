from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Dict
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

class HandoffPayload(BaseModel):
    state: Dict[str, Any]
    reason: str
