import pytest
import os
import uuid

# Set environment variable BEFORE importing core.db
os.environ["DB_URL"] = "sqlite:///:memory:"

from core.db import create_db_and_tables, engine, get_session, DAGTask
from sqlmodel import Session, select

def test_db_creation():
    create_db_and_tables()
    with Session(engine) as session:
        task_id = str(uuid.uuid4())
        task = DAGTask(task_id=task_id, status="PENDING", assigned_persona="Madara", time_started=0.0, max_ttl=60, parent_task_ids_json="[]")
        session.add(task)
        session.commit()

        result = session.exec(select(DAGTask).where(DAGTask.task_id == task_id)).all()
        assert len(result) == 1
        assert result[0].task_id == task_id
