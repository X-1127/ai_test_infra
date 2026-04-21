# 延迟注入、故障注入、流式响应和日志系统详解

## 功能概述

Mock LLM Server 提供了强大的延迟注入、故障注入、流式响应和日志系统功能，用于测试应用程序在各种网络条件、错误情况下的行为，以及监控和记录系统运行状态。这些功能可以帮助开发者验证应用的健壮性、错误处理能力和性能表现。

## 核心特性

### 1. 延迟注入 (Delay Injection)

模拟网络延迟，测试应用程序的响应时间和超时处理能力。

**功能特点：**
- 可配置的最小和最大延迟时间（毫秒）
- 在指定范围内随机生成延迟
- 可随时启用/禁用
- 支持实时配置更新

**使用场景：**
- 测试慢速网络环境下的应用表现
- 验证超时机制是否正常工作
- 模拟高延迟场景下的用户体验
- 测试应用的并发处理能力

### 2. 故障注入 (Fault Injection)

模拟各种错误情况，测试应用程序的错误处理能力。

**支持的故障类型：**

#### 1. HTTP 错误 (http_error)
- 返回指定的 HTTP 状态码
- 可自定义错误消息
- 用于测试 HTTP 错误处理
- 支持所有标准 HTTP 状态码

#### 2. 超时 (timeout)
- 模拟长时间等待
- 返回 504 Gateway Timeout
- 用于测试超时处理
- 默认等待时间为 30 秒

#### 3. 无效响应 (invalid_response)
- 返回不符合 API 规范的响应
- 用于测试响应解析错误处理
- 帮助发现客户端解析逻辑的问题

#### 4. 空响应 (empty_response)
- 返回空的 choices 数组
- 用于测试空响应处理
- 验证应用对空结果的健壮性

**功能特点：**
- 可配置故障注入概率（0.0 - 1.0）
- 支持多种故障类型
- 可自定义 HTTP 状态码和错误消息
- 支持实时配置更新

### 3. 流式响应 (Streaming Response)

模拟真实LLM的流式输出效果，使用Server-Sent Events (SSE)协议逐字符或逐词发送响应。

**功能特点：**
- 支持SSE流式输出
- 逐字符发送响应内容
- 模拟真实LLM的打字效果
- 完全兼容OpenAI流式响应格式

**使用场景：**
- 测试客户端对流式响应的处理能力
- 验证流式数据的正确解析
- 模拟真实LLM的响应体验
- 测试流式连接的稳定性

### 4. 日志系统 (Logging System)

完整的请求、错误和访问日志记录与查询系统。

**功能特点：**
- 记录所有API请求和响应
- 记录系统错误和异常
- 支持日志类型过滤
- 支持分页查询
- 测试环境与生产环境日志隔离

**日志类型：**
- **请求日志**: 记录API请求的详细信息
- **错误日志**: 记录系统错误和异常
- **访问日志**: 记录访问统计信息

## API 端点说明

### 获取注入配置
```
GET /v1/config/injection
```

获取当前的延迟和故障注入配置。

**响应示例：**
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

### 更新注入配置
```
PUT /v1/config/injection
```

更新延迟和/或故障注入配置。

**请求示例：**
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

### 重置注入配置
```
POST /v1/config/injection/reset
```

将所有注入配置重置为默认值。

### 流式响应聊天
```
POST /v1/chat/completions
```

发送流式响应请求。

**请求示例：**
```json
{
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "model": "mock-model",
  "temperature": 1.0,
  "max_tokens": 100,
  "stream": true
}
```

**响应示例：**
```
data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "你"}, "finish_reason": null}]}

data: {"id": "mock-1234567890", "object": "chat.completion.chunk", "created": 1234567890, "model": "mock-model", "choices": [{"index": 0, "delta": {"content": "好"}, "finish_reason": null}]}

...

data: [DONE]
```

### 获取日志
```
GET /v1/logs
```

获取日志记录，支持分页和类型过滤。

**查询参数：**
- `log_type` (可选): 日志类型 ("request", "error", "access")
- `limit` (可选): 返回记录数量限制（默认: 100）
- `offset` (可选): 起始位置偏移量（默认: 0）

**响应示例：**
```json
{
  "logs": [
    {
      "timestamp": "2026-04-21T10:30:00",
      "log_type": "request",
      "method": "POST",
      "path": "/v1/chat/completions",
      "status_code": 200,
      "duration_ms": 150,
      "client_ip": "127.0.0.1",
      "user_agent": "python-requests/2.31.0",
      "body": "Response: 10 chars"
    }
  ],
  "count": 1
}
```

### 清空日志
```
POST /v1/logs/clear
```

清空所有日志记录。

**响应示例：**
```json
{
  "message": "日志已清空",
  "count": 0
}
```

## 使用示例

### 延迟注入示例

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

#### Python 延迟测试

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
            "max_delay_ms": 300
        }
    }
)

# 测试请求
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

print(f"延迟: {(end_time - start_time) * 1000:.0f}ms")
print(f"响应: {response.json()}")

# 重置配置
httpx.post("http://localhost:8000/v1/config/injection/reset")
```

### 故障注入示例

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

### 组合使用示例

#### 同时启用延迟和故障注入

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

#### Python 综合测试

```python
import httpx
import time

# 配置延迟和故障注入
httpx.put(
    "http://localhost:8000/v1/config/injection",
    json={
        "delay": {
            "enabled": True,
            "min_delay_ms": 100,
            "max_delay_ms": 500
        },
        "fault": {
            "enabled": True,
            "fault_type": "http_error",
            "http_status_code": 503,
            "error_message": "服务不可用",
            "probability": 0.3
        }
    }
)

# 发送多个请求测试
success_count = 0
failure_count = 0

for i in range(10):
    try:
        start_time = time.time()
        response = httpx.post(
            "http://localhost:8000/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": f"测试请求 {i+1}"}
                ]
            }
        )
        end_time = time.time()
        
        if response.status_code == 200:
            success_count += 1
            print(f"请求 {i+1}: 成功 (延迟: {(end_time - start_time) * 1000:.0f}ms)")
        else:
            failure_count += 1
            print(f"请求 {i+1}: 失败 (状态码: {response.status_code})")
    except Exception as e:
        failure_count += 1
        print(f"请求 {i+1}: 异常 - {str(e)}")

print(f"\n统计: 成功 {success_count} 次, 失败 {failure_count} 次")

# 重置配置
httpx.post("http://localhost:8000/v1/config/injection/reset")
```

## 配置参数详解

### 延迟配置 (DelayConfig)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | boolean | false | 是否启用延迟注入 |
| min_delay_ms | integer | 0 | 最小延迟时间（毫秒） |
| max_delay_ms | integer | 1000 | 最大延迟时间（毫秒） |

**注意事项：**
- 延迟时间在 min_delay_ms 和 max_delay_ms 之间随机生成
- 建议设置合理的延迟范围，避免测试时间过长
- 可以通过调整延迟范围模拟不同的网络条件

### 故障配置 (FaultConfig)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | boolean | false | 是否启用故障注入 |
| fault_type | string | "none" | 故障类型 |
| http_status_code | integer | 500 | HTTP错误状态码（仅http_error类型） |
| error_message | string | "Internal server error" | 错误消息（仅http_error类型） |
| probability | float | 1.0 | 故障注入概率（0.0-1.0） |

**故障类型说明：**
- `none`: 不注入故障
- `http_error`: 注入HTTP错误
- `timeout`: 注入超时
- `invalid_response`: 注入无效响应
- `empty_response`: 注入空响应

**注意事项：**
- probability 为 0.0 表示从不注入故障
- probability 为 1.0 表示每次都注入故障
- probability 为 0.5 表示约50%的请求会触发故障

## 测试场景建议

### 1. 基础功能测试

**目标**: 验证应用的基本功能

**配置**:
```json
{
  "delay": {"enabled": false},
  "fault": {"enabled": false}
}
```

### 2. 网络延迟测试

**目标**: 测试应用在慢速网络下的表现

**配置**:
```json
{
  "delay": {
    "enabled": true,
    "min_delay_ms": 500,
    "max_delay_ms": 2000
  },
  "fault": {"enabled": false}
}
```

### 3. 错误处理测试

**目标**: 验证应用的错误处理能力

**配置**:
```json
{
  "delay": {"enabled": false},
  "fault": {
    "enabled": true,
    "fault_type": "http_error",
    "http_status_code": 500,
    "probability": 0.5
  }
}
```

### 4. 超时处理测试

**目标**: 测试应用的超时处理机制

**配置**:
```json
{
  "delay": {"enabled": false},
  "fault": {
    "enabled": true,
    "fault_type": "timeout",
    "probability": 0.3
  }
}
```

### 5. 综合压力测试

**目标**: 模拟真实世界的复杂场景

**配置**:
```json
{
  "delay": {
    "enabled": true,
    "min_delay_ms": 100,
    "max_delay_ms": 1000
  },
  "fault": {
    "enabled": true,
    "fault_type": "http_error",
    "http_status_code": 503,
    "probability": 0.2
  }
}
```

## 最佳实践

### 1. 渐进式测试

从低延迟和低故障概率开始，逐步增加难度：

```python
# 第一阶段：低延迟
config_delay_low = {
    "delay": {"enabled": True, "min_delay_ms": 50, "max_delay_ms": 200},
    "fault": {"enabled": False}
}

# 第二阶段：中等延迟
config_delay_medium = {
    "delay": {"enabled": True, "min_delay_ms": 200, "max_delay_ms": 500},
    "fault": {"enabled": False}
}

# 第三阶段：高延迟 + 低故障概率
config_combined = {
    "delay": {"enabled": True, "min_delay_ms": 500, "max_delay_ms": 1000},
    "fault": {"enabled": True, "probability": 0.1}
}
```

### 2. 场景化测试

模拟真实的网络条件和错误场景：

```python
# 模拟移动网络
mobile_network = {
    "delay": {"enabled": True, "min_delay_ms": 100, "max_delay_ms": 500},
    "fault": {"enabled": True, "fault_type": "http_error", "probability": 0.05}
}

# 模拟不稳定网络
unstable_network = {
    "delay": {"enabled": True, "min_delay_ms": 50, "max_delay_ms": 2000},
    "fault": {"enabled": True, "fault_type": "timeout", "probability": 0.15}
}
```

### 3. 监控和日志

记录注入的延迟和故障，便于分析：

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_with_injection():
    # 配置注入
    httpx.put("http://localhost:8000/v1/config/injection", json=config)
    
    # 执行测试
    start_time = time.time()
    try:
        response = httpx.post(...)
        logger.info(f"请求成功，耗时: {(time.time() - start_time) * 1000:.0f}ms")
    except Exception as e:
        logger.error(f"请求失败: {str(e)}")
```

### 4. 重置配置

测试完成后记得重置配置：

```python
# 测试前保存配置
original_config = httpx.get("http://localhost:8000/v1/config/injection").json()

# 执行测试
# ...

# 测试后恢复配置
httpx.post("http://localhost:8000/v1/config/injection/reset")
```

### 5. 组合测试

同时测试延迟和故障，模拟真实复杂场景：

```python
# 模拟真实世界的复杂场景
real_world_scenario = {
    "delay": {
        "enabled": True,
        "min_delay_ms": 100,
        "max_delay_ms": 800
    },
    "fault": {
        "enabled": True,
        "fault_type": "http_error",
        "http_status_code": 503,
        "probability": 0.1
    }
}
```

## 注意事项

1. **延迟时间**: 延迟时间在 min_delay_ms 和 max_delay_ms 之间随机生成
2. **故障概率**: 故障注入基于概率，不是每次请求都会触发
3. **超时等待**: 超时故障会等待30秒后返回504错误
4. **测试环境**: 建议在测试环境中使用，避免影响生产环境
5. **配置重置**: 测试完成后记得重置配置
6. **日志记录**: 记录测试过程中的延迟和故障信息，便于分析

## 故障排查

### 延迟不生效

**可能原因：**
- delay.enabled 设置为 false
- min_delay_ms 和 max_delay_ms 设置不正确
- 配置未正确更新

**解决方法：**
```bash
# 检查当前配置
curl http://localhost:8000/v1/config/injection

# 确认配置已更新
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

### 故障不触发

**可能原因：**
- fault.enabled 设置为 false
- probability 设置为 0
- 测试次数不足

**解决方法：**
```bash
# 检查当前配置
curl http://localhost:8000/v1/config/injection

# 增加故障概率
curl -X PUT http://localhost:8000/v1/config/injection \
  -H "Content-Type: application/json" \
  -d '{
    "fault": {
      "enabled": true,
      "fault_type": "http_error",
      "probability": 1.0
    }
  }'

# 发送多次请求验证
for i in {1..10}; do
  curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{"messages": [{"role": "user", "content": "test"}]}'
done
```

### 配置重置失败

**可能原因：**
- 服务器未运行
- API 端点错误
- 网络问题

**解决方法：**
```bash
# 检查服务器状态
curl http://localhost:8000/health

# 手动重置配置
curl -X POST http://localhost:8000/v1/config/injection/reset

# 验证重置结果
curl http://localhost:8000/v1/config/injection
```

## 相关文档

- [API 文档](api.md) - 完整的 API 参考
- [部署指南](deployment.md) - 服务器部署说明
- [项目说明文档](../PROJECT_GUIDE.md) - 项目总体说明