# API Documentation

## Overview

Mock LLM Server provides a mock implementation of the OpenAI Chat Completions API for testing purposes.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the server is running.

**Response:**
```json
{
  "status": "healthy"
}
```

### 2. Root Endpoint

**GET** `/`

Get server information and available endpoints.

**Response:**
```json
{
  "status": "ok",
  "message": "Mock LLM Server is running",
  "endpoints": {
    "chat_completions": "/v1/chat/completions",
    "get_injection_config": "/v1/config/injection",
    "update_injection_config": "/v1/config/injection",
    "reset_injection_config": "/v1/config/injection/reset",
    "health": "/health"
  }
}
```

### 3. Get Injection Configuration

**GET** `/v1/config/injection`

Get current delay and fault injection configuration.

**Response:**
```json
{
  "delay": {
    "enabled": false,
    "min_delay_ms": 0,
    "max_delay_ms": 1000
  },
  "fault": {
    "enabled": false,
    "fault_type": "none",
    "http_status_code": 500,
    "error_message": "Internal server error",
    "probability": 1.0
  }
}
```

### 4. Update Injection Configuration

**PUT** `/v1/config/injection`

Update delay and/or fault injection configuration.

**Request Body:**
```json
{
  "delay": {
    "enabled": true,
    "min_delay_ms": 100,
    "max_delay_ms": 500
  },
  "fault": {
    "enabled": true,
    "fault_type": "http_error",
    "http_status_code": 503,
    "error_message": "Service unavailable",
    "probability": 0.5
  }
}
```

**Parameters:**
- `delay` (optional): Delay injection configuration
  - `enabled`: Enable/disable delay injection
  - `min_delay_ms`: Minimum delay in milliseconds
  - `max_delay_ms`: Maximum delay in milliseconds
- `fault` (optional): Fault injection configuration
  - `enabled`: Enable/disable fault injection
  - `fault_type`: Type of fault to inject ("none", "http_error", "timeout", "invalid_response", "empty_response")
  - `http_status_code`: HTTP status code for http_error type
  - `error_message`: Error message for http_error type
  - `probability`: Probability of fault injection (0.0 to 1.0)

**Response:**
```json
{
  "delay": {
    "enabled": true,
    "min_delay_ms": 100,
    "max_delay_ms": 500
  },
  "fault": {
    "enabled": true,
    "fault_type": "http_error",
    "http_status_code": 503,
    "error_message": "Service unavailable",
    "probability": 0.5
  }
}
```

### 5. Reset Injection Configuration

**POST** `/v1/config/injection/reset`

Reset all injection configurations to default values.

**Response:**
```json
{
  "delay": {
    "enabled": false,
    "min_delay_ms": 0,
    "max_delay_ms": 1000
  },
  "fault": {
    "enabled": false,
    "fault_type": "none",
    "http_status_code": 500,
    "error_message": "Internal server error",
    "probability": 1.0
  }
}
```

### 6. Chat Completions

**POST** `/v1/chat/completions`

Generate mock chat completions.

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ],
  "model": "mock-model",
  "temperature": 1.0,
  "max_tokens": 100
}
```

**Parameters:**
- `messages` (required): Array of message objects
  - `role`: Message role ("system", "user", "assistant")
  - `content`: Message content
- `model` (optional): Model identifier (default: "mock-model")
- `temperature` (optional): Sampling temperature (default: 1.0)
- `max_tokens` (optional): Maximum tokens to generate (default: 100)

**Response:**
```json
{
  "id": "mock-1234567890",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "mock-model",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "This is a mock response."
      },
      "finish_reason": "stop"
    }
  ]
}
```

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Messages list cannot be empty"
}
```

## Configuration

The server can be configured using environment variables:

- `MOCK_RESPONSE`: Custom mock response text
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)
- `DEBUG`: Enable debug mode (default: false)

## Example Usage

### Basic Chat Completion

#### cURL

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'
```

#### Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }
)

print(response.json())
```

#### JavaScript

```javascript
fetch('http://localhost:8000/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Hello' }
    ]
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### Delay Injection

#### Enable Delay Injection

```bash
curl -X PUT http://localhost:8000/v1/config/injection \
  -H "Content-Type: application/json" \
  -d '{
    "delay": {
      "enabled": true,
      "min_delay_ms": 100,
      "max_delay_ms": 500
    }
  }'
```

#### Python Example with Delay

```python
import httpx
import time

# Enable delay injection
httpx.put(
    "http://localhost:8000/v1/config/injection",
    json={
        "delay": {
            "enabled": True,
            "min_delay_ms": 100,
            "max_delay_ms": 500
        }
    }
)

# Make request with delay
start_time = time.time()
response = httpx.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }
)
end_time = time.time()

print(f"Response: {response.json()}")
print(f"Delay: {(end_time - start_time) * 1000:.0f}ms")
```

### Fault Injection

#### Enable HTTP Error Fault

```bash
curl -X PUT http://localhost:8000/v1/config/injection \
  -H "Content-Type: application/json" \
  -d '{
    "fault": {
      "enabled": true,
      "fault_type": "http_error",
      "http_status_code": 503,
      "error_message": "Service unavailable",
      "probability": 1.0
    }
  }'
```

#### Enable Timeout Fault

```bash
curl -X PUT http://localhost:8000/v1/config/injection \
  -H "Content-Type: application/json" \
  -d '{
    "fault": {
      "enabled": true,
      "fault_type": "timeout",
      "probability": 0.5
    }
  }'
```

#### Enable Invalid Response Fault

```bash
curl -X PUT http://localhost:8000/v1/config/injection \
  -H "Content-Type: application/json" \
  -d '{
    "fault": {
      "enabled": true,
      "fault_type": "invalid_response",
      "probability": 0.3
    }
  }'
```

#### Enable Empty Response Fault

```bash
curl -X PUT http://localhost:8000/v1/config/injection \
  -H "Content-Type: application/json" \
  -d '{
    "fault": {
      "enabled": true,
      "fault_type": "empty_response",
      "probability": 0.2
    }
  }'
```

### Combined Delay and Fault Injection

```bash
curl -X PUT http://localhost:8000/v1/config/injection \
  -H "Content-Type: application/json" \
  -d '{
    "delay": {
      "enabled": true,
      "min_delay_ms": 200,
      "max_delay_ms": 1000
    },
    "fault": {
      "enabled": true,
      "fault_type": "http_error",
      "http_status_code": 500,
      "error_message": "Internal server error",
      "probability": 0.3
    }
  }'
```

### Reset Configuration

```bash
curl -X POST http://localhost:8000/v1/config/injection/reset
```

### Python Testing with Fault Injection

```python
import httpx
import random

# Configure fault injection with 30% probability
httpx.put(
    "http://localhost:8000/v1/config/injection",
    json={
        "fault": {
            "enabled": True,
            "fault_type": "http_error",
            "http_status_code": 503,
            "error_message": "Service unavailable",
            "probability": 0.3
        }
    }
)

# Make multiple requests to test fault handling
for i in range(10):
    try:
        response = httpx.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": f"Request {i+1}"}
                ]
            }
        )
        print(f"Request {i+1}: Success - {response.json()}")
    except httpx.HTTPStatusError as e:
        print(f"Request {i+1}: Failed - {e.response.status_code} - {e.response.text}")
```