import time
from fastapi import APIRouter, HTTPException
from app.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    ChoiceMessage
)
from app.services.mock_service import MockService

router = APIRouter()
mock_service = MockService()


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")
    
    timestamp = int(time.time())
    mock_response_content = mock_service.get_mock_response()
    
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