import pytest
import os
import json

# Set environment variable BEFORE importing core.db
os.environ["DB_URL"] = "sqlite:///:memory:"

from core.db import create_db_and_tables, engine, get_session, DAGTask
from agents.madara import MadaraOrchestrator
from sqlmodel import Session
from core.schemas import PersonaEnum, ActionTierEnum

def test_routing_classifier():
    create_db_and_tables()
    with Session(engine) as session:
        orchestrator = MadaraOrchestrator(session)

        # Test 1: Ichigo
        task1 = DAGTask(task_id="t1", status="PENDING", assigned_persona="Madara", time_started=0, max_ttl=60, parent_task_ids_json="[]", task_payload="sudo rm -rf /")
        assert orchestrator._routing_classifier(task1) == PersonaEnum.ICHIGO

        # Test 2: Itachi
        task2 = DAGTask(task_id="t2", status="PENDING", assigned_persona="Madara", time_started=0, max_ttl=60, parent_task_ids_json="[]", task_payload="safe", action_tier=ActionTierEnum.CRITICAL.value)
        assert orchestrator._routing_classifier(task2) == PersonaEnum.ITACHI

        # Test 3: Natsu
        task3 = DAGTask(task_id="t3", status="PENDING", assigned_persona="Madara", time_started=0, max_ttl=60, parent_task_ids_json="[]", task_payload="safe", task_type="mvp", action_tier=ActionTierEnum.STANDARD.value)
        assert orchestrator._routing_classifier(task3) == PersonaEnum.NATSU
