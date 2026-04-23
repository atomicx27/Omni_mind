from pydantic import BaseModel, Field
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
    SHELL_EXEC = "shell_exec"
    ESCALATE = "escalate"

class AgentResult(BaseModel):
    task_id: str
    persona: str
    action_tier: ActionTierEnum
    action_type: ActionTypeEnum
    target: str
    payload: Dict[str, Any]
    uncertainty_flags: List[str]
    requires_human: bool
    handoff_to: Optional[str] = None

class HandoffPayload(BaseModel):
    state: Dict[str, Any]
    reason: str
