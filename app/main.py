from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from .router import SmartRouter
import structlog

app = FastAPI(title="OpenMemoryRouter", version="1.0")
router = SmartRouter()
logger = structlog.get_logger()

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    headers = dict(request.headers)
    try:
        response = await router.route(body, headers)
        if isinstance(response, dict):
            return response
        else:
            # Streaming
            async def stream_generator():
                async for chunk in response:
                    yield f"data: {chunk.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(stream_generator(), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/v1/models")
async def list_models():
    # Placeholder - in full version would list from providers
    return {"object": "list", "data": [{"id": "openai/gpt-4o-mini", "object": "model"}]}

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0", "features": ["caching", "ebm", "forecasting", "streaming"]}