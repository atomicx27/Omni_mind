from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
from typing import Dict, Any
from sqlmodel import select
from core.db import get_session, DAGTask
import json

app = FastAPI(title="Sovereign AGI API")

async def event_generator(request: Request):
    while True:
        if await request.is_disconnected():
            break

        session_gen = get_session()
        try:
            db = next(session_gen)
            tasks = db.exec(select(DAGTask)).all()

            task_list = []
            for task in tasks:
                task_list.append({
                    "task_id": task.task_id,
                    "status": task.status,
                    "assigned_persona": task.assigned_persona
                })

            yield f"data: {json.dumps({'type': 'task.update', 'tasks': task_list})}\n\n"
        except StopIteration:
            pass
        finally:
            try:
                next(session_gen) # Ensure cleanup
            except StopIteration:
                pass

        await asyncio.sleep(1)

@app.get("/events")
async def sse_events(request: Request):
    return StreamingResponse(event_generator(request), media_type="text/event-stream")

@app.post("/kill")
async def kill_switch():
    # In a full implementation, this would signal the watchdog or orchestrator to halt
    return {"status": "kill_signal_sent", "message": "System shutdown initiated"}

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "healthy"}
