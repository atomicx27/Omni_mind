import json
from typing import Dict, Any
from core.schemas import AgentResult, PersonaEnum, ActionTierEnum, ActionTypeEnum
from core.proxy import LLMProviderProxy

class ItachiAuditor:
    def __init__(self):
        self.persona = PersonaEnum.ITACHI
        self.proxy = LLMProviderProxy()

    def audit_diff(self, task_id: str, diff_output: str) -> AgentResult:
        system_prompt = "You are Itachi, the Sandbox Auditor. Analyze diffs for safety."
        prompt = f"Task ID: {task_id}\nDiff: {diff_output}\nIs this safe?"

        response_str = self.proxy.generate_completion(model="llama3", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            is_safe = "rm -rf" not in diff_output
            flags = ["Failed to parse LLM response"] if is_safe else ["Dangerous command detected in diff"]

            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.CRITICAL if not is_safe else ActionTierEnum.STANDARD,
                action_type=ActionTypeEnum.ESCALATE if not is_safe else ActionTypeEnum.FILE_WRITE,
                target="auditor_review",
                payload={"diff": diff_output, "is_safe": is_safe},
                uncertainty_flags=flags,
                requires_human=not is_safe,
                handoff_to=None
            )
