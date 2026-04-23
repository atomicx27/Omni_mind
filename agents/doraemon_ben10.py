import json
from core.schemas import AgentResult, PersonaEnum, ActionTierEnum, ActionTypeEnum
from core.proxy import LLMProviderProxy

class DoraemonIntegrator:
    def __init__(self):
        self.persona = PersonaEnum.DORAEMON
        self.proxy = LLMProviderProxy()

    def fetch(self, task_id: str, url: str) -> AgentResult:
        system_prompt = "You are Doraemon, the API Integrator. Extract data from the given URL."
        prompt = f"Task ID: {task_id}\nURL: {url}\nExtract the data."

        response_str = self.proxy.generate_completion(model="mistral", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.TRIVIAL,
                action_type=ActionTypeEnum.SHELL_EXEC,
                target=url,
                payload={"data": "api_response_mock"},
                uncertainty_flags=["Failed to parse LLM response"],
                requires_human=False
            )

class Ben10Compositor:
    def __init__(self):
        self.persona = PersonaEnum.BEN10
        self.proxy = LLMProviderProxy()

    def compose(self, task_id: str, tools: list) -> AgentResult:
        system_prompt = "You are Ben 10, the MCP Tool Compositor. Construct a tool execution plan."
        prompt = f"Task ID: {task_id}\nTools: {tools}\nConstruct plan."

        response_str = self.proxy.generate_completion(model="claude-3.5-sonnet", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            return AgentResult(
                task_id=task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.STANDARD,
                action_type=ActionTypeEnum.SHELL_EXEC,
                target="tool_chain",
                payload={"plan": tools},
                uncertainty_flags=["Failed to parse LLM response"],
                requires_human=False
            )
