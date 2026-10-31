from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx

app = FastAPI(title="MyAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

AI_GATEWAY_URL = "https://ai-gateway.vercel.sh/v1/chat/completions"
AI_GATEWAY_API_KEY = os.getenv("AI_GATEWAY_API_KEY")

MODEL = os.getenv(
    "AI_MODEL",
    "reflection/beam-free"
)


class ChatRequest(BaseModel):
    message: str
    history: list = []


@app.get("/")
async def root():
    return {
        "status": "online",
        "model": MODEL
    }


@app.get("/health")
async def health():
    return {
        "status": "online",
        "model": MODEL,
        "gateway_configured": bool(AI_GATEWAY_API_KEY)
    }


@app.post("/chat")
async def chat(request: ChatRequest):

    if not AI_GATEWAY_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="AI_GATEWAY_API_KEY is not configured"
        )

    messages = []

    for item in request.history:
        if item.get("role") in ["user", "assistant"]:
            messages.append({
                "role": item["role"],
                "content": item["content"]
            })

    messages.append({
        "role": "user",
        "content": request.message
    })

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {AI_GATEWAY_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                AI_GATEWAY_URL,
                headers=headers,
                json=payload
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        data = response.json()

        answer = data["choices"][0]["message"]["content"]

        return {
            "answer": answer,
            "model": MODEL
        }

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI Gateway connection failed: {str(e)}"
        )