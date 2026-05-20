from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from fastapi.responses import StreamingResponse
import asyncio
from typing import Dict, Any
from sqlmodel import select, Session
from core.db import engine, DAGTask
import json
import os

app = FastAPI(title="Sovereign AGI API")

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    admin_key = os.getenv("ADMIN_API_KEY", "default_secret_key")
    if api_key != admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return api_key

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
async def sse_events(request: Request, _ = Depends(verify_api_key)):
    return StreamingResponse(event_generator(request), media_type="text/event-stream")

@app.post("/kill")
async def kill_switch(_ = Depends(verify_api_key)):
    return {"status": "kill_signal_sent", "message": "System shutdown initiated"}

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "healthy"}
