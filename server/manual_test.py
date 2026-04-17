import os
os.environ["MOCK_RESPONSE"] = "Custom mock response for testing!"

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("Testing Mock LLM Server...")
print("=" * 50)

# Test 1: Root endpoint
print("\n1. Testing root endpoint...")
response = client.get("/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 2: Chat completions with default response
print("\n2. Testing chat completions with default response...")
response = client.post(
    "/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 3: Chat completions with custom MOCK_RESPONSE
print("\n3. Testing chat completions with custom MOCK_RESPONSE...")
response = client.post(
    "/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "What is the weather?"}
        ]
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 4: Empty messages (should fail)
print("\n4. Testing empty messages (should fail)...")
response = client.post(
    "/v1/chat/completions",
    json={
        "messages": []
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\n" + "=" * 50)
print("All tests completed!")