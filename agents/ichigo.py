import re
import json
from typing import Dict, Any
from core.schemas import AgentResult, PersonaEnum, ActionTierEnum, ActionTypeEnum
from core.proxy import LLMProviderProxy

class IchigoSecurity:
    def __init__(self):
        self.persona = PersonaEnum.ICHIGO
        self.proxy = LLMProviderProxy()
        self.destructive_patterns = [
            re.compile(r"rm\s+-rf\s+/"),
            re.compile(r">\s*\.env"),
            re.compile(r"chmod\s+777\s+/"),
            re.compile(r"sudo\s+su")
        ]

    def check_command(self, task_id: str, command: str) -> AgentResult:
        flags = []
        for pattern in self.destructive_patterns:
            if pattern.search(command):
                flags.append(f"Destructive pattern matched: {pattern.pattern}")

        if flags:
             return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.CRITICAL,
                action_type=ActionTypeEnum.ESCALATE,
                target=command,
                payload={"safe": False},
                uncertainty_flags=flags,
                requires_human=True
            )

        system_prompt = "You are Ichigo, the Security Guardian. Perform semantic security check on commands."
        prompt = f"Task ID: {task_id}\nCommand: {command}\nIs it semantically safe?"

        response_str = self.proxy.generate_completion(model="llama3", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.TRIVIAL,
                action_type=ActionTypeEnum.SHELL_EXEC,
                target=command,
                payload={"safe": True},
                uncertainty_flags=["Failed to parse LLM response"],
                requires_human=False
            )
