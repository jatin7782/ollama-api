import os
import httpx

from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .auth import verify_api_key

app = FastAPI(
    title="My Ollama API",
    version="1.0.0"
)

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434"
)

DEFAULT_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5-coder:1.5b"
)


class ChatRequest(BaseModel):
    model: str | None = None
    messages: list
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None


@app.get("/")
async def root():
    return {
        "name": "My Ollama API",
        "status": "online"
    }


@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(
                f"{OLLAMA_URL}/api/tags"
            )

        return {
            "status": "ok",
            "ollama": response.status_code == 200
        }

    except Exception as e:
        return {
            "status": "error",
            "ollama": False,
            "error": str(e)
        }


@app.get("/v1/models")
async def models(
    _: bool = Depends(verify_api_key)
):
    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{OLLAMA_URL}/v1/models"
        )

    return response.json()


@app.post("/v1/chat/completions")
async def chat(
    request: ChatRequest,
    _: bool = Depends(verify_api_key)
):

    model = request.model or DEFAULT_MODEL

    payload = {
        "model": model,
        "messages": request.messages,
        "stream": request.stream
    }

    if request.temperature is not None:
        payload["temperature"] = request.temperature

    if request.max_tokens is not None:
        payload["max_tokens"] = request.max_tokens

    if request.stream:

        async def generate():

            async with httpx.AsyncClient() as client:

                async with client.stream(
                    "POST",
                    f"{OLLAMA_URL}/v1/chat/completions",
                    json=payload,
                    timeout=None
                ) as response:

                    async for chunk in response.aiter_bytes():
                        yield chunk

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    async with httpx.AsyncClient(timeout=None) as client:

        response = await client.post(
            f"{OLLAMA_URL}/v1/chat/completions",
            json=payload
        )

    return response.json()