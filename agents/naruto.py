import json
from typing import Dict, Any
from core.schemas import AgentResult, PersonaEnum, ActionTierEnum, ActionTypeEnum
from core.memory import FailureMemory
from core.proxy import LLMProviderProxy

class NarutoHealer:
    def __init__(self, memory_db: FailureMemory):
        self.persona = PersonaEnum.NARUTO
        self.memory = memory_db
        self.proxy = LLMProviderProxy()

    def heal(self, task_id: str, error_message: str, stack_trace: str) -> AgentResult:
        match_result = self.memory.check_failure(error_message, stack_trace)

        if match_result["matched"]:
            resolution = match_result["resolution"]
            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.STANDARD,
                action_type=ActionTypeEnum.FILE_WRITE,
                target="code_repair",
                payload={"resolution": resolution, "similarity": match_result["similarity"]},
                uncertainty_flags=[],
                requires_human=False
            )
        else:
            system_prompt = "You are Naruto, the Self-Healer. Generate code fixes based on error traces."
            prompt = f"Error: {error_message}\nTrace: {stack_trace}\nFix it."

            response_str = self.proxy.generate_completion(model="llama3", prompt=prompt, system_prompt=system_prompt)

            try:
                parsed = json.loads(response_str)
                return AgentResult(**parsed)
            except Exception as e:
                return AgentResult(
                    task_id=task_id,
                    persona=self.persona,
                    action_tier=ActionTierEnum.CRITICAL,
                    action_type=ActionTypeEnum.ESCALATE,
                    target="unknown_error",
                    payload={"error": error_message},
                    uncertainty_flags=["Novel error, no resolution found", "LLM parse failed"],
                    requires_human=True
                )
