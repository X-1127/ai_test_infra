import time
import random
import asyncio
from fastapi import APIRouter, HTTPException, Response
from app.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    ChoiceMessage,
    ConfigUpdateRequest,
    ConfigResponse
)
from app.services.mock_service import MockService

router = APIRouter()
mock_service = MockService()


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")
    
    await mock_service.apply_delay()
    
    if mock_service.should_inject_fault():
        fault_type, status_code, error_message = mock_service.get_fault_details()
        
        if fault_type == "http_error":
            raise HTTPException(status_code=status_code, detail=error_message)
        elif fault_type == "timeout":
            await asyncio.sleep(30)
            raise HTTPException(status_code=504, detail="Gateway timeout")
        elif fault_type == "invalid_response":
            return Response(content='{"invalid": "response structure"}', media_type="application/json")
        elif fault_type == "empty_response":
            return ChatCompletionResponse(
                id=f"mock-{int(time.time())}",
                created=int(time.time()),
                model=request.model or "mock-model",
                choices=[]
            )
    
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


@router.get("/v1/config/injection", response_model=ConfigResponse)
async def get_injection_config():
    return ConfigResponse(
        delay=mock_service.get_delay_config(),
        fault=mock_service.get_fault_config()
    )


@router.put("/v1/config/injection", response_model=ConfigResponse)
async def update_injection_config(request: ConfigUpdateRequest):
    if request.delay:
        mock_service.update_delay_config(request.delay)
    if request.fault:
        mock_service.update_fault_config(request.fault)
    
    return ConfigResponse(
        delay=mock_service.get_delay_config(),
        fault=mock_service.get_fault_config()
    )


@router.post("/v1/config/injection/reset")
async def reset_injection_config():
    from app.models import DelayConfig, FaultConfig
    mock_service.update_delay_config(DelayConfig())
    mock_service.update_fault_config(FaultConfig())
    
    return ConfigResponse(
        delay=mock_service.get_delay_config(),
        fault=mock_service.get_fault_config()
    )