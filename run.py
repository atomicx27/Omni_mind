from core.db import create_db_and_tables, engine, get_session
from core.watchdog import TTLWatchdog
from core.memory import FailureMemory
from core.proxy import LLMProviderProxy
from agents.madara import MadaraOrchestrator
import time
import os

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
                    result = orchestrator.route_task(task)
                    print(f"Routing result: {result}")

                    task.status = "RESOLVED"
                    db_session.add(task)
                db_session.commit()

            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        watchdog.stop()

if __name__ == "__main__":
    main()
