# LLM Mock Server 项目说明文档

## 📋 项目概述

**LLM Mock Server** 是一个专为测试AI应用而设计的模拟LLM服务器。它提供了与OpenAI API兼容的接口，支持延迟注入和故障注入功能，帮助开发者测试和验证AI应用在各种网络条件和错误场景下的行为。

### 🎯 核心特性

- **OpenAI API兼容**: 完全兼容OpenAI聊天完成接口格式
- **延迟注入**: 模拟网络延迟，测试应用响应时间和超时处理
- **故障注入**: 模拟各种错误场景，验证错误处理机制
- **灵活配置**: 支持环境变量和运行时配置
- **现代化架构**: 基于FastAPI和Pydantic V2构建
- **完整测试**: 包含单元测试和集成测试
- **Docker支持**: 提供Docker和Docker Compose部署方案

## 🏗️ 技术架构

### 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.13+ | 编程语言 |
| FastAPI | 0.115.0+ | Web框架 |
| Pydantic | 2.7.0+ | 数据验证 |
| Uvicorn | 0.30.0+ | ASGI服务器 |
| Pytest | 8.2.0+ | 测试框架 |
| Docker | - | 容器化部署 |

### 架构设计

```
┌─────────────────────────────────────────┐
│           客户端应用                    │
└─────────────────┬───────────────────────┘
                  │ HTTP请求
                  ▼
┌─────────────────────────────────────────┐
│         FastAPI 应用层                 │
│  ┌─────────────────────────────────┐   │
│  │   API 路由层 (app/api/)        │   │
│  │   - 聊天接口                    │   │
│  │   - 配置管理接口                │   │
│  └─────────────┬───────────────────┘   │
│                │                       │
│  ┌─────────────▼───────────────────┐   │
│  │   服务层 (app/services/)        │   │
│  │   - 模拟响应逻辑                │   │
│  │   - 延迟注入                    │   │
│  │   - 故障注入                    │   │
│  └─────────────┬───────────────────┘   │
│                │                       │
│  ┌─────────────▼───────────────────┐   │
│  │   配置层 (app/config.py)        │   │
│  │   - 环境变量管理                │   │
│  │   - 配置验证                    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 📂 项目结构

```
llm-mock-server/
├── app/                      # 应用主目录
│   ├── __init__.py           # 应用包初始化
│   ├── main.py               # FastAPI应用入口
│   ├── config.py             # 配置管理
│   ├── models.py             # 数据模型定义
│   ├── api/                  # API路由
│   │   ├── __init__.py
│   │   └── chat.py          # 聊天相关接口
│   └── services/             # 业务逻辑
│       ├── __init__.py
│       ├── mock_service.py  # 模拟服务实现
│       └── response_config_manager.py # YAML配置管理
├── tests/                   # 测试目录
│   ├── unit/                # 单元测试
│   ├── integration/         # 集成测试
│   └── fixtures/            # 测试数据
├── scripts/                 # 脚本工具
│   ├── check_dependencies.py
│   ├── start.bat
│   └── start_server.py
├── docs/                    # 文档目录
│   ├── api.md              # API文档
│   ├── deployment.md       # 部署文档
│   ├── injection_features.md # 注入功能说明
│   └── yaml_config_features.md # YAML配置功能说明
├── config/                  # 配置文件
│   ├── responses.yaml      # YAML回复配置
│   ├── responses.yaml.example # 配置示例
│   ├── test_responses.yaml # 测试配置
│   └── test_responses.yaml.template # 测试配置模板
├── .env                    # 环境变量配置
├── .env.example            # 环境变量示例
├── Dockerfile              # Docker镜像构建
├── docker-compose.yml      # Docker编排
├── pyproject.toml          # 项目配置
└── README.md              # 项目说明
```

## 🚀 快速开始

### 环境要求

- Python 3.13 或更高版本
- pip 包管理器
- (可选) Docker 和 Docker Compose

### 本地安装

1. **克隆仓库**
```bash
git clone <repository-url>
cd llm-mock-server
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -e .[dev]
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件设置你的配置
```

5. **启动服务器**
```bash
python scripts/start_server.py
```

### Docker部署

1. **使用Docker Compose（推荐）**
```bash
docker-compose up -d
```

2. **使用Docker命令**
```bash
docker build -t mock-llm-server .
docker run -d -p 8000:8000 --name mock-llm-server mock-llm-server
```

**Docker特性**：
- 多阶段构建，优化镜像大小
- 非root用户运行，提高安全性  
- 内建健康检查，自动监控服务状态
- 支持外部配置文件挂载
- 自动日志轮转（最大10MB，保留3个文件）

## 🔧 功能说明

### 1. 基础聊天功能

提供与OpenAI兼容的聊天完成接口：

```bash
POST /v1/chat/completions
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hello"}
  ],
  "model": "mock-model",
  "temperature": 1.0,
  "max_tokens": 100
}
```

### 2. 延迟注入

模拟网络延迟，测试应用的响应时间处理能力：

```bash
PUT /v1/config/injection
Content-Type: application/json

{
  "delay": {
    "enabled": true,
    "min_delay_ms": 100,
    "max_delay_ms": 500
  }
}
```

### 3. 故障注入

模拟各种错误场景：

- **HTTP错误**: 返回指定的HTTP状态码
- **超时**: 模拟长时间等待
- **无效响应**: 返回不符合规范的响应
- **空响应**: 返回空的choices数组

```bash
PUT /v1/config/injection
Content-Type: application/json

{
  "fault": {
    "enabled": true,
    "fault_type": "http_error",
    "http_status_code": 503,
    "error_message": "Service unavailable",
    "probability": 0.5
  }
}
```

### 4. 配置管理

- **获取配置**: `GET /v1/config/injection`
- **更新配置**: `PUT /v1/config/injection`
- **重置配置**: `POST /v1/config/injection/reset`

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行带覆盖率报告的测试
pytest tests/ --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/unit/test_services.py -v

# 运行特定测试类
pytest tests/unit/test_services.py::TestMockService -v
```

### 测试结构

- **单元测试**: 测试单个组件的功能
- **集成测试**: 测试组件间的交互
- **测试夹具**: 提供共享的测试资源

## ⚙️ 配置说明

### 环境变量

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| APP_NAME | string | "Mock LLM Server" | 应用名称 |
| APP_VERSION | string | "1.0.0" | 应用版本 |
| HOST | string | "0.0.0.0" | 服务器主机地址 |
| PORT | integer | 8000 | 服务器端口 |
| DEBUG | boolean | false | 调试模式 |
| MOCK_RESPONSE | string | "This is a mock response." | 模拟响应内容 |
| LOG_LEVEL | string | "INFO" | 日志级别 |
| LOG_FORMAT | string | "json" | 日志格式 |

### 配置文件

创建 `.env` 文件来自定义配置：

```bash
APP_NAME=My Mock Server
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
DEBUG=false
MOCK_RESPONSE=自定义响应内容
LOG_LEVEL=INFO
```

## 📊 API端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 根路径，返回服务器信息 |
| `/health` | GET | 健康检查 |
| `/v1/chat/completions` | POST | 聊天完成接口 |
| `/v1/config/injection` | GET | 获取注入配置 |
| `/v1/config/injection` | PUT | 更新注入配置 |
| `/v1/config/injection/reset` | POST | 重置注入配置 |
| `/v1/config/yaml` | GET | 获取YAML配置 |
| `/v1/config/yaml/enable` | PUT | 启用YAML配置 |
| `/v1/config/yaml/disable` | PUT | 禁用YAML配置 |
| `/v1/config/yaml/reload` | POST | 重载YAML配置 |
| `/v1/config/yaml/validate` | POST | 验证YAML配置 |
| `/v1/config/yaml/rules` | POST | 添加YAML规则 |
| `/v1/config/yaml/rules/{index}` | DELETE | 删除YAML规则 |
| `/v1/config/yaml/rules/{index}` | PUT | 更新YAML规则 |
| `/v1/config/yaml/rules/{index}/enable` | PUT | 启用YAML规则 |
| `/v1/config/yaml/rules/{index}/disable` | PUT | 禁用YAML规则 |
| `/v1/config/yaml/rules/validate` | POST | 验证YAML规则 |
| `/v1/config/yaml/rules/search` | GET | 搜索YAML规则 |

## 🎨 使用场景

### 1. AI应用开发测试

在开发AI应用时，使用Mock Server模拟LLM响应，避免调用真实的API，节省成本。

### 2. 错误处理验证

通过故障注入功能，测试应用在各种错误场景下的处理能力。

### 3. 性能测试

使用延迟注入功能，模拟网络延迟，测试应用的性能表现。

### 4. 集成测试

在CI/CD流程中使用Mock Server，确保应用与LLM集成的稳定性。

## 🔍 监控和日志

### 健康检查

```bash
curl http://localhost:8000/health
```

### 查看日志

```bash
# Docker环境
docker logs -f mock-llm-server

# 本地环境
# 日志输出到控制台
```

## 🛠️ 开发指南

### 添加新功能

1. 在 `app/models.py` 中定义数据模型
2. 在 `app/services/` 中实现业务逻辑
3. 在 `app/api/` 中添加API路由
4. 在 `tests/` 中编写测试用例
5. 更新相关文档

### 代码规范

- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 使用 MyPy 进行类型检查

```bash
# 格式化代码
black app/ tests/

# 代码检查
flake8 app/ tests/

# 类型检查
mypy app/
```

## 📈 性能优化

### 建议配置

- **生产环境**: 关闭DEBUG模式，设置适当的日志级别
- **高并发**: 使用多个容器实例，配置负载均衡
- **资源限制**: 在Docker中设置CPU和内存限制

## 🔒 安全建议

1. **不要在生产环境启用DEBUG模式**
2. **使用HTTPS保护API通信**
3. **实施速率限制防止滥用**
4. **定期更新依赖包**
5. **保护敏感配置信息**

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

详细的开发日志请查看 [LOG.md](LOG.md)

## 📄 许可证

本项目采用 MIT 许可证

## 📞 联系方式

- 作者: XY
- 邮箱: your.email@example.com

## 🔗 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)

---

**注意**: 本项目仅用于测试目的，不提供真实的AI推理能力。