from sqlmodel import Field, SQLModel, create_engine, Session, text
from typing import Optional
import os
import uuid

class Anchor(SQLModel, table=True):
    __tablename__ = "anchors"
    id: Optional[int] = Field(default=None, primary_key=True)
    constraint_text: str

class DAGTask(SQLModel, table=True):
    __tablename__ = "tasks"
    task_id: str = Field(primary_key=True)
    status: str
    assigned_persona: str
    time_started: float
    max_ttl: int
    parent_task_ids_json: str
    task_payload: str = Field(default="")
    task_type: str = Field(default="standard")
    action_tier: str = Field(default="STANDARD")
    retry_count: int = Field(default=0)
    checkpoint_hash: Optional[str] = None

class ExecutionSnapshot(SQLModel, table=True):
    __tablename__ = "snapshots"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    snapshot_hash: str = Field(index=True)
    target_scope: str
    blobs_json: str

class ExecutionLog(SQLModel, table=True):
    __tablename__ = "execution_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str
    pre_checksum: str
    post_checksum: str
    status: str
    persona_executed: Optional[str] = None
    rollback_status: Optional[str] = None

db_url = os.getenv("DB_URL", "sqlite:///database.db")
engine = create_engine(db_url, connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    if db_url.startswith("sqlite"):
        with engine.connect() as con:
            con.execute(text("PRAGMA journal_mode=WAL;"))

def get_session():
    with Session(engine) as session:
        yield session
