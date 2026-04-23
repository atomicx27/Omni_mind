import time
import json
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

    def route_task(self, task: DAGTask) -> AgentResult:
        system_prompt = "You are Madara, the DAG Orchestrator. Route tasks to the correct persona."
        prompt = f"Task ID: {task.task_id}\nAssigned Persona: {task.assigned_persona}\nDecide routing."

        response_str = self.proxy.generate_completion(model="llama3", prompt=prompt, system_prompt=system_prompt)

        try:
            parsed = json.loads(response_str)
            return AgentResult(**parsed)
        except Exception as e:
            return AgentResult(
                task_id=task.task_id,
                persona=self.persona,
                action_tier=ActionTierEnum.STANDARD,
                action_type=ActionTypeEnum.SHELL_EXEC,
                target="orchestration",
                payload={"action": "route_task", "task": task.task_id},
                uncertainty_flags=["Failed to parse LLM response"],
                requires_human=False,
                handoff_to=PersonaEnum(task.assigned_persona) if task.assigned_persona else None
            )
