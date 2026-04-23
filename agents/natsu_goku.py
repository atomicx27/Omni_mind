import json
from core.schemas import AgentResult, PersonaEnum, ActionTierEnum, ActionTypeEnum
from core.proxy import LLMProviderProxy

class GokuOptimizer:
    def __init__(self):
        self.persona = PersonaEnum.GOKU
        self.proxy = LLMProviderProxy()

    def optimize(self, task_id: str, code: str) -> AgentResult:
        system_prompt = "You are Goku, the Code Optimizer. Refactor code."
        prompt = f"Task ID: {task_id}\nCode: {code}\nOptimize it."

        response_str = self.proxy.generate_completion(model="llama3", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.STANDARD,
                action_type=ActionTypeEnum.FILE_WRITE,
                target="optimized_code",
                payload={"code": code + "\n# Optimized"},
                uncertainty_flags=["Failed to parse LLM response"],
                requires_human=False
            )

class NatsuMVP:
    def __init__(self):
        self.persona = PersonaEnum.NATSU
        self.proxy = LLMProviderProxy()

    def execute(self, task_id: str, prompt_text: str) -> AgentResult:
        system_prompt = "You are Natsu, the MVP Executor. Write extreme speed code."
        prompt = f"Task ID: {task_id}\nPrompt: {prompt_text}\nWrite MVP code."

        response_str = self.proxy.generate_completion(model="llama3", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.STANDARD,
                action_type=ActionTypeEnum.FILE_WRITE,
                target="mvp_code",
                payload={"code": "# TODO: implement\npass"},
                uncertainty_flags=["Failed to parse LLM response"],
                requires_human=False
            )
