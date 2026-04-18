import pytest
import httpx

@pytest.mark.asyncio
class TestClientIntegration:
    async def test_simple_chat_completion(self, base_url):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "user", "content": "Hello, how are you?"}
                    ]
                }
            )
            result = response.json()
            assert response.status_code == 200
            assert "choices" in result
            assert len(result["choices"]) == 1

    async def test_multi_turn_conversation(self, base_url):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "What is 2+2?"},
                        {"role": "assistant", "content": "2+2 equals 4."},
                        {"role": "user", "content": "What about 3+3?"}
                    ]
                }
            )
            result = response.json()
            assert response.status_code == 200
            assert result["choices"][0]["message"]["role"] == "assistant"

    async def test_custom_model(self, base_url):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "user", "content": "Test"}
                    ],
                    "model": "gpt-4-turbo"
                }
            )
            result = response.json()
            assert response.status_code == 200
            assert result["model"] == "gpt-4-turbo"