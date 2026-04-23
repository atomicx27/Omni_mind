from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
from typing import Dict, Any
from sqlmodel import select, Session
from core.db import engine, DAGTask
import json

app = FastAPI(title="Sovereign AGI API")

async def event_generator(request: Request):
    while True:
        if await request.is_disconnected():
            break

        with Session(engine) as db:
            tasks = db.exec(select(DAGTask)).all()

            task_list = []
            for task in tasks:
                task_list.append({
                    "task_id": task.task_id,
                    "status": task.status,
                    "assigned_persona": task.assigned_persona
                })

            yield f"data: {json.dumps({'type': 'task.update', 'tasks': task_list})}\n\n"

        await asyncio.sleep(1)

@app.get("/events")
async def sse_events(request: Request):
    return StreamingResponse(event_generator(request), media_type="text/event-stream")

@app.post("/kill")
async def kill_switch():
    return {"status": "kill_signal_sent", "message": "System shutdown initiated"}

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "healthy"}
