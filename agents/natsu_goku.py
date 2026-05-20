import json
import re
from core.schemas import AgentResult, PersonaEnum, ActionTierEnum, ActionTypeEnum
from core.proxy import LLMProviderProxy

class GokuOptimizer:
    def __init__(self):
        self.persona = PersonaEnum.GOKU
        self.proxy = LLMProviderProxy()

    def optimize(self, task_id: str, code: str) -> AgentResult:
        system_prompt = "You are Goku, the Code Optimizer. Refactor code."
        prompt = f"Task ID: {task_id}\nCode: {code}\nOptimize it."

        response_str = self.proxy.generate_completion(model="codellama", prompt=prompt, system_prompt=system_prompt)

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

        response_str = self.proxy.generate_completion(model="codellama", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            # Fallback: Try to extract code from markdown or raw response
            extracted_code = "# TODO: implement\npass"

            # Try to find code in triple backticks
            code_match = re.search(r"```(?:python)?\n(.*?)\n```", response_str, re.DOTALL)
            if code_match:
                extracted_code = code_match.group(1)
            elif response_str.strip():
                # If no code blocks but response has text, use it as raw code
                extracted_code = response_str.strip()

            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.STANDARD,
                action_type=ActionTypeEnum.FILE_WRITE,
                target="mvp_code",
                payload={"code": extracted_code},
                uncertainty_flags=["Failed to parse LLM response, extracted from raw"],
                requires_human=False
            )
