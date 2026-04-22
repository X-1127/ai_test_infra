# LLM Mock Server Backend

LLM Mock Server 后端服务器 - OpenAI API 兼容的模拟服务器。

## 功能特性

- ✅ OpenAI API 兼容的聊天接口
- ✅ 流式和非流式响应
- ✅ 延迟注入（可配置随机延迟）
- ✅ 故障注入（4种故障类型）
- ✅ YAML 配置管理（12个API端点）
- ✅ 完整的日志系统
- ✅ 环境隔离机制
- ✅ Docker 支持

## 快速开始

### 环境要求

- Python 3.13+
- pip

### 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"
```

### 启动服务器

```bash
# 使用 Python 直接启动
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 或使用启动脚本
python scripts/start_server.py
```

### Docker 部署

```bash
# 使用 Docker
docker build -t llm-mock-backend .
docker run -p 8000:8000 llm-mock-backend

# 使用 Docker Compose
docker-compose up -d
```

## API 文档

启动服务器后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试

```bash
# 运行所有测试（需要在 backend 目录下）
cd backend
pytest tests/ -v

# 运行带覆盖率报告的测试
pytest tests/ --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/unit/test_services.py -v
```

## 配置

### 环境变量

```bash
# .env 文件
DEBUG=true
LOG_LEVEL=info
HOST=0.0.0.0
PORT=8000
```

### YAML 配置

```bash
# 启用 YAML 配置
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
```

## 延迟注入

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

## 故障注入

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

## 日志查询

```bash
# 获取所有日志
curl http://localhost:8000/v1/logs

# 获取请求日志
curl "http://localhost:8000/v1/logs?log_type=request"

# 获取错误日志，限制返回10条
curl "http://localhost:8000/v1/logs?log_type=error&limit=10"
```

## 项目结构

```
backend/
├── app/                    # 应用代码
│   ├── api/               # API 路由
│   ├── services/          # 业务逻辑
│   ├── config.py          # 配置管理
│   ├── main.py            # 应用入口
│   └── models.py          # 数据模型
├── config/                # 配置文件
├── tests/                 # 测试代码
│   ├── unit/             # 单元测试
│   └── integration/      # 集成测试
├── scripts/              # 工具脚本
├── Dockerfile            # Docker 配置
├── docker-compose.yml    # Docker Compose 配置
└── pyproject.toml        # 项目配置
```

## 开发

### 代码风格

```bash
# 格式化代码
black app/ tests/

# 检查代码风格
flake8 app/ tests/

# 类型检查
mypy app/
```

### 添加新功能

1. 在 `app/api/` 中添加新的路由
2. 在 `app/services/` 中添加业务逻辑
3. 在 `tests/` 中添加测试
4. 更新文档

## 许可证

MIT License