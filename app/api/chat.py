import time
import random
import asyncio
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi.responses import StreamingResponse
from app.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    ChoiceMessage,
    ConfigUpdateRequest,
    ConfigResponse,
    ResponseRule,
    ResponseConfig,
    YAMLConfigStatus,
    StreamChoice,
    StreamChoiceMessage,
    StreamChatCompletionResponse
)
from app.services.mock_service import MockService
from app.services.log_manager import get_log_manager

router = APIRouter()
mock_service = MockService()
log_manager = get_log_manager()


@router.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest, http_request: Request):
    start_time = time.time()
    client_ip = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get("user-agent")
    
    if not request.messages:
        log_manager.log_request(
            method="POST",
            path="/v1/chat/completions",
            status_code=400,
            duration_ms=(time.time() - start_time) * 1000,
            client_ip=client_ip,
            user_agent=user_agent
        )
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")
    
    await mock_service.apply_delay()
    
    if mock_service.should_inject_fault():
        fault_type, status_code, error_message = mock_service.get_fault_details()
        
        log_manager.log_request(
            method="POST",
            path="/v1/chat/completions",
            status_code=status_code,
            duration_ms=(time.time() - start_time) * 1000,
            client_ip=client_ip,
            user_agent=user_agent,
            body=f"Fault injected: {fault_type}"
        )
        
        if fault_type == "http_error":
            raise HTTPException(status_code=status_code, detail=error_message)
        elif fault_type == "timeout":
            await asyncio.sleep(30)
            raise HTTPException(status_code=504, detail="Gateway timeout")
        elif fault_type == "invalid_response":
            return Response(content='{"invalid": "response structure"}', media_type="application/json")
        elif fault_type == "empty_response":
            if request.stream:
                return StreamingResponse(generate_empty_stream(), media_type="text/event-stream")
            else:
                return ChatCompletionResponse(
                    id=f"mock-{int(time.time())}",
                    created=int(time.time()),
                    model=request.model or "mock-model",
                    choices=[]
                )
    
    timestamp = int(time.time())
    
    if mock_service.get_use_yaml_config() and request.messages:
        last_message = request.messages[-1]
        mock_response_content = mock_service.get_mock_response(last_message.content)
    else:
        mock_response_content = mock_service.get_mock_response()
    
    if request.stream:
        response = StreamingResponse(
            generate_stream(mock_response_content, request.model or "mock-model", timestamp),
            media_type="text/event-stream"
        )
        log_manager.log_request(
            method="POST",
            path="/v1/chat/completions",
            status_code=200,
            duration_ms=(time.time() - start_time) * 1000,
            client_ip=client_ip,
            user_agent=user_agent,
            body=f"Stream response: {len(mock_response_content)} chars"
        )
        return response
    
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
    
    log_manager.log_request(
        method="POST",
        path="/v1/chat/completions",
        status_code=200,
        duration_ms=(time.time() - start_time) * 1000,
        client_ip=client_ip,
        user_agent=user_agent,
        body=f"Response: {len(mock_response_content)} chars"
    )
    
    return response


async def generate_empty_stream():
    yield "data: {\"choices\":[{\"index\":0,\"delta\":{},\"finish_reason\":\"stop\"}]}\n\n"
    yield "data: [DONE]\n\n"


async def generate_stream(content: str, model: str, created: int):
    chunks = split_content(content)
    
    for i, chunk in enumerate(chunks):
        stream_response = StreamChatCompletionResponse(
            id=f"mock-{created}",
            created=created,
            model=model,
            choices=[
                StreamChoice(
                    index=0,
                    delta=StreamChoiceMessage(content=chunk),
                    finish_reason=None
                )
            ]
        )
        yield f"data: {stream_response.model_dump_json()}\n\n"
        await asyncio.sleep(0.05)
    
    final_response = StreamChatCompletionResponse(
        id=f"mock-{created}",
        created=created,
        model=model,
        choices=[
            StreamChoice(
                index=0,
                delta=StreamChoiceMessage(content=""),
                finish_reason="stop"
            )
        ]
    )
    yield f"data: {final_response.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"


def split_content(content: str, chunk_size: int = 10) -> list[str]:
    if not content:
        return []
    return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]


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


@router.get("/v1/config/yaml", response_model=YAMLConfigStatus)
async def get_yaml_config():
    config = mock_service.get_yaml_config()
    return YAMLConfigStatus(
        enabled=mock_service.get_use_yaml_config(),
        config=config.model_dump()
    )


@router.put("/v1/config/yaml/enable")
async def enable_yaml_config():
    mock_service.set_use_yaml_config(True)
    config = mock_service.get_yaml_config()
    return YAMLConfigStatus(
        enabled=True,
        config=config.model_dump()
    )


@router.put("/v1/config/yaml/disable")
async def disable_yaml_config():
    mock_service.set_use_yaml_config(False)
    config = mock_service.get_yaml_config()
    return YAMLConfigStatus(
        enabled=False,
        config=config.model_dump()
    )


@router.post("/v1/config/yaml/reload")
async def reload_yaml_config():
    mock_service.reload_yaml_config()
    config = mock_service.get_yaml_config()
    return YAMLConfigStatus(
        enabled=mock_service.get_use_yaml_config(),
        config=config.model_dump()
    )


@router.post("/v1/config/yaml/rules")
async def add_yaml_rule(rule: ResponseRule):
    mock_service.response_config_manager.add_rule(rule)
    config = mock_service.get_yaml_config()
    return YAMLConfigStatus(
        enabled=mock_service.get_use_yaml_config(),
        config=config.model_dump()
    )


@router.delete("/v1/config/yaml/rules/{index}")
async def delete_yaml_rule(index: int):
    success = mock_service.response_config_manager.remove_rule(index)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    config = mock_service.get_yaml_config()
    return YAMLConfigStatus(
        enabled=mock_service.get_use_yaml_config(),
        config=config.model_dump()
    )


@router.put("/v1/config/yaml/rules/{index}")
async def update_yaml_rule(index: int, rule: ResponseRule):
    success = mock_service.response_config_manager.update_rule(index, rule)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    config = mock_service.get_yaml_config()
    return YAMLConfigStatus(
        enabled=mock_service.get_use_yaml_config(),
        config=config.model_dump()
    )


@router.put("/v1/config/yaml/rules/{index}/enable")
async def enable_yaml_rule(index: int):
    success = mock_service.response_config_manager.enable_rule(index, True)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    config = mock_service.get_yaml_config()
    return YAMLConfigStatus(
        enabled=mock_service.get_use_yaml_config(),
        config=config.model_dump()
    )


@router.put("/v1/config/yaml/rules/{index}/disable")
async def disable_yaml_rule(index: int):
    success = mock_service.response_config_manager.enable_rule(index, False)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    config = mock_service.get_yaml_config()
    return YAMLConfigStatus(
        enabled=mock_service.get_use_yaml_config(),
        config=config.model_dump()
    )


@router.post("/v1/config/yaml/validate")
async def validate_yaml_config(config_data: dict):
    try:
        from app.services.response_config_manager import ResponseConfigManager
        manager = ResponseConfigManager()
        
        if manager._validate_config(config_data):
            return {"valid": True, "message": "é…ç½®éªŒè¯é€šè¿‡"}
        else:
            return {"valid": False, "message": "é…ç½®éªŒè¯å¤±è´¥"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"é…ç½®éªŒè¯é”™è¯¯: {str(e)}")


@router.post("/v1/config/yaml/rules/validate")
async def validate_yaml_rule(rule: ResponseRule):
    try:
        is_valid, message = mock_service.response_config_manager.validate_rule(rule)
        
        if is_valid:
            return {"valid": True, "message": "è§„åˆ™éªŒè¯é€šè¿‡"}
        else:
            return {"valid": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"è§„åˆ™éªŒè¯é”™è¯¯: {str(e)}")


@router.get("/v1/config/yaml/rules/search")
async def search_yaml_rules(keyword: str, match_type: Optional[str] = None):
    try:
        results = mock_service.response_config_manager.search_rules(keyword, match_type)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"è§„åˆ™æœç´¢é”™è¯¯: {str(e)}")