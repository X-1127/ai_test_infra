# LLM Mock Server 项目说明文档

## 📋 项目概述

**LLM Mock Server** 是一个专为测试AI应用而设计的模拟LLM服务器。它提供了与OpenAI API兼容的接口，支持延迟注入和故障注入功能，帮助开发者测试和验证AI应用在各种网络条件和错误场景下的行为。项目还包含一个功能完善的桌面管理应用，提供图形化界面来管理服务器、配置注入参数、查看日志和进行测试。

### 🎯 核心特性

- **OpenAI API兼容**: 完全兼容OpenAI聊天完成接口格式
- **流式响应**: 支持SSE流式输出，模拟真实LLM的打字效果
- **延迟注入**: 模拟网络延迟，测试应用响应时间和超时处理
- **故障注入**: 模拟各种错误场景，验证错误处理机制
- **日志系统**: 完整的请求、错误和访问日志记录与查询
- **灵活配置**: 支持环境变量和运行时配置
- **YAML配置**: 支持通过YAML文件配置预设回复规则
- **现代化架构**: 基于FastAPI和Pydantic V2构建
- **完整测试**: 包含129个测试用例（单元测试和集成测试）
- **环境隔离**: 测试环境与生产环境完全隔离
- **Docker支持**: 提供Docker和Docker Compose部署方案
- **桌面管理应用**: 功能完善的图形化管理界面

## 🏗️ 技术架构

### 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.13+ | 编程语言 |
| FastAPI | 0.115.0+ | Web框架 |
| Pydantic | 2.7.0+ | 数据验证 |
| Uvicorn | 0.30.0+ | ASGI服务器 |
| Pytest | 8.2.0+ | 测试框架 |
| PyQt6 | 6.6.0+ | 桌面应用GUI框架 |
| httpx | 0.27.0+ | HTTP客户端 |
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
│  │   - 日志接口                    │   │
│  └─────────────┬───────────────────┘   │
│                │                       │
│  ┌─────────────▼───────────────────┐   │
│  │   服务层 (app/services/)        │   │
│  │   - 模拟响应逻辑                │   │
│  │   - 延迟注入                    │   │
│  │   - 故障注入                    │   │
│  │   - YAML配置管理                │   │
│  │   - 日志管理                    │   │
│  └─────────────┬───────────────────┘   │
│                │                       │
│  ┌─────────────▼───────────────────┐   │
│  │   配置层 (app/config.py)        │   │
│  │   - 环境变量管理                │   │
│  │   - 配置验证                    │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         桌面管理应用                  │
│  ┌─────────────────────────────────┐   │
│  │   UI层 (desktop/ui/)          │   │
│  │   - 主窗口                    │   │
│  │   - 服务器管理标签页            │   │
│  │   - 配置管理标签页              │   │
│  │   - 日志查看标签页              │   │
│  │   - 测试界面标签页              │   │
│  │   - 性能监控标签页              │   │
│  └─────────────┬───────────────────┘   │
│                │                       │
│  ┌─────────────▼───────────────────┐   │
│  │   服务层 (desktop/services/)   │   │
│  │   - API客户端                  │   │
│  │   - 服务器管理器                │   │
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
│   │   ├── chat.py          # 聊天和配置接口
│   │   └── logs.py          # 日志接口
│   └── services/             # 业务逻辑
│       ├── __init__.py
│       ├── mock_service.py  # 模拟服务实现
│       ├── response_config_manager.py # YAML配置管理
│       └── log_manager.py   # 日志管理
├── desktop/                  # 桌面应用
│   ├── __init__.py
│   ├── main.py              # 桌面应用入口
│   ├── config/              # 桌面应用配置
│   │   ├── __init__.py
│   │   └── settings.py      # 桌面应用设置
│   ├── ui/                  # 用户界面
│   │   ├── __init__.py
│   │   ├── main_window.py   # 主窗口
│   │   ├── server_tab.py    # 服务器管理标签页
│   │   ├── config_tab.py    # 配置管理标签页
│   │   ├── logs_tab.py      # 日志查看标签页
│   │   ├── test_tab.py      # 测试界面标签页
│   │   ├── monitor_tab.py   # 性能监控标签页
│   │   └── rule_edit_dialog.py # 规则编辑对话框
│   └── services/            # 桌面应用服务
│       ├── __init__.py
│       ├── api_client.py    # API客户端
│       └── server_manager.py # 服务器管理
├── tests/                   # 测试目录
│   ├── __init__.py
│   ├── conftest.py          # 测试配置和夹具
│   ├── unit/                # 单元测试
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_response_config_manager.py
│   ├── integration/         # 集成测试
│   │   ├── test_api.py
│   │   ├── test_yaml_config_api.py
│   │   └── test_logs_api.py
│   └── fixtures/            # 测试数据
│       └── test_data.json
├── scripts/                 # 脚本工具
│   ├── check_dependencies.py
│   ├── start.bat
│   └── start_server.py
├── docs/                    # 文档目录
│   ├── api.md              # API文档
│   ├── deployment.md       # 部署文档
│   ├── injection_features.md # 注入功能说明
│   ├── yaml_config_features.md # YAML配置功能说明
│   ├── test_system.md      # 测试系统说明
│   ├── performance_analysis.md # 性能分析
│   └── performance_guide.md # 性能优化指南
├── config/                  # 配置文件
│   ├── responses.yaml      # YAML回复配置
│   ├── responses.yaml.example # 配置示例
│   ├── test_responses.yaml # 测试配置
│   └── test_responses.yaml.template # 测试配置模板
├── logs/                     # 日志目录
│   ├── access.log
│   ├── error.log
│   └── request.log
├── .env                    # 环境变量配置
├── .env.example            # 环境变量示例
├── .gitignore
├── Dockerfile              # Docker镜像构建
├── docker-compose.yml      # Docker编排
├── pyproject.toml          # 项目配置
├── README.md              # 项目说明
├── PROJECT_GUIDE.md       # 项目说明文档
├── DESKTOP_APP_PLAN.md   # 桌面应用开发计划
├── LOG.md                # 开发日志
└── start_desktop.bat     # 桌面应用启动脚本
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

6. **启动桌面应用（可选）**
```bash
python desktop/main.py
# 或使用批处理文件（Windows）
start_desktop.bat
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
- 自动日志轮转（最大10MB，保留5个文件）

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
  "max_tokens": 100,
  "stream": false
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

### 4. YAML配置管理

支持通过YAML文件配置预设回复规则：

- **精确匹配**: 用户输入必须完全匹配触发词
- **包含匹配**: 用户输入包含触发词即可
- **正则匹配**: 支持复杂的正则表达式

```bash
# 启用YAML配置
PUT /v1/config/yaml/enable

# 添加规则
POST /v1/config/yaml/rules
{
  "trigger": "你好",
  "response": "你好！有什么可以帮助你的吗？",
  "match_type": "exact",
  "enabled": true
}

# 搜索规则
GET /v1/config/yaml/rules/search?keyword=你好
```

### 5. 日志系统

完整的日志记录和查询功能：

- **请求日志**: 记录所有API请求
- **错误日志**: 记录所有错误信息
- **访问日志**: 记录访问信息
- **日志搜索**: 支持关键词搜索
- **日志统计**: 提供统计分析

```bash
# 获取日志
GET /v1/logs?log_type=request&limit=100

# 搜索日志
POST /v1/logs/search
{
  "keyword": "error",
  "log_type": "error",
  "limit": 10
}

# 获取统计
GET /v1/logs/stats
```

### 6. 配置管理

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

### 测试统计

- 总计：129个测试用例
- 单元测试：62个
- 集成测试：67个
- 测试覆盖率：90%+

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
| TESTING | boolean | false | 测试环境标识 |

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

### 聊天接口
| 端点 | 方法 | 描述 |
|------|------|------|
| `/v1/chat/completions` | POST | 聊天完成接口（支持流式和非流式）|

### 配置管理接口
| 端点 | 方法 | 描述 |
|------|------|------|
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

### 日志接口
| 端点 | 方法 | 描述 |
|------|------|------|
| `/v1/logs` | GET | 获取日志记录 |
| `/v1/logs/query` | POST | 查询日志 |
| `/v1/logs/search` | POST | 搜索日志 |
| `/v1/logs/stats` | GET | 获取日志统计 |
| `/v1/logs` | DELETE | 清空日志 |
| `/v1/logs/file/{log_type}` | GET | 获取日志文件路径 |

### 系统接口
| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 根路径，返回服务器信息 |
| `/health` | GET | 健康检查 |

## 🎨 使用场景

### 1. AI应用开发测试

在开发AI应用时，使用Mock Server模拟LLM响应，避免调用真实的API，节省成本。

### 2. 错误处理验证

通过故障注入功能，测试应用在各种错误场景下的处理能力。

### 3. 性能测试

使用延迟注入功能，模拟网络延迟，测试应用的性能表现。

### 4. 集成测试

在CI/CD流程中使用Mock Server，确保应用与LLM集成的稳定性。

### 5. 桌面管理

使用桌面应用进行可视化的服务器管理、配置调整、日志查看和功能测试。

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
# 日志输出到控制台和文件
```

### 桌面应用监控

使用桌面应用的性能监控功能：
- 实时性能指标
- 请求统计
- 响应时间统计
- 错误率统计
- 最近错误显示

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
black app/ tests/ desktop/

# 代码检查
flake8 app/ tests/ desktop/

# 类型检查
mypy app/
```

## 📈 性能优化

### 建议配置

- **生产环境**: 关闭DEBUG模式，设置适当的日志级别
- **高并发**: 使用多个容器实例，配置负载均衡
- **资源限制**: 在Docker中设置CPU和内存限制

### 性能特性

- YAML配置规则索引优化
- 正则表达式缓存
- 异步请求处理
- 日志内存缓存（最多1000条）
- 日志文件轮转（10MB，保留5个文件）

## 🔒 安全建议

1. **不要在生产环境启用DEBUG模式**
2. **使用HTTPS保护API通信**
3. **实施速率限制防止滥用**
4. **定期更新依赖包**
5. **保护敏感配置信息**
6. **限制API访问IP**

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
- 邮箱: 2162314757@qq.com

## 🔗 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)
- [PyQt6 文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

---

**注意**: 本项目仅用于测试目的，不提供真实的AI推理能力。