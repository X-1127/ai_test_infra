from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


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


class HealthResponse(BaseModel):
    status: str


class RootResponse(BaseModel):
    status: str
    message: str
    endpoints: dict


class DelayConfig(BaseModel):
    enabled: bool = False
    min_delay_ms: int = 0
    max_delay_ms: int = 1000


class FaultConfig(BaseModel):
    enabled: bool = False
    fault_type: str = Field(default="none", pattern="^(none|http_error|timeout|invalid_response|empty_response)$")
    http_status_code: int = 500
    error_message: str = "Internal server error"
    probability: float = Field(default=1.0, ge=0.0, le=1.0)


class InjectionConfig(BaseModel):
    delay: DelayConfig = Field(default_factory=DelayConfig)
    fault: FaultConfig = Field(default_factory=FaultConfig)


class ConfigUpdateRequest(BaseModel):
    delay: Optional[DelayConfig] = None
    fault: Optional[FaultConfig] = None


class ConfigResponse(BaseModel):
    delay: DelayConfig
    fault: FaultConfig


class ResponseRule(BaseModel):
    trigger: str
    response: str
    match_type: str = Field(default="contains", pattern="^(exact|contains|regex)$")
    enabled: bool = True


class ResponseConfig(BaseModel):
    default_response: str = "这是一个模拟响应。"
    rules: List[ResponseRule] = []
    metadata: Dict[str, Any] = {}


class YAMLConfigStatus(BaseModel):
    enabled: bool
    config: ResponseConfig