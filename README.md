# LLM Mock Server - AI应用测试工具

一个测试开发工程师学习AI应用测试的实践项目，包含完整的Mock Server实现、测试用例、桌面管理应用和开发日志。

## 🎯 项目简介

本项目是一个功能完整的LLM模拟服务器，专为测试AI应用而设计。它提供了与OpenAI API兼容的接口，支持延迟注入和故障注入功能，帮助开发者验证AI应用在各种场景下的行为。项目还包含一个功能完善的桌面管理应用，提供图形化界面来管理服务器、配置注入参数、查看日志和进行测试。

### 核心功能

- ✅ **OpenAI API兼容**: 完全兼容OpenAI聊天完成接口格式
- ✅ **流式响应**: 支持SSE流式输出，模拟真实LLM的打字效果
- ✅ **延迟注入**: 模拟网络延迟，测试应用响应时间和超时处理
- ✅ **故障注入**: 模拟HTTP错误、超时、无效响应等多种错误场景
- ✅ **日志系统**: 完整的请求、错误和访问日志记录与查询
- ✅ **灵活配置**: 支持环境变量和运行时配置
- ✅ **完整测试**: 包含129个测试用例（单元测试和集成测试）
- ✅ **环境隔离**: 测试环境与生产环境完全隔离
- ✅ **Docker支持**: 提供Docker和Docker Compose部署方案
- ✅ **桌面管理应用**: 功能完善的图形化管理界面

## 🚀 快速开始

### 环境要求

- Python 3.13+
- pip

### 本地安装

```bash
# 1. 克隆仓库
git clone <repository-url>
cd llm-mock-server

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -e .[dev]

# 4. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件设置你的配置

# 5. 启动服务器
python scripts/start_server.py

# 6. 启动桌面应用（可选）
python desktop/main.py
# 或使用批处理文件（Windows）
start_desktop.bat
```

### 打包成可执行文件

将整个项目（包括后端服务器和桌面应用）打包成独立的可执行文件：

**Windows**:
```bash
# 运行打包脚本
build.bat

# 打包完成后，可执行文件位于：
# dist\LLM_Mock_Server.exe
```

**Linux/Mac**:
```bash
# 运行打包脚本
chmod +x build.sh
./build.sh

# 打包完成后，可执行文件位于：
# dist/LLM_Mock_Server
```

**分发说明**:
- 打包后的可执行文件包含所有依赖和资源
- 用户无需安装 Python 即可直接运行
- 双击运行即可启动桌面应用和后端服务器

详细的打包指南请查看 [BUILD_GUIDE.md](BUILD_GUIDE.md)

### Docker部署

```bash
# 使用Docker Compose（推荐）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 或使用Docker命令
docker build -t mock-llm-server .
docker run -d -p 8000:8000 --name mock-llm-server mock-llm-server
```

**Docker特性**：
- 多阶段构建，优化镜像大小
- 非root用户运行，提高安全性
- 内建健康检查，自动监控服务状态
- 支持外部配置文件挂载
- 自动日志轮转（最大10MB，保留5个文件）

## 📚 使用示例

### 基础聊天请求

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

### 流式响应请求

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

### 查询日志

```bash
# 获取所有日志
curl http://localhost:8000/v1/logs

# 获取请求日志
curl "http://localhost:8000/v1/logs?log_type=request"

# 获取错误日志，限制返回10条
curl "http://localhost:8000/v1/logs?log_type=error&limit=10"
```

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
      "error_message": "服务不可用",
      "probability": 0.5
    }
  }'
```

### YAML配置管理

```bash
# 启用YAML配置
curl -X PUT http://localhost:8000/v1/config/yaml/enable

# 添加规则
curl -X POST http://localhost:8000/v1/config/yaml/rules \
  -H "Content-Type: application/json" \
  -d '{
    "trigger": "你好",
    "response": "你好！有什么可以帮助你的吗？",
    "match_type": "exact",
    "enabled": true
  }'

# 搜索规则
curl "http://localhost:8000/v1/config/yaml/rules/search?keyword=你好"
```

## 🧪 运行测试

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

**测试统计**：
- 总计：129个测试用例
- 单元测试：62个
- 集成测试：67个
- 测试覆盖率：90%+

## 📖 文档

- [项目说明文档](PROJECT_GUIDE.md) - 完整的项目说明
- [桌面应用文档](desktop/README.md) - 桌面管理应用说明
- [API文档](docs/api.md) - API接口详细说明
- [部署指南](docs/deployment.md) - 部署和运维指南
- [注入功能说明](docs/injection_features.md) - 延迟和故障注入功能详解
- [YAML配置功能说明](docs/yaml_config_features.md) - YAML配置功能详解
- [测试系统说明](docs/test_system.md) - 测试系统详细说明

## 🎓 学习历程

### 项目背景

作为一个测试开发工程师，我想探索：
- 一个测试开发工程师能否自己动手理解和实现Agent和RAG
- 如何为AI应用设计有效的测试工具
- 如何使用AI辅助开发提高效率

### 相关项目

#### 1. 多智能体旅行规划助手
基于LangGraph实现的多智能体系统，能够完成：
- 机票查询
- 酒店预订
- 行程邮件生成
- 全流程任务编排

**测试计划**：
- 使用Mock Server模拟各种异常（超时、报错、卡死）
- 编写pytest用例确保系统稳定性

#### 2. RAG问答系统
完整的RAG问答流程实现：
- Ollama本地模型部署
- Qdrant向量库搭建
- Snowflake Embedding接入
- 文档切片检索与生成

**测试计划**：
- 系统评估不同切片策略的效果
- 增加鲁棒性测试（空文档、超长上下文）

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.13+ | 编程语言 |
| FastAPI | 0.115.0+ | Web框架 |
| Pydantic | 2.7.0+ | 数据验证 |
| Uvicorn | 0.30.0+ | ASGI服务器 |
| Pytest | 8.2.0+ | 测试框架 |
| PyQt6 | 6.6.0+ | 桌面应用GUI框架 |
| httpx | 0.27.0+ | HTTP客户端 |

## 📊 项目结构

```
llm-mock-server/
├── app/                      # 应用主目录
│   ├── api/                  # API路由
│   │   ├── chat.py          # 聊天和配置接口
│   │   └── logs.py          # 日志接口
│   ├── services/             # 业务逻辑
│   │   ├── mock_service.py  # 模拟服务
│   │   ├── response_config_manager.py # YAML配置管理
│   │   └── log_manager.py   # 日志管理
│   ├── config.py             # 配置管理
│   ├── models.py             # 数据模型
│   └── main.py               # 应用入口
├── desktop/                  # 桌面应用
│   ├── main.py              # 应用入口
│   ├── config/              # 配置模块
│   ├── ui/                  # 用户界面
│   │   ├── main_window.py   # 主窗口
│   │   ├── server_tab.py    # 服务器管理
│   │   ├── config_tab.py    # 配置管理
│   │   ├── logs_tab.py      # 日志查看
│   │   ├── test_tab.py      # 测试界面
│   │   ├── monitor_tab.py   # 性能监控
│   │   └── rule_edit_dialog.py # 规则编辑对话框
│   └── services/            # 服务模块
│       ├── api_client.py    # API客户端
│       └── server_manager.py # 服务器管理
├── tests/                    # 测试目录
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── fixtures/             # 测试数据
├── scripts/                  # 脚本工具
├── docs/                     # 文档目录
├── config/                   # 配置文件
├── logs/                     # 日志目录
└── pyproject.toml           # 项目配置
```

## 🎯 项目完成度

### 后端服务器 
- ✅ OpenAI API兼容接口
- ✅ 流式和非流式响应
- ✅ 延迟注入（可配置随机延迟）
- ✅ 故障注入（4种故障类型）
- ✅ YAML配置管理（12个API端点）
- ✅ 完整的日志系统
- ✅ 环境隔离机制
- ✅ Docker支持

### 桌面应用 
- ✅ 主窗口框架
- ✅ 服务器管理（启动/停止/重启/状态监控）
- ✅ 配置管理（延迟/故障/YAML配置）
- ✅ 日志查看（实时显示/过滤/搜索/导出）
- ✅ 测试界面（聊天/流式/批量/性能测试）
- ✅ 性能监控（实时指标/统计/错误显示）
- ⚠️ 桌面应用测试（待添加）

### 测试体系 
- ✅ 129个测试用例
- ✅ 单元测试和集成测试
- ✅ 测试环境隔离
- ⚠️ 桌面应用测试（待添加）
- ⚠️ 端到端测试（待添加）

### 文档体系 
- ✅ 完整的项目文档
- ✅ API文档
- ✅ 部署指南
- ✅ 功能说明文档

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📝 开发日志

详细的开发日志请查看 [LOG.md](LOG.md)

## 📄 许可证

本项目采用 MIT 许可证

---

**作者**: XY  
**日期**: 2026.04  
**项目状态**: 积极开发中