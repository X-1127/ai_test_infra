import httpx
import asyncio

async def test_mock_server():
    base_url = "http://localhost:8000"
    
    print("Testing Mock LLM Server")
    print("=" * 60)
    
    # Test 1: Simple chat completion
    print("\n1. Simple chat completion:")
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
        print(f"Response: {result['choices'][0]['message']['content']}")
    
    # Test 2: Multi-turn conversation
    print("\n2. Multi-turn conversation:")
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
        print(f"Response: {result['choices'][0]['message']['content']}")
    
    # Test 3: With custom model
    print("\n3. With custom model:")
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
        print(f"Model: {result['model']}")
        print(f"Response: {result['choices'][0]['message']['content']}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    try:
        asyncio.run(test_mock_server())
    except httpx.ConnectError:
        print("Error: Could not connect to the server.")
        print("Please make sure the server is running on http://localhost:8000")
        print("Run: python main.py")