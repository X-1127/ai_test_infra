import os
import sys
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.dirname(__file__))

from main import app

client = TestClient(app)

print("Quick Test of Mock LLM Server")
print("=" * 50)

# Test 1: Basic chat completion
print("\nTest 1: Basic chat completion")
response = client.post(
    "/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }
)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Response ID: {data['id']}")
    print(f"Object: {data['object']}")
    print(f"Content: {data['choices'][0]['message']['content']}")
    print("✓ Test passed!")
else:
    print(f"✗ Test failed: {response.text}")

# Test 2: Root endpoint
print("\nTest 2: Root endpoint")
response = client.get("/")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Status: {data['status']}")
    print("✓ Test passed!")
else:
    print(f"✗ Test failed: {response.text}")

# Test 3: Health check
print("\nTest 3: Health check")
response = client.get("/health")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Health: {data['status']}")
    print("✓ Test passed!")
else:
    print(f"✗ Test failed: {response.text}")

print("\n" + "=" * 50)
print("Quick test completed!")