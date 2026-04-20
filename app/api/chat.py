import time
import random
import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, Response
from app.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Choice,
    ChoiceMessage,
    ConfigUpdateRequest,
    ConfigResponse,
    ResponseRule,
    ResponseConfig,
    YAMLConfigStatus
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
    
    if mock_service.get_use_yaml_config() and request.messages:
        last_message = request.messages[-1]
        mock_response_content = mock_service.get_mock_response(last_message.content)
    else:
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
            return {"valid": True, "message": "配置验证通过"}
        else:
            return {"valid": False, "message": "配置验证失败"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"配置验证错误: {str(e)}")


@router.post("/v1/config/yaml/rules/validate")
async def validate_yaml_rule(rule: ResponseRule):
    try:
        is_valid, message = mock_service.response_config_manager.validate_rule(rule)
        
        if is_valid:
            return {"valid": True, "message": "规则验证通过"}
        else:
            return {"valid": False, "message": message}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"规则验证错误: {str(e)}")


@router.get("/v1/config/yaml/rules/search")
async def search_yaml_rules(keyword: str, match_type: Optional[str] = None):
    try:
        results = mock_service.response_config_manager.search_rules(keyword, match_type)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"规则搜索错误: {str(e)}")