import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("Testing Mock LLM Server...")
print("=" * 60)

# Test 1: Basic chat completion
print("\n1. Testing basic chat completion...")
response = client.post(
    "/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ID: {data['id']}")
    print(f"   Object: {data['object']}")
    print(f"   Model: {data['model']}")
    print(f"   Content: {data['choices'][0]['message']['content']}")
    print(f"   Finish Reason: {data['choices'][0]['finish_reason']}")
    print("   [PASS]")
else:
    print(f"   [FAIL] {response.text}")

# Test 2: Multiple messages
print("\n2. Testing multiple messages...")
response = client.post(
    "/v1/chat/completions",
    json={
        "messages": [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "How are you?"}
        ]
    }
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print("   [PASS]")
else:
    print(f"   [FAIL] {response.text}")

# Test 3: Custom model
print("\n3. Testing custom model...")
response = client.post(
    "/v1/chat/completions",
    json={
        "messages": [{"role": "user", "content": "Test"}],
        "model": "gpt-4"
    }
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Model: {data['model']}")
    print("   [PASS]")
else:
    print(f"   [FAIL] {response.text}")

# Test 4: Empty messages (should fail)
print("\n4. Testing empty messages (should fail)...")
response = client.post(
    "/v1/chat/completions",
    json={"messages": []}
)
print(f"   Status: {response.status_code}")
if response.status_code == 400:
    print("   [PASS] Correctly rejected empty messages")
else:
    print(f"   [FAIL] Should return 400")

# Test 5: Root endpoint
print("\n5. Testing root endpoint...")
response = client.get("/")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Status: {data['status']}")
    print("   [PASS]")
else:
    print(f"   [FAIL] {response.text}")

# Test 6: Health endpoint
print("\n6. Testing health endpoint...")
response = client.get("/health")
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   Health: {data['status']}")
    print("   [PASS]")
else:
    print(f"   [FAIL] {response.text}")

print("\n" + "=" * 60)
print("All tests completed!")