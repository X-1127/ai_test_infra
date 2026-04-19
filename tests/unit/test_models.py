import pytest
from app.models import (
    Message,
    ChatCompletionRequest,
    ChoiceMessage,
    Choice,
    ChatCompletionResponse,
    HealthResponse,
    RootResponse
)


class TestModels:
    def test_message_model(self):
        message = Message(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"
    
    def test_chat_completion_request_default_values(self):
        request = ChatCompletionRequest(messages=[Message(role="user", content="Hello")])
        assert request.model == "mock-model"
        assert request.temperature == 1.0
        assert request.max_tokens == 100
    
    def test_chat_completion_request_custom_values(self):
        request = ChatCompletionRequest(
            messages=[Message(role="user", content="Hello")],
            model="gpt-4",
            temperature=0.7,
            max_tokens=200
        )
        assert request.model == "gpt-4"
        assert request.temperature == 0.7
        assert request.max_tokens == 200
    
    def test_choice_message_default_role(self):
        choice_message = ChoiceMessage(content="Response")
        assert choice_message.role == "assistant"
    
    def test_choice_default_values(self):
        choice = Choice(message=ChoiceMessage(content="Response"))
        assert choice.index == 0
        assert choice.finish_reason == "stop"
    
    def test_chat_completion_response_structure(self):
        response = ChatCompletionResponse(
            id="test-id",
            created=1234567890,
            model="mock-model",
            choices=[Choice(message=ChoiceMessage(content="Response"))]
        )
        assert response.id == "test-id"
        assert response.object == "chat.completion"
        assert response.created == 1234567890
        assert response.model == "mock-model"
        assert len(response.choices) == 1
    
    def test_health_response(self):
        response = HealthResponse(status="healthy")
        assert response.status == "healthy"
    
    def test_root_response(self):
        response = RootResponse(
            status="ok",
            message="Test",
            endpoints={"test": "/test"}
        )
        assert response.status == "ok"
        assert response.message == "Test"
        assert response.endpoints == {"test": "/test"}