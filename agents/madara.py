import time
import json
import re
from typing import Dict, Any, List
from core.db import get_session, DAGTask
from core.schemas import AgentResult, PersonaEnum, ActionTierEnum, ActionTypeEnum
from core.proxy import LLMProviderProxy
from sqlmodel import select

class MadaraOrchestrator:
    def __init__(self, db_session):
        self.db = db_session
        self.persona = PersonaEnum.MADARA
        self.proxy = LLMProviderProxy()

    def poll_tasks(self) -> List[DAGTask]:
        tasks = self.db.exec(select(DAGTask).where(DAGTask.status == "PENDING")).all()
        ready_tasks = []
        for task in tasks:
            parent_ids = json.loads(task.parent_task_ids_json)
            parents = self.db.exec(select(DAGTask).where(DAGTask.task_id.in_(parent_ids))).all()
            if all(p.status == "RESOLVED" for p in parents):
                ready_tasks.append(task)
        return ready_tasks

    def _routing_classifier(self, task: DAGTask) -> PersonaEnum:
        # Deterministic routing logic priority
        payload = task.assigned_persona # Mocking task payload content for routing

        if re.search(r"sudo|rm -rf|\.env", payload, re.IGNORECASE):
            return PersonaEnum.ICHIGO

        # Mocking task attributes for demonstration
        task_type = "standard"
        action_tier = ActionTierEnum.STANDARD
        estimated_tokens = 1000
        previous_failures = 0
        requires_mcp_tools = False

        if action_tier == ActionTierEnum.CRITICAL:
            return PersonaEnum.ITACHI
        elif not task.parent_task_ids_json == "[]": # has unresolved parents -> madara (but shouldn't be polled)
            return PersonaEnum.MADARA
        elif requires_mcp_tools:
            return PersonaEnum.BEN10
        elif task_type == "api_integration":
            return PersonaEnum.DORAEMON
        elif task_type in ["optimize", "refactor"]:
            return PersonaEnum.GOKU
        elif previous_failures > 0:
            return PersonaEnum.NARUTO
        elif estimated_tokens > 50000:
            return PersonaEnum.CHHOTA_BHEEM
        elif task_type in ["mvp", "prototype"] and action_tier in [ActionTierEnum.TRIVIAL, ActionTierEnum.STANDARD]:
            return PersonaEnum.NATSU

        return PersonaEnum.RIMURU

    def route_task(self, task: DAGTask) -> AgentResult:
        assigned_persona = self._routing_classifier(task)

        return AgentResult(
            task_id=task.task_id,
            persona=self.persona,
            action_tier=ActionTierEnum.STANDARD,
            action_type=ActionTypeEnum.SHELL_EXEC,
            target="orchestration",
            payload={"action": "route_task", "task": task.task_id},
            uncertainty_flags=[],
            requires_human=False,
            handoff_to=assigned_persona
        )
