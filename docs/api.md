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
    "health": "/health"
  }
}
```

### 3. Chat Completions

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

### cURL

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'
```

### Python

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

### JavaScript

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