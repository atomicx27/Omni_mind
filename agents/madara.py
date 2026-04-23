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
        payload = task.task_payload

        if re.search(r"sudo|rm -rf|\.env", payload, re.IGNORECASE):
            return PersonaEnum.ICHIGO

        if not task.parent_task_ids_json == "[]":
            return PersonaEnum.MADARA

        if task.action_tier == "CRITICAL":
            return PersonaEnum.ITACHI
        elif task.task_type == "mcp_tool_chain":
            return PersonaEnum.BEN10
        elif task.task_type == "api_integration":
            return PersonaEnum.DORAEMON
        elif task.task_type in ["optimize", "refactor"]:
            return PersonaEnum.GOKU
        elif task.retry_count > 0:
            return PersonaEnum.NARUTO
        elif task.task_type == "heavy_compute":
            return PersonaEnum.CHHOTA_BHEEM
        elif task.task_type in ["mvp", "prototype"] and task.action_tier in ["TRIVIAL", "STANDARD"]:
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
