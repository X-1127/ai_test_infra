# API 文档

## 概述

Mock LLM Server 提供了 OpenAI 聊天完成 API 的模拟实现，专门用于测试目的。支持流式响应、延迟注入、故障注入、日志记录等功能。

## 基础 URL

```
http://localhost:8000
```

## API 端点

### 1. 健康检查

**GET** `/health`

检查服务器是否正常运行。

**响应示例:**
```json
{
  "status": "healthy"
}
```

### 2. 根路径端点

**GET** `/`

获取服务器信息和可用的端点列表。

**响应示例:**
```json
{
  "status": "ok",
  "message": "Mock LLM Server is running",
  "endpoints": {
    "chat_completions": "/v1/chat/completions",
    "get_injection_config": "/v1/config/injection",
    "update_injection_config": "/v1/config/injection",
    "reset_injection_config": "/v1/config/injection/reset",
    "get_yaml_config": "/v1/config/yaml",
    "enable_yaml_config": "/v1/config/yaml/enable",
    "disable_yaml_config": "/v1/config/yaml/disable",
    "reload_yaml_config": "/v1/config/yaml/reload",
    "validate_yaml_config": "/v1/config/yaml/validate",
    "add_yaml_rule": "/v1/config/yaml/rules",
    "delete_yaml_rule": "/v1/config/yaml/rules/{index}",
    "update_yaml_rule": "/v1/config/yaml/rules/{index}",
    "enable_yaml_rule": "/v1/config/yaml/rules/{index}/enable",
    "disable_yaml_rule": "/v1/config/yaml/rules/{index}/disable",
    "validate_yaml_rule": "/v1/config/yaml/rules/validate",
    "search_yaml_rules": "/v1/config/yaml/rules/search",
    "get_logs": "/v1/logs",
    "query_logs": "/v1/logs/query",
    "search_logs": "/v1/logs/search",
    "get_log_stats": "/v1/logs/stats",
    "clear_logs": "/v1/logs",
    "get_log_file_path": "/v1/logs/file/{log_type}",
    "health": "/health"
  }
}
```

### 3. 获取注入配置

**GET** `/v1/config/injection`

获取当前的延迟和故障注入配置。

**响应示例:**
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

### 4. 更新注入配置

**PUT** `/v1/config/injection`

更新延迟和/或故障注入配置。

**请求体示例:**
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

**参数说明:**
- `delay` (可选): 延迟注入配置
  - `enabled`: 启用/禁用延迟注入
  - `min_delay_ms`: 最小延迟时间（毫秒）
  - `max_delay_ms`: 最大延迟时间（毫秒）
- `fault` (可选): 故障注入配置
  - `enabled`: 启用/禁用故障注入
  - `fault_type`: 故障类型 ("none", "http_error", "timeout", "invalid_response", "empty_response")
  - `http_status_code`: HTTP错误状态码（仅http_error类型）
  - `error_message`: 错误消息（仅http_error类型）
  - `probability`: 故障注入概率（0.0 到 1.0）

**响应示例:**
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

### 5. 重置注入配置

**POST** `/v1/config/injection/reset`

将所有注入配置重置为默认值。

**响应示例:**
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

### 6. 聊天完成

**POST** `/v1/chat/completions`

生成模拟的聊天完成响应。支持流式和非流式两种模式。

**请求体示例:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "你好"
    }
  ],
  "model": "mock-model",
  "temperature": 1.0,
  "max_tokens": 100,
  "stream": false
}
```

**参数说明:**
- `messages` (必需): 消息对象数组
  - `role`: 消息角色 ("system", "user", "assistant")
  - `content`: 消息内容
- `model` (可选): 模型标识符（默认: "mock-model"）
- `temperature` (可选): 采样温度（默认: 1.0）
- `max_tokens` (可选): 最大生成token数（默认: 100）
- `stream` (可选): 是否启用流式响应（默认: false）

**非流式响应示例:**
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
        "content": "这是一个模拟响应。"
      },
      "finish_reason": "stop"
    }
  ]
}
```

**流式响应示例:**
```
data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "这"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "是"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "一"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "个"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "模"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "拟"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "响"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "应"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "。"}, "finish_reason": null}]}

data: [DONE]
```

### 7. 获取日志

**GET** `/v1/logs`

获取日志记录，支持分页和类型过滤。

**查询参数:**
- `log_type` (可选): 日志类型 ("request", "error", "access")
- `limit` (可选): 返回记录数量限制（默认: 100）
- `offset` (可选): 起始位置偏移量（默认: 0）

**响应示例:**
```json
{
  "count": 5,
  "limit": 100,
  "offset": 0,
  "logs": [
    {
      "timestamp": "2024-01-01T12:00:00.000000",
      "type": "request",
      "method": "POST",
      "path": "/v1/chat/completions",
      "status_code": 200,
      "duration_ms": 45.5,
      "client_ip": "127.0.0.1",
      "user_agent": "testclient",
      "body": "Response: 24 chars"
    }
  ]
}
```

### 8. 查询日志

**POST** `/v1/logs/query`

根据条件查询日志记录。

**请求体示例:**
```json
{
  "log_type": "request",
  "limit": 50,
  "offset": 0
}
```

**响应示例:**
```json
{
  "count": 10,
  "limit": 50,
  "offset": 0,
  "logs": [...]
}
```

### 9. 搜索日志

**POST** `/v1/logs/search`

根据关键词搜索日志记录。

**请求体示例:**
```json
{
  "keyword": "chat",
  "log_type": "request",
  "limit": 20
}
```

**响应示例:**
```json
{
  "count": 5,
  "keyword": "chat",
  "logs": [...]
}
```

### 10. 获取日志统计

**GET** `/v1/logs/stats`

获取日志统计信息。

**响应示例:**
```json
{
  "total_logs": 150,
  "by_type": {
    "request": 100,
    "error": 5,
    "access": 45
  },
  "recent_errors": 2,
  "avg_response_time": 67.8
}
```

### 11. 清空日志

**DELETE** `/v1/logs`

清空所有内存中的日志记录。

**响应示例:**
```json
{
  "message": "Logs cleared successfully"
}
```

### 13. 验证 YAML 配置

**POST** `/v1/config/yaml/validate`

验证 YAML 配置格式是否正确。

**请求体示例:**
```json
{
  "version": "1.0",
  "description": "测试配置",
  "rules": [
    {
      "name": "问候规则",
      "trigger": "你好",
      "match_type": "exact",
      "response": "你好！我是 Mock LLM Server。",
      "enabled": true
    }
  ]
}
```

**响应示例:**
```json
{
  "valid": true,
  "message": "配置验证通过"
}
```

### 14. 验证 YAML 规则

**POST** `/v1/config/yaml/rules/validate`

验证单个 YAML 规则格式是否正确。

**请求体示例:**
```json
{
  "name": "问候规则",
  "trigger": "你好",
  "match_type": "exact",
  "response": "你好！我是 Mock LLM Server。",
  "enabled": true
}
```

**响应示例:**
```json
{
  "valid": true,
  "message": "规则验证通过"
}
```

### 15. 搜索 YAML 规则

**GET** `/v1/config/yaml/rules/search`

根据关键词搜索 YAML 规则。

**查询参数:**
- `keyword` (必需): 搜索关键词
- `match_type` (可选): 匹配类型过滤 ("exact", "contains", "regex")

**响应示例:**
```json
{
  "results": [
    {
      "name": "问候规则",
      "trigger": "你好",
      "match_type": "exact",
      "response": "你好！我是 Mock LLM Server。",
      "enabled": true
    }
  ],
  "count": 1
}
```

## 错误响应

### 400 错误请求

```json
{
  "detail": "Messages list cannot be empty"
}
```

### 404 未找到

```json
{
  "detail": "Log file not found"
}
```

## 配置说明

服务器可以通过环境变量进行配置：

- `MOCK_RESPONSE`: 自定义模拟响应文本
- `PORT`: 服务器端口（默认: 8000）
- `HOST`: 服务器主机（默认: 0.0.0.0）
- `DEBUG`: 启用调试模式（默认: false）
- `TESTING`: 测试模式（默认: false）
- `LOG_LEVEL`: 日志级别（默认: INFO）
- `LOG_FORMAT`: 日志格式（json/text，默认: json）

## 使用示例

### 基础聊天完成

#### cURL

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
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
            {"role": "user", "content": "你好"}
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
      { role: 'user', content: '你好' }
    ]
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### 流式响应

#### cURL

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
    ],
    "stream": true
  }'
```

#### Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "stream": True
    }
)

for line in response.iter_lines():
    if line.startswith("data: "):
        data = line[6:]
        if data == "[DONE]":
            break
        print(data)
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
      { role: 'user', content: '你好' }
    ],
    stream: true
  })
})
  .then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    function read() {
      reader.read().then(({ done, value }) => {
        if (done) return;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line[6:];
            if (data === '[DONE]') {
              return;
            }
            console.log(data);
          }
        }
        
        read();
      });
    }
    
    read();
  });
```

### 延迟注入

#### 启用延迟注入

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

#### Python 延迟示例

```python
import httpx
import time

# 启用延迟注入
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

# 发送带延迟的请求
start_time = time.time()
response = httpx.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)
end_time = time.time()

print(f"响应: {response.json()}")
print(f"延迟: {(end_time - start_time) * 1000:.0f}ms")
```

### 故障注入

#### 启用 HTTP 错误故障

```bash
curl -X PUT http://localhost:8000/v1/config/injection \
  -H "Content-Type: application/json" \
  -d '{
    "fault": {
      "enabled": true,
      "fault_type": "http_error",
      "http_status_code": 503,
      "error_message": "服务不可用",
      "probability": 1.0
    }
  }'
```

#### 启用超时故障

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

#### 启用无效响应故障

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

#### 启用空响应故障

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

### 组合延迟和故障注入

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
      "error_message": "内部服务器错误",
      "probability": 0.3
    }
  }'
```

### 重置配置

```bash
curl -X POST http://localhost:8000/v1/config/injection/reset
```

### Python 故障注入测试

```python
import httpx
import random

# 配置故障注入，概率为30%
httpx.put(
    "http://localhost:8000/v1/config/injection",
    json={
        "fault": {
            "enabled": True,
            "fault_type": "http_error",
            "http_status_code": 503,
            "error_message": "服务不可用",
            "probability": 0.3
        }
    }
)

# 发送多个请求测试故障处理
for i in range(10):
    try:
        response = httpx.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": f"请求 {i+1}"}
                ]
            }
        )
        print(f"请求 {i+1}: 成功 - {response.json()}")
    except httpx.HTTPStatusError as e:
        print(f"请求 {i+1}: 失败 - {e.response.status_code} - {e.response.text}")
```

### 日志查询

#### 获取所有日志

```bash
curl http://localhost:8000/v1/logs
```

#### 按类型过滤日志

```bash
curl "http://localhost:8000/v1/logs?log_type=request&limit=10"
```

#### 搜索日志

```bash
curl -X POST http://localhost:8000/v1/logs/search \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "error",
    "log_type": "error",
    "limit": 20
  }'
```

#### 获取日志统计

```bash
curl http://localhost:8000/v1/logs/stats
```

#### 清空日志

```bash
curl -X DELETE http://localhost:8000/v1/logs
```

## 故障类型详解

### HTTP 错误 (http_error)
- 返回指定的 HTTP 状态码
- 可自定义错误消息
- 用于测试 HTTP 错误处理

### 超时 (timeout)
- 模拟长时间等待
- 返回 504 Gateway Timeout
- 用于测试超时处理

### 无效响应 (invalid_response)
- 返回不符合 API 规范的响应
- 用于测试响应解析错误处理

### 空响应 (empty_response)
- 返回空的 choices 数组
- 用于测试空响应处理

## 最佳实践

1. **渐进式测试**: 从低延迟和低故障概率开始，逐步增加
2. **场景化测试**: 模拟真实的网络条件和错误场景
3. **监控和日志**: 记录注入的延迟和故障，便于分析
4. **重置配置**: 测试完成后记得重置配置
5. **组合测试**: 同时测试延迟和故障，模拟真实复杂场景
6. **流式响应**: 对于长响应内容，使用流式模式提升用户体验

## 注意事项

- 延迟时间在 min_delay_ms 和 max_delay_ms 之间随机生成
- 故障注入基于概率，不是每次请求都会触发
- 超时故障会等待30秒后返回504错误
- 流式响应会按字符分块返回内容
- 日志记录所有请求，包括注入的延迟和故障信息
- 建议在测试环境中使用，避免影响生产环境
- 测试环境会使用独立的日志目录（logs_test/），避免污染生产日志