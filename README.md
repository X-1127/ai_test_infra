# LLM Mock Server

一个测试开发工程师学习AI应用测试的实践项目，包含完整的Mock Server实现、测试用例、桌面管理应用和开发日志。

## 项目结构

本项目采用前后端分离的架构，包含三个独立的部分：

```
llm-mock-server/
├── backend/              # 后端服务器
│   ├── app/             # 应用代码
│   ├── config/          # 配置文件
│   ├── tests/           # 测试代码
│   ├── scripts/         # 工具脚本
│   ├── Dockerfile       # Docker 配置
│   ├── docker-compose.yml
│   ├── README.md        # 后端文档
│   └── pyproject.toml  # 后端项目配置
├── desktop-app/         # 桌面应用
│   ├── app/             # 应用代码
│   ├── scripts/         # 工具脚本
│   ├── build.spec       # 打包配置
│   ├── README.md        # 桌面应用文档
│   └── pyproject.toml  # 桌面应用项目配置
├── docs/                # 项目文档
├── README.md            # 项目总览
├── LOG.md              # 开发日志
└── .gitignore          # Git 忽略规则
```

## 快速开始

### 后端服务器

```bash
cd backend

# 安装依赖
pip install -e ".[dev]"

# 启动服务器
python scripts/start_server.py
# 或
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

详细文档：[backend/README.md](backend/README.md)

### 桌面应用

```bash
cd desktop-app

# 安装依赖
pip install -e ".[build]"

# 启动应用
python main.py
# 或
llm-mock-desktop
```

详细文档：[desktop-app/README.md](desktop-app/README.md)

## 功能特性

### 后端服务器

- ✅ OpenAI API 兼容的聊天接口
- ✅ 流式和非流式响应
- ✅ 延迟注入（可配置随机延迟）
- ✅ 故障注入（4种故障类型）
- ✅ YAML 配置管理（12个API端点）
- ✅ 完整的日志系统
- ✅ 环境隔离机制
- ✅ Docker 支持
- ✅ 完整的测试体系（129个测试用例）
- ✅ 完整的压测工具（4种压测场景）

### 桌面应用

- ✅ 服务器管理（启动/停止/重启/状态监控）
- ✅ 配置管理（延迟/故障/YAML配置）
- ✅ 日志查看（实时显示/过滤/搜索/导出）
- ✅ 测试界面（聊天/流式/批量/性能测试）
- ✅ 性能监控（实时指标/统计/错误显示）
- ✅ 可打包成独立可执行文件

## 部署方式

### 后端服务器

#### Docker 部署

```bash
cd backend

# 使用 Docker
docker build -t llm-mock-backend .
docker run -p 8000:8000 llm-mock-backend

# 使用 Docker Compose
docker-compose up -d
```

#### 本地部署

```bash
cd backend

# 安装依赖
pip install -e ".[dev]"

# 启动服务器
python scripts/start_server.py
```

### 桌面应用

#### 打包分发

```bash
cd desktop-app

# Windows
python scripts/build.bat

# Linux/Mac
python scripts/build.sh
```

打包完成后，可执行文件位于：
- Windows: `dist/LLM_Mock_Desktop.exe`
- Linux/Mac: `dist/LLM_Mock_Desktop`

用户可以直接运行可执行文件，无需安装 Python。

## 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest tests/ -v

# 运行带覆盖率报告的测试
pytest tests/ --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/unit/test_services.py -v
```

**测试统计**：
- 总计：129个测试用例
- 单元测试：62个
- 集成测试：67个
- 测试覆盖率：90%+

## 文档

- [后端服务器文档](backend/README.md) - 后端服务器详细说明
- [桌面应用文档](desktop-app/README.md) - 桌面应用详细说明
- [API文档](docs/api.md) - API接口详细说明
- [部署指南](docs/deployment.md) - 部署相关说明
- [功能说明](docs/) - 各功能模块详细说明

## 开发日志

详细的开发日志记录在 [LOG.md](LOG.md) 中，包含每日的开发进度、遇到的问题和解决方案。


## 使用场景

- 开发阶段：在没有真实 API 的情况下开发 AI 应用
- 测试阶段：测试各种边界条件和错误场景
- 演示阶段：在没有网络的情况下演示应用功能
- 成本控制：避免在开发测试中消耗真实的 API 配额
- 稳定性测试：模拟各种网络条件和服务器状态

## 技术栈

### 后端服务器

- FastAPI - Web 框架
- Uvicorn - ASGI 服务器
- Pydantic - 数据验证
- PyYAML - YAML 配置管理
- pytest - 测试框架

### 桌面应用

- PyQt6 - GUI 框架
- httpx - HTTP 客户端
- PyInstaller - 打包工具

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！