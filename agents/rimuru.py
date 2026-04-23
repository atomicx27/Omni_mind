import json
from core.schemas import AgentResult, PersonaEnum, ActionTierEnum, ActionTypeEnum
from core.proxy import LLMProviderProxy

class RimuruBridge:
    def __init__(self):
        self.persona = PersonaEnum.RIMURU
        self.proxy = LLMProviderProxy()

    def summarize(self, task_id: str, context: str) -> AgentResult:
        system_prompt = "You are Rimuru, the Context Bridge. Summarize context."
        prompt = f"Task ID: {task_id}\nContext: {context}\nSummarize it."

        response_str = self.proxy.generate_completion(model="phi3:mini", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.TRIVIAL,
                action_type=ActionTypeEnum.FILE_WRITE,
                target="context_summary",
                payload={"summary": f"Summarized {len(context)} chars"},
                uncertainty_flags=["Failed to parse LLM response"],
                requires_human=False
            )
