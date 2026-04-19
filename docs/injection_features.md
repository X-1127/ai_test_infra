# 延迟注入和故障注入功能

## 概述

Mock LLM Server 现在支持延迟注入和故障注入功能，用于测试应用程序在各种网络条件和错误情况下的行为。

## 功能特性

### 1. 延迟注入 (Delay Injection)

模拟网络延迟，测试应用程序的响应时间和超时处理能力。

**特性：**
- 可配置的最小和最大延迟时间（毫秒）
- 在指定范围内随机生成延迟
- 可随时启用/禁用

**使用场景：**
- 测试慢速网络环境下的应用表现
- 验证超时机制是否正常工作
- 模拟高延迟场景下的用户体验

### 2. 故障注入 (Fault Injection)

模拟各种错误情况，测试应用程序的错误处理能力。

**支持的故障类型：**

1. **HTTP错误 (http_error)**
   - 返回指定的HTTP状态码
   - 可自定义错误消息
   - 用于测试HTTP错误处理

2. **超时 (timeout)**
   - 模拟长时间等待
   - 返回504 Gateway Timeout
   - 用于测试超时处理

3. **无效响应 (invalid_response)**
   - 返回不符合API规范的响应
   - 用于测试响应解析错误处理

4. **空响应 (empty_response)**
   - 返回空的choices数组
   - 用于测试空响应处理

**特性：**
- 可配置故障注入概率（0.0 - 1.0）
- 支持多种故障类型
- 可自定义HTTP状态码和错误消息

## API端点

### 获取注入配置
```
GET /v1/config/injection
```

### 更新注入配置
```
PUT /v1/config/injection
```

### 重置注入配置
```
POST /v1/config/injection/reset
```

## 使用示例

### 启用延迟注入

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

### 启用故障注入

```bash
curl -X PUT http://localhost:8000/v1/config/injection \
  -H "Content-Type: application/json" \
  -d '{
    "fault": {
      "enabled": true,
      "fault_type": "http_error",
      "http_status_code": 503,
      "error_message": "Service unavailable",
      "probability": 0.5
    }
  }'
```

### 组合使用

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

## Python测试示例

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
            {"role": "user", "content": "Hello"}
        ]
    }
)
end_time = time.time()

print(f"延迟: {(end_time - start_time) * 1000:.0f}ms")
print(f"响应: {response.json()}")

# 重置配置
httpx.post("http://localhost:8000/v1/config/injection/reset")
```

## 测试脚本

项目包含一个完整的测试脚本 `test_injection_features.py`，可以测试所有注入功能：

```bash
python test_injection_features.py
```

## 配置参数详解

### 延迟配置 (DelayConfig)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | boolean | false | 是否启用延迟注入 |
| min_delay_ms | integer | 0 | 最小延迟时间（毫秒） |
| max_delay_ms | integer | 1000 | 最大延迟时间（毫秒） |

### 故障配置 (FaultConfig)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| enabled | boolean | false | 是否启用故障注入 |
| fault_type | string | "none" | 故障类型：none, http_error, timeout, invalid_response, empty_response |
| http_status_code | integer | 500 | HTTP错误状态码（仅http_error类型） |
| error_message | string | "Internal server error" | 错误消息（仅http_error类型） |
| probability | float | 1.0 | 故障注入概率（0.0-1.0） |

## 最佳实践

1. **渐进式测试**：从低延迟和低故障概率开始，逐步增加
2. **场景化测试**：模拟真实的网络条件和错误场景
3. **监控和日志**：记录注入的延迟和故障，便于分析
4. **重置配置**：测试完成后记得重置配置
5. **组合测试**：同时测试延迟和故障，模拟真实复杂场景

## 注意事项

- 延迟时间在min_delay_ms和max_delay_ms之间随机生成
- 故障注入基于概率，不是每次请求都会触发
- 超时故障会等待30秒后返回504错误
- 建议在测试环境中使用，避免影响生产环境

## 故障排查

### 延迟不生效
- 检查delay.enabled是否为true
- 确认min_delay_ms和max_delay_ms设置正确

### 故障不触发
- 检查fault.enabled是否为true
- 确认probability大于0
- 多次请求以验证概率设置

### 配置重置失败
- 确认服务器正在运行
- 检查API端点是否正确

## 相关文档

- [API文档](./api.md) - 完整的API参考
- [部署指南](./deployment.md) - 服务器部署说明