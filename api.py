from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
from typing import Dict, Any

app = FastAPI(title="Sovereign AGI API")

async def event_generator():
    while True:
        await asyncio.sleep(1)
        yield f"data: {{\"status\": \"polling\"}}\n\n"

@app.get("/events")
async def sse_events():
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "healthy"}
