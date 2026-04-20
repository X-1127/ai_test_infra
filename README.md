# LLM Mock Server - AI应用测试工具

一个测试开发工程师学习AI应用测试的实践项目，包含完整的Mock Server实现、测试用例和开发日志。

## 🎯 项目简介

本项目是一个功能完整的LLM模拟服务器，专为测试AI应用而设计。它提供了与OpenAI API兼容的接口，支持延迟注入和故障注入功能，帮助开发者验证AI应用在各种场景下的行为。

### 核心功能

- ✅ **OpenAI API兼容**: 完全兼容OpenAI聊天完成接口格式
- ✅ **延迟注入**: 模拟网络延迟，测试应用响应时间和超时处理
- ✅ **故障注入**: 模拟HTTP错误、超时、无效响应等多种错误场景
- ✅ **灵活配置**: 支持环境变量和运行时配置
- ✅ **完整测试**: 包含单元测试和集成测试
- ✅ **Docker支持**: 提供Docker和Docker Compose部署方案

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
```

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
- 自动日志轮转（最大10MB，保留3个文件）

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

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行带覆盖率报告的测试
pytest tests/ --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/unit/test_services.py -v
```

## 📖 文档

- [项目说明文档](PROJECT_GUIDE.md) - 完整的项目说明
- [API文档](docs/api.md) - API接口详细说明
- [部署指南](docs/deployment.md) - 部署和运维指南
- [注入功能说明](docs/injection_features.md) - 延迟和故障注入功能详解
- [YAML配置功能说明](docs/yaml_config_features.md) - YAML配置功能详解

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

## 📊 项目结构

```
llm-mock-server/
├── app/                      # 应用主目录
│   ├── api/                  # API路由
│   ├── services/             # 业务逻辑
│   ├── config.py             # 配置管理
│   ├── models.py             # 数据模型
│   └── main.py               # 应用入口
├── tests/                    # 测试目录
│   ├── unit/                 # 单元测试
│   ├── integration/          # 集成测试
│   └── fixtures/             # 测试数据
├── scripts/                  # 脚本工具
├── docs/                     # 文档目录
├── config/                   # 配置文件
└── pyproject.toml           # 项目配置
```

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📝 开发日志

详细的开发日志请查看 [LOG.md](LOG.md)

## 📄 许可证

本项目采用 MIT 许可证

---

**作者**: XY  
**日期**: 2026.04  
**项目状态**: 活跃开发中