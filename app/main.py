from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from .router import SmartRouter
from .db import db
from .memory import memory
import structlog

app = FastAPI(title="OpenMemoryRouter", version="2.0-Phase2")
router = SmartRouter()
logger = structlog.get_logger()

@app.on_event("startup")
async def startup():
    await db.connect()
    await db.execute("""
        CREATE TABLE IF NOT EXISTS route_memory (
            prompt_hash TEXT PRIMARY KEY,
            best_provider TEXT,
            best_model TEXT,
            energy_score FLOAT,
            success_count INTEGER DEFAULT 1,
            failure_count INTEGER DEFAULT 0,
            last_used TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            request_id TEXT,
            rating INTEGER,
            accepted BOOLEAN,
            notes TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    headers = dict(request.headers)
    try:
        response = await router.route(body, headers)
        if isinstance(response, dict):
            return response
        else:
            async def stream_generator():
                async for chunk in response:
                    yield f"data: {chunk.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(stream_generator(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(status_code=500, content={"error": {"message": str(e), "type": "internal_error"}})

@app.post("/v1/feedback")
async def submit_feedback(request: Request):
    data = await request.json()
    await memory.record_feedback(
        data.get("request_id", "unknown"),
        data.get("rating", 5),
        data.get("accepted", True),
        data.get("notes", "")
    )
    # TODO Phase 3: Update EBM weights from feedback
    return {"status": "success", "message": "Feedback recorded. Thank you! The system will learn from this."}

@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": [{"id": "openai/gpt-4o-mini", "object": "model", "created": 1677610602}]}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "2.0-Phase2",
        "features": ["postgres", "memory", "feedback", "ebm_forecasting", "multi_layer_cache", "streaming", "openai_compatible"]
    }