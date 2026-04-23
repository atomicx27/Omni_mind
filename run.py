from core.db import create_db_and_tables, engine, get_session, DAGTask
from core.watchdog import TTLWatchdog
from core.memory import FailureMemory
from core.proxy import LLMProviderProxy
from agents.madara import MadaraOrchestrator
from sqlmodel import Session
import time
import os

def handle_timeout(task_id: str):
    print(f"Task {task_id} timed out.")

    with Session(engine) as db_session:
        task = db_session.get(DAGTask, task_id)

        if task:
            retries = task.retry_count
            if retries >= 3:
                print(f"Task {task_id} exceeded max retries. Escalating to human.")
                task.status = "ESCALATED"
            else:
                print(f"Re-queuing task {task_id}. Retry {retries + 1}/3")
                task.status = "NEEDS_REROUTE"
                task.retry_count = retries + 1

            db_session.add(task)
            db_session.commit()

def main():
    print("Initializing Sovereign AGI Version 2.0 Framework...")

    print("Setting up persistence engine (SQLite with WAL)...")
    create_db_and_tables()

    print("Connecting to ChromaDB failure memory...")
    memory = FailureMemory()

    print("Connecting to Redis rate limit proxy...")
    proxy = LLMProviderProxy()

    print("Starting execution watchdog daemon...")
    watchdog = TTLWatchdog()
    watchdog.start()

    print("Initialization complete. AGI Framework is ready.")

    session_generator = get_session()
    db_session = next(session_generator)
    orchestrator = MadaraOrchestrator(db_session)

    print("Starting polling loop...")
    try:
        while True:
            ready_tasks = orchestrator.poll_tasks()
            if ready_tasks:
                for task in ready_tasks:
                    print(f"Task {task.task_id} is ready for processing.")

                    if task.max_ttl > 0:
                         watchdog.register_task(task.task_id, task.max_ttl, handle_timeout)

                    result = orchestrator.route_task(task)
                    print(f"Routing result: {result}")

                    task.status = "RESOLVED"
                    db_session.add(task)

                    if task.max_ttl > 0:
                        watchdog.complete_task(task.task_id)

                db_session.commit()

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        watchdog.stop()

if __name__ == "__main__":
    main()
