# Mock LLM Server

一个简单的 Mock LLM 服务器，模拟 OpenAI Chat Completion API。

## 功能特性

- 完全兼容 OpenAI Chat Completion API 格式
- 支持自定义响应内容（通过环境变量）
- 简单易用，适合测试和开发

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务器

### 默认方式运行

```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动。

### 自定义端口和主机

```bash
# Windows
set PORT=3000
set HOST=127.0.0.1
python main.py

# Linux/Mac
export PORT=3000
export HOST=127.0.0.1
python main.py
```

### 自定义响应内容

```bash
# Windows
set MOCK_RESPONSE=This is a custom response!
python main.py

# Linux/Mac
export MOCK_RESPONSE="This is a custom response!"
python main.py
```

## API 接口

### POST /v1/chat/completions

模拟 OpenAI Chat Completion API。

**请求示例：**

```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

**响应示例：**

```json
{
  "id": "mock-1713456789",
  "object": "chat.completion",
  "created": 1713456789,
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

### GET /

服务器状态信息。

**响应示例：**

```json
{
  "status": "ok",
  "message": "Mock LLM Server is running",
  "endpoints": {
    "chat_completions": "/v1/chat/completions"
  }
}
```

### GET /health

健康检查端点。

**响应示例：**

```json
{
  "status": "healthy"
}
```

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `MOCK_RESPONSE` | 自定义的响应内容 | "This is a mock response." |
| `PORT` | 服务器端口 | 8000 |
| `HOST` | 服务器主机 | "0.0.0.0" |

## 测试

### 运行单元测试

```bash
pytest test_main.py -v
```

### 运行手动测试

```bash
python manual_test.py
```

## 项目结构

```
llm-mock-server/
├── main.py              # 主应用程序
├── test_main.py         # 单元测试
├── manual_test.py       # 手动测试脚本
├── requirements.txt     # 依赖列表
└── README.md           # 项目文档
```

## 使用示例

### Python 客户端

```python
import httpx

async def chat_with_mock():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "Hello!"}
                ]
            }
        )
        result = response.json()
        print(result["choices"][0]["message"]["content"])

# 运行
import asyncio
asyncio.run(chat_with_mock())
```

### JavaScript/Node.js 客户端

```javascript
const response = await fetch('http://localhost:8000/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    messages: [
      { role: 'user', content: 'Hello!' }
    ]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

## 许可证

MIT License