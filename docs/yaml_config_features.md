# YAML配置预设回复功能说明

## 功能概述

YAML配置预设回复功能允许用户通过YAML配置文件定义预设的回复规则，根据用户输入的内容动态匹配并返回相应的回复。这大大提升了Mock Server的灵活性和实用性。

## 核心特性

### 1. 多种匹配方式
- **精确匹配 (exact)**: 用户输入必须完全匹配触发词
- **包含匹配 (contains)**: 用户输入包含触发词即可匹配
- **正则匹配 (regex)**: 使用正则表达式进行复杂匹配

### 2. 规则管理
- 动态添加、删除、修改规则
- 启用/禁用特定规则
- 规则优先级控制（按顺序匹配）

### 3. 配置热重载
- 支持运行时重新加载配置文件
- 无需重启服务器即可更新规则

### 4. 灵活切换
- 可以随时启用/禁用YAML配置
- 禁用时回退到默认响应模式

## 配置文件格式

### 文件位置
```
config/responses.yaml
```

### 配置结构

```yaml
responses:
  # 默认回复（当没有匹配到任何规则时使用）
  default_response: "这是一个模拟响应。"

  # 预设回复规则列表
  rules:
    # 规则1：精确匹配
    - trigger: "你好"
      response: "你好！有什么可以帮助你的吗？"
      match_type: "exact"
      enabled: true

    # 规则2：包含匹配
    - trigger: "天气"
      response: "今天天气不错，适合出去走走。"
      match_type: "contains"
      enabled: true

    # 规则3：正则匹配
    - trigger: ".*错误.*"
      response: "抱歉，发生了错误。"
      match_type: "regex"
      enabled: true

# 配置元数据
metadata:
  version: "1.0.0"
  description: "Mock LLM Server 预设回复配置"
  last_updated: "2026-04-20"
```

### 配置参数说明

#### 规则参数 (Rule)

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| trigger | string | 是 | 触发词或正则表达式 |
| response | string | 是 | 匹配成功后返回的回复 |
| match_type | string | 否 | 匹配类型：exact、contains、regex（默认：contains） |
| enabled | boolean | 否 | 是否启用该规则（默认：true） |

#### 匹配类型说明

- **exact**: 精确匹配，用户输入必须完全等于trigger
- **contains**: 包含匹配，用户输入包含trigger即可
- **regex**: 正则匹配，使用正则表达式进行匹配

## API端点

### 1. 获取YAML配置状态

**GET** `/v1/config/yaml`

获取当前YAML配置的状态和内容。

**响应示例：**
```json
{
  "enabled": false,
  "config": {
    "default_response": "这是一个模拟响应。",
    "rules": [
      {
        "trigger": "你好",
        "response": "你好！有什么可以帮助你的吗？",
        "match_type": "exact",
        "enabled": true
      }
    ],
    "metadata": {
      "version": "1.0.0",
      "description": "Mock LLM Server 预设回复配置",
      "last_updated": "2026-04-20"
    }
  }
}
```

### 2. 启用YAML配置

**PUT** `/v1/config/yaml/enable`

启用YAML配置功能。

**响应示例：**
```json
{
  "enabled": true,
  "config": {
    "default_response": "这是一个模拟响应。",
    "rules": [...],
    "metadata": {...}
  }
}
```

### 3. 禁用YAML配置

**PUT** `/v1/config/yaml/disable`

禁用YAML配置功能，回退到默认响应模式。

**响应示例：**
```json
{
  "enabled": false,
  "config": {
    "default_response": "这是一个模拟响应。",
    "rules": [...],
    "metadata": {...}
  }
}
```

### 4. 重载YAML配置

**POST** `/v1/config/yaml/reload`

重新加载YAML配置文件，无需重启服务器。

**响应示例：**
```json
{
  "enabled": true,
  "config": {
    "default_response": "这是一个模拟响应。",
    "rules": [...],
    "metadata": {...}
  }
}
```

### 5. 验证配置

**POST** `/v1/config/yaml/validate`

验证YAML配置文件的格式和内容是否正确。

**请求体：**
```json
{
  "responses": {
    "default_response": "默认响应",
    "rules": [
      {
        "trigger": "测试",
        "response": "测试响应",
        "match_type": "exact",
        "enabled": true
      }
    ]
  }
}
```

**响应示例：**
```json
{
  "valid": true,
  "message": "配置验证通过"
}
```

### 6. 添加规则

**POST** `/v1/config/yaml/rules`

添加新的回复规则。

**请求体：**
```json
{
  "trigger": "测试",
  "response": "测试成功！",
  "match_type": "exact",
  "enabled": true
}
```

**响应示例：**
```json
{
  "enabled": true,
  "config": {
    "default_response": "这是一个模拟响应。",
    "rules": [
      {
        "trigger": "你好",
        "response": "你好！有什么可以帮助你的吗？",
        "match_type": "exact",
        "enabled": true
      },
      {
        "trigger": "测试",
        "response": "测试成功！",
        "match_type": "exact",
        "enabled": true
      }
    ],
    "metadata": {...}
  }
}
```

### 7. 删除规则

**DELETE** `/v1/config/yaml/rules/{index}`

删除指定索引的规则。

**参数：**
- `index`: 规则索引（从0开始）

**响应示例：**
```json
{
  "enabled": true,
  "config": {
    "default_response": "这是一个模拟响应。",
    "rules": [...],
    "metadata": {...}
  }
}
```

### 8. 更新规则

**PUT** `/v1/config/yaml/rules/{index}`

更新指定索引的规则。

**参数：**
- `index`: 规则索引（从0开始）

**请求体：**
```json
{
  "trigger": "更新后的规则",
  "response": "更新后的响应",
  "match_type": "exact",
  "enabled": true
}
```

**响应示例：**
```json
{
  "enabled": true,
  "config": {
    "default_response": "这是一个模拟响应。",
    "rules": [...],
    "metadata": {...}
  }
}
```

### 9. 启用规则

**PUT** `/v1/config/yaml/rules/{index}/enable`

启用指定索引的规则。

**参数：**
- `index`: 规则索引（从0开始）

**响应示例：**
```json
{
  "enabled": true,
  "config": {
    "default_response": "这是一个模拟响应。",
    "rules": [...],
    "metadata": {...}
  }
}
```

### 10. 禁用规则

**PUT** `/v1/config/yaml/rules/{index}/disable`

禁用指定索引的规则。

**参数：**
- `index`: 规则索引（从0开始）

**响应示例：**
```json
{
  "enabled": true,
  "config": {
    "default_response": "这是一个模拟响应。",
    "rules": [...],
    "metadata": {...}
  }
}
```

### 11. 验证规则

**POST** `/v1/config/yaml/rules/validate`

验证规则的格式和内容是否正确。

**请求体：**
```json
{
  "trigger": "测试",
  "response": "测试响应",
  "match_type": "exact",
  "enabled": true
}
```

**响应示例：**
```json
{
  "valid": true,
  "message": "规则验证通过"
}
```

**无效规则示例：**
```json
{
  "valid": false,
  "message": "触发词不能为空"
}
```

### 12. 搜索规则

**GET** `/v1/config/yaml/rules/search`

根据关键词和匹配类型搜索规则。

**参数：**
- `keyword`: 搜索关键词（可选）
- `match_type`: 匹配类型过滤（可选）：exact、contains、regex

**响应示例：**
```json
{
  "results": [
    {
      "index": 0,
      "rule": {
        "trigger": "你好",
        "response": "你好！有什么可以帮助你的吗？",
        "match_type": "exact",
        "enabled": true
      }
    }
  ],
  "count": 1
}
```

## 使用示例

### Python示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 启用YAML配置
response = requests.put(f"{BASE_URL}/v1/config/yaml/enable")
print(f"启用YAML配置: {response.json()}")

# 2. 发送聊天请求
response = requests.post(f"{BASE_URL}/v1/chat/completions", json={
    "messages": [{"role": "user", "content": "你好"}]
})
print(f"聊天响应: {response.json()}")

# 3. 添加新规则
new_rule = {
    "trigger": "测试",
    "response": "测试成功！",
    "match_type": "exact",
    "enabled": True
}
response = requests.post(f"{BASE_URL}/v1/config/yaml/rules", json=new_rule)
print(f"添加规则: {response.json()}")

# 4. 测试新规则
response = requests.post(f"{BASE_URL}/v1/chat/completions", json={
    "messages": [{"role": "user", "content": "测试"}]
})
print(f"新规则响应: {response.json()}")
```

### cURL示例

```bash
# 1. 启用YAML配置
curl -X PUT http://localhost:8000/v1/config/yaml/enable

# 2. 发送聊天请求
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "你好"}]
  }'

# 3. 添加新规则
curl -X POST http://localhost:8000/v1/config/yaml/rules \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "测试",
    "response": "测试成功！",
    "match_type": "exact",
    "enabled": true
  }'

# 4. 测试新规则
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "测试"}]
  }'
```

## 匹配规则说明

### 规则优先级

规则按配置文件中的顺序依次匹配，一旦匹配成功就返回对应的响应，不再继续匹配后续规则。

### 匹配示例

#### 精确匹配
```yaml
- trigger: "你好"
  response: "你好！有什么可以帮助你的吗？"
  match_type: "exact"
```
- 匹配: "你好" ✅
- 不匹配: "你好吗" ❌
- 不匹配: "你好！" ❌

#### 包含匹配
```yaml
- trigger: "天气"
  response: "今天天气不错，适合出去走走。"
  match_type: "contains"
```
- 匹配: "今天天气怎么样" ✅
- 匹配: "天气真好" ✅
- 不匹配: "今天怎么样" ❌

#### 正则匹配
```yaml
- trigger: "\\d+"
  response: "检测到数字"
  match_type: "regex"
```
- 匹配: "我有123个苹果" ✅
- 匹配: "数字是456" ✅
- 不匹配: "我没有苹果" ❌

## 最佳实践

### 1. 规则组织
- 将常用规则放在前面
- 按匹配类型分组组织
- 使用清晰的命名和描述

### 2. 性能优化
- 避免过于复杂的正则表达式
- 合理设置规则数量
- 定期清理不使用的规则
- 利用规则索引和缓存机制

### 3. 测试验证
- 添加规则后立即测试
- 验证规则优先级
- 测试边界情况
- 使用配置验证API

### 4. 配置管理
- 使用版本控制管理配置文件
- 定期备份配置
- 记录配置变更历史
- 使用配置验证功能

### 5. 错误处理
- 设置合理的默认回复
- 处理正则表达式错误
- 监控规则匹配情况
- 使用规则验证功能

## 边界情况处理

### 1. 空输入处理

系统会自动处理空输入和空白输入，返回默认响应：

```python
# 空字符串
response = requests.post("/v1/chat/completions", json={
    "messages": [{"role": "user", "content": ""}]
})
# 返回默认响应

# 空白字符串
response = requests.post("/v1/chat/completions", json={
    "messages": [{"role": "user", "content": "   "}]
})
# 返回默认响应
```

### 2. 特殊字符处理

系统支持特殊字符的匹配：

```yaml
rules:
  - trigger: "测试@#$%"
    response: "特殊字符匹配"
    match_type: "exact"
    enabled: true
```

### 3. 规则优先级

系统按以下优先级匹配规则：
1. 精确匹配
2. 包含匹配
3. 正则匹配

相同匹配类型的规则按配置顺序匹配。

## 配置验证

### 1. 配置文件验证

在应用配置前，使用验证API检查配置：

```bash
curl -X POST http://localhost:8000/v1/config/yaml/validate \
  -H "Content-Type: application/json" \
  -d '{
    "responses": {
      "default_response": "默认响应",
      "rules": [
        {
          "trigger": "测试",
          "response": "测试响应",
          "match_type": "exact",
          "enabled": true
        }
      ]
    }
  }'
```

### 2. 规则验证

在添加规则前，验证规则的正确性：

```bash
curl -X POST http://localhost:8000/v1/config/yaml/rules/validate \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "测试",
    "response": "测试响应",
    "match_type": "exact",
    "enabled": true
  }'
```

### 3. 验证错误处理

系统会返回详细的验证错误信息：

```json
{
  "valid": false,
  "message": "触发词不能为空"
}
```

常见验证错误：
- 触发词不能为空
- 响应不能为空
- 正则表达式错误
- 匹配类型无效

## 规则搜索

### 1. 关键词搜索

根据关键词搜索规则：

```bash
curl "http://localhost:8000/v1/config/yaml/rules/search?keyword=你好"
```

### 2. 类型过滤

按匹配类型过滤规则：

```bash
curl "http://localhost:8000/v1/config/yaml/rules/search?match_type=exact"
```

### 3. 组合搜索

同时使用关键词和类型过滤：

```bash
curl "http://localhost:8000/v1/config/yaml/rules/search?keyword=测试&match_type=exact"
```

### 4. 搜索结果

搜索结果包含规则索引和详细信息：

```json
{
  "results": [
    {
      "index": 0,
      "rule": {
        "trigger": "你好",
        "response": "你好！有什么可以帮助你的吗？",
        "match_type": "exact",
        "enabled": true
      }
    }
  ],
  "count": 1
}
```

## 性能优化

### 1. 正则表达式缓存

系统自动缓存编译后的正则表达式，避免重复编译：

```python
# 系统自动处理，无需手动配置
# 相同的正则表达式只会编译一次
```

### 2. 规则索引

系统按匹配类型建立规则索引，提高匹配效率：

```python
# 系统自动构建索引
# 按exact、contains、regex分类存储规则
```

### 3. 匹配优先级

系统按优先级顺序匹配，提高匹配效率：

```python
# 优先级：exact -> contains -> regex
# 快速匹配，减少不必要的正则匹配
```

### 4. 边界处理

系统快速处理边界情况，减少不必要的匹配：

```python
# 空输入直接返回默认响应
# 空白输入直接返回默认响应
# 禁用的规则跳过匹配
```

## 故障排查

### 常见问题

#### 1. 规则不生效

**可能原因：**
- YAML配置未启用
- 规则被禁用
- 规则顺序问题

**解决方法：**
```bash
# 检查配置状态
curl http://localhost:8000/v1/config/yaml

# 启用配置
curl -X PUT http://localhost:8000/v1/config/yaml/enable

# 检查规则状态
curl http://localhost:8000/v1/config/yaml
```

#### 2. 正则匹配失败

**可能原因：**
- 正则表达式语法错误
- 特殊字符未转义

**解决方法：**
```yaml
# 错误示例
- trigger: "\d+"
  response: "检测到数字"
  match_type: "regex"

# 正确示例
- trigger: "\\d+"
  response: "检测到数字"
  match_type: "regex"
```

#### 3. 配置文件加载失败

**可能原因：**
- 文件路径错误
- YAML语法错误
- 文件权限问题

**解决方法：**
```bash
# 检查文件是否存在
ls config/responses.yaml

# 验证YAML语法
python -c "import yaml; yaml.safe_load(open('config/responses.yaml'))"

# 检查文件权限
ls -la config/responses.yaml
```

## 高级用法

### 1. 动态规则管理

```python
import requests

# 批量添加规则
rules = [
    {"trigger": "规则1", "response": "响应1", "match_type": "exact", "enabled": True},
    {"trigger": "规则2", "response": "响应2", "match_type": "exact", "enabled": True},
]

for rule in rules:
    requests.post("http://localhost:8000/v1/config/yaml/rules", json=rule)
```

### 2. 规则优先级调整

```python
import requests

# 获取当前规则
response = requests.get("http://localhost:8000/v1/config/yaml")
rules = response.json()["config"]["rules"]

# 调整规则顺序（将第一个规则移到最后）
first_rule = rules.pop(0)
rules.append(first_rule)

# 更新所有规则
for i, rule in enumerate(rules):
    requests.put(f"http://localhost:8000/v1/config/yaml/rules/{i}", json=rule)
```

### 3. 条件匹配组合

```yaml
# 使用正则表达式实现复杂匹配
- trigger: "^(你好|您好|嗨)"
  response: "你好！有什么可以帮助你的吗？"
  match_type: "regex"
  enabled: true

- trigger: "(?i)error"
  response: "检测到错误信息"
  match_type: "regex"
  enabled: true
```

## 相关文档

- [API文档](api.md) - 完整的API参考
- [部署指南](deployment.md) - 服务器部署说明
- [注入功能说明](injection_features.md) - 延迟和故障注入功能详解
- [项目说明文档](../PROJECT_GUIDE.md) - 项目总体说明