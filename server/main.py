import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

app = FastAPI(title="Mock LLM Server", version="1.0.0")

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "mock-model"
    temperature: Optional[float] = 1.0
    max_tokens: Optional[int] = 100

class ChoiceMessage(BaseModel):
    role: str = "assistant"
    content: str

class Choice(BaseModel):
    index: int = 0
    message: ChoiceMessage
    finish_reason: str = "stop"

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]

def get_mock_response() -> str:
    return os.getenv("MOCK_RESPONSE", "This is a mock response.")

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")
    
    import time
    timestamp = int(time.time())
    mock_response_content = get_mock_response()
    
    response = ChatCompletionResponse(
        id=f"mock-{timestamp}",
        created=timestamp,
        model=request.model or "mock-model",
        choices=[
            Choice(
                index=0,
                message=ChoiceMessage(content=mock_response_content),
                finish_reason="stop"
            )
        ]
    )
    
    return response

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Mock LLM Server is running",
        "endpoints": {
            "chat_completions": "/v1/chat/completions"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)