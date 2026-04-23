import json
from typing import Dict, Any
from core.schemas import AgentResult, PersonaEnum, ActionTierEnum, ActionTypeEnum
from core.proxy import LLMProviderProxy

class ChhotaBheemHeavy:
    def __init__(self):
        self.persona = PersonaEnum.CHHOTA_BHEEM
        self.proxy = LLMProviderProxy()

    def dispatch(self, task_id: str, payload_size: int) -> AgentResult:
        system_prompt = "You are Chhota Bheem, the Heavy Colab Dispatcher. Format heavy payload for execution."
        prompt = f"Task ID: {task_id}\nPayload Size: {payload_size}\nFormat it."

        response_str = self.proxy.generate_completion(model="llama3", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.STANDARD,
                action_type=ActionTypeEnum.SHELL_EXEC,
                target="colab_cluster",
                payload={"job_id": f"heavy_job_{task_id}"},
                uncertainty_flags=["Failed to parse LLM response"],
                requires_human=False
            )
