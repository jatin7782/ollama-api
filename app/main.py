import os

import httpx

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434"
)

MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5-coder:1.5b"
)

app = FastAPI(
    title="My Ollama AI API",
    version="1.0.0"
)

# For a simple demo. In production, restrict this to your
# exact GitHub Pages origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)


@app.get("/")
async def root():
    return {
        "status": "online",
        "model": MODEL,
        "service": "Ollama AI API"
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
            "ollama": response.status_code == 200,
            "model": MODEL
        }

    except Exception as e:
        return {
            "status": "error",
            "ollama": False,
            "error": str(e)
        }


@app.post("/chat")
async def chat(request: ChatRequest):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Give clear and accurate answers."
            )
        }
    ]

    for item in request.history:
        role = item.get("role")
        content = item.get("content")

        if role in ["user", "assistant"] and isinstance(content, str):
            messages.append({
                "role": role,
                "content": content
            })

    messages.append({
        "role": "user",
        "content": request.message
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }

    try:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload
            )

        response.raise_for_status()
        data = response.json()

        answer = data.get("message", {}).get("content", "")

        return {
            "success": True,
            "model": MODEL,
            "answer": answer
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
