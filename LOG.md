## 2026-04-17

**目标**：1.用 trae 生成 Mock Server 骨架
          2.学习FastAPI的/chat/completions标准格式

- 做了一个分阶段的规划：

| 阶段 | 内容 |
|------|------|
| 0 | 环境准备 |
| 1 | 固定响应 MVP |
| 2 | 延迟注入 |
| 3 | 故障注入（错误码） |
| 4 | YAML 配置预设回复 |
| 5 | 流式响应 |
| 6 | 请求日志记录 |
| 7 | 测试 + Docker |
| 8 | CI/CD集成 |

**已完成的工作**：

- ✅ 阶段0：环境准备
    - 创建项目目录 llm-mock-server
    - 创建 Python 虚拟环境
    - 安装依赖（FastAPI, uvicorn, pydantic, pyyaml, httpx, pytest, pytest-asyncio）
    - 生成 requirements.txt

- ✅ 阶段1：固定响应 MVP
    - 实现 POST /v1/chat/completions 接口，返回 OpenAI 格式固定响应
    - 支持环境变量 MOCK_RESPONSE 自定义回复内容
    - 添加 /health 健康检查和根路径状态接口
    - 生成配套文件：test_main.py（单元测试）、simple_test.py（快速测试脚本）、README.md、start.bat
    - 成功启动服务器，浏览器访问 http://localhost:8000/ 返回 `{"status":"ok",...}`

**卡点**：
- 在尝试阶段2的时候遇到了服务器卡死的问题，尚不清楚原因；
- 是否能让延迟可配置？能不能做到随机延迟？延迟上限合理的值是什么？都还不清楚


**明日计划**：重构test_app.py，使用pytest测试类

## 2026-04-18

**目标**：重构test_app.py，使用pytest测试类

**已完成的工作**：

- ✅ 项目结构重构
    - 创建server子文件夹，将所有代码文件迁移到server目录
    - 更新start.bat脚本，适配新的目录结构

- ✅ 测试框架搭建
    - 创建server/tests文件夹，建立标准pytest测试结构
    - 创建server/tests/__init__.py空文件
    - 创建server/tests/conftest.py，包含共享fixtures
    - 重构所有测试文件，移除手动创建的client实例，改用pytest fixtures
    - 创建pytest.ini配置文件，设置测试路径和命名规则

- ✅ 测试文件重构
    - test_main.py：主要API测试，使用client fixture
    - test_simple.py：简单测试，重构成pytest测试类
    - test_quick.py：快速测试，重构成pytest测试类
    - test_manual.py：手动测试，重构成pytest测试类
    - test_client_integration.py：客户端集成测试，使用asyncio
    - test_app.py：应用测试，重构成pytest测试类

**卡点**：
- 笔者今日一次性拔了四颗智齿，疼痛难忍导致无法正常工作
- 休息半天，复习一下FastAPI的相关内容



**明日计划**：重构项目文件结构，学习阶段2（延迟注入）前置知识

## 2026-04-19

**目标**：项目完全重构，建立现代化Python项目结构，学习阶段2（延迟注入）前置知识

**已完成的工作**：

- ✅ 项目完全重构
    - 创建新的目录结构：
        - `app/` - 应用主目录（main.py, config.py, models.py, api/, services/）
        - `tests/` - 测试目录（unit/, integration/, fixtures/）
        - `scripts/` - 脚本工具目录
        - `docs/` - 文档目录
        - `logs/` - 日志目录
    - 删除旧的 `server/` 目录
    - 创建完整的配置文件：`pyproject.toml`, `.env`, `.env.example`
    - 创建 Docker 支持：`Dockerfile`, `docker-compose.yml`

- ✅ 模块化设计
    - `app/main.py` - FastAPI 应用入口
    - `app/config.py` - 配置管理
    - `app/models.py` - Pydantic 数据模型
    - `app/api/chat.py` - 聊天 API 路由
    - `app/services/mock_service.py` - 模拟服务业务逻辑

- ✅ 配置管理优化
    - **切换到 Pydantic V2**：使用 `pydantic_settings.BaseSettings` 和 `SettingsConfigDict`
    - **增强配置验证**：添加 `@field_validator` 处理各种布尔值格式
    - **移除过时语法**：不再使用 `Field(default=..., env=...)` 的过时写法

- ✅ 功能验证
    - 成功启动服务器：`python scripts/start_server.py`
    - 验证健康检查端点：`http://localhost:8000/health`
    - 验证根路径：`http://localhost:8000/`
    - 验证聊天接口：`http://localhost:8000/v1/chat/completions`
    - 验证 API 文档：`http://localhost:8000/docs`

**遇到的问题和解决方案**：


1. **Pydantic V2 弃用警告**
    - 问题：使用了过时的 Pydantic V1 语法
    - 解决：迁移到 Pydantic V2 语法

2. **文件管理混乱**
    - 问题：存在大量中间测试文件和旧代码
    - 解决：系统化清理，删除所有不必要的文件和目录


**明日计划**：
1. 继续完善 Mock Server 功能，进入阶段2（延迟注入）
2. 添加对应阶段2的测试用例覆盖
3. 实现日志系统
4. 探索延迟注入的可配置性和随机延迟实现