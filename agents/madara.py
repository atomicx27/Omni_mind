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

        all_parent_ids = set()
        task_to_parents = {}
        for task in tasks:
            p_ids = json.loads(task.parent_task_ids_json)
            all_parent_ids.update(p_ids)
            task_to_parents[task.task_id] = p_ids

        # Batch fetch all parents
        all_parents = self.db.exec(select(DAGTask).where(DAGTask.task_id.in_(list(all_parent_ids)))).all()
        parent_status_map = {p.task_id: p.status for p in all_parents}

        ready_tasks = []
        for task in tasks:
            parent_ids = task_to_parents[task.task_id]
            if all(parent_status_map.get(pid) == "RESOLVED" for pid in parent_ids):
                ready_tasks.append(task)
        return ready_tasks

    def _routing_classifier(self, task: DAGTask) -> PersonaEnum:
        payload = task.task_payload

        if re.search(r"sudo|rm -rf|\.env", payload, re.IGNORECASE):
            return PersonaEnum.ICHIGO

        if not task.parent_task_ids_json == "[]":
            return PersonaEnum.MADARA

        if task.action_tier == ActionTierEnum.CRITICAL.value:
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
        elif task.task_type in ["mvp", "prototype"] and task.action_tier in [ActionTierEnum.TRIVIAL.value, ActionTierEnum.STANDARD.value]:
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
