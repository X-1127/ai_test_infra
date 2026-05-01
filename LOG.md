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
3. 学习日志系统如何配置和使用
4. 探索延迟注入的可配置性和随机延迟实现

## 2026-04-20

**目标**：完成阶段2（延迟注入）、阶段3（故障注入）、阶段4（YAML配置预设回复），建立完整的测试体系和文档

**已完成的工作**：

- ✅ 阶段2：延迟注入功能实现
    - 实现 `DelayConfig` 数据模型，支持可配置的延迟范围
    - 在 `MockService` 中实现 `apply_delay()` 方法，支持随机延迟
    - 延迟时间在 `min_delay_ms` 和 `max_delay_ms` 之间随机生成
    - 添加延迟配置API端点：`GET/PUT /v1/config/injection`
    - 实现延迟配置重置功能：`POST /v1/config/injection/reset`
    - 添加延迟注入测试用例，验证延迟范围和效果

- ✅ 阶段3：故障注入功能实现
    - 实现 `FaultConfig` 数据模型，支持多种故障类型
    - 实现4种故障类型：
        - `http_error`：返回自定义HTTP状态码和错误消息
        - `timeout`：模拟长时间等待，返回504错误
        - `invalid_response`：返回不符合API规范的响应
        - `empty_response`：返回空的choices数组
    - 支持故障概率配置（0.0-1.0），可控制故障触发频率
    - 延迟和故障注入可组合使用，模拟真实复杂场景
    - 添加完整的故障注入测试用例，覆盖所有故障类型

- ✅ 阶段4：YAML配置预设回复功能实现
    - 创建 `ResponseConfigManager` 类，管理YAML配置文件
    - 实现3种匹配方式：
        - `exact`：精确匹配，用户输入必须完全匹配触发词
        - `contains`：包含匹配，用户输入包含触发词即可
        - `regex`：正则匹配，支持复杂的正则表达式
    - 实现12个YAML配置管理API端点：
        - 配置管理：获取、启用、禁用、重载YAML配置
        - 规则管理：添加、删除、更新、启用、禁用规则
        - 验证功能：验证配置和规则格式
        - 搜索功能：按关键词和类型搜索规则
    - 支持配置热重载，无需重启服务器即可更新规则
    - 实现规则索引和正则表达式缓存，提升匹配性能

- ✅ 测试环境隔离机制
    - 实现三重环境检测：`PYTEST_XDIST_WORKER`、`PYTEST_CURRENT_TEST`、`TESTING`
    - 测试环境自动使用 `test_responses.yaml`，生产环境使用 `responses.yaml`
    - 每个测试前自动从模板恢复配置，确保测试独立性
    - 实现配置降级策略，测试配置缺失时自动使用默认配置

- ✅ 当前的测试体系建设
    - 单元测试：62个测试用例
        - `test_models.py`：测试数据模型（8个用例）
        - `test_services.py`：测试服务层（14个用例）
        - `test_response_config_manager.py`：测试配置管理（40个用例）
    - 集成测试：41个测试用例
        - `test_api.py`：测试API端点（15个用例）
        - `test_yaml_config_api.py`：测试YAML配置API（26个用例）
    - 总计103个测试用例，覆盖所有核心功能
    - 添加性能测试，验证100个规则的匹配性能

- ✅ 完善文档体系
    - `docs/api.md`（488行）：完整的API参考文档，包含所有端点说明和使用示例
    - `docs/deployment.md`（423行）：部署和运维指南，包含本地部署、Docker部署、生产环境配置
    - `docs/injection_features.md`（627行）：延迟和故障注入功能详解，包含配置参数和测试场景
    - `docs/yaml_config_features.md`（831行）：YAML配置功能说明，包含匹配规则和最佳实践
    - 更新 `README.md` 和 `PROJECT_GUIDE.md`，反映最新功能

- ✅ 配置文件完善
    - 创建 `config/responses.yaml`：生产环境配置，包含5个预设规则
    - 创建 `config/test_responses.yaml`：测试环境配置
    - 创建 `config/responses.yaml.example`：配置示例文件
    - 创建 `config/test_responses.yaml.template`：测试配置模板
    - 支持配置元数据管理（版本、描述、更新时间）

- ✅ 依赖检查工具
    - 创建 `scripts/check_dependencies.py`，检查所有依赖是否正确安装
    - 支持版本检测和错误提示
    - 提供安装建议和解决方案

**遇到的问题和解决方案**：

1. **性能问题**
    - 问题：设备本身性能影响延迟注入效果
    - 解决：改写延迟注入测试用例，验证延迟范围和效果，确保在不同设备上都能正常工作

2. **规则匹配效率问题**
    - 问题：规则数量多时匹配效率低，导致响应时间增加
    - 解决：按匹配类型建立规则索引，优先匹配精确匹配

3. **测试配置污染问题**
    - 问题：测试修改配置影响其他测试，导致测试结果不准确
    - 解决：每个测试前自动从模板恢复配置，使用autouse fixture

4. **YAML配置验证复杂**
    - 问题：配置文件格式错误难以定位
    - 解决：实现详细的配置验证API，返回具体的错误信息


**明日计划**：
1. 评估阶段5（流式响应）的实现方案和技术难点
2. 探索阶段6（请求日志记录）的设计和实现
3. 考虑添加CI/CD流程，自动测试和部署

## 2026-04-21

**目标**：完成阶段5（流式响应）、阶段6（请求日志记录）、阶段7（测试+Docker）、阶段8（CI/CD集成），开发桌面管理应用

**已完成的工作**：

- ✅ 阶段5：流式响应功能实现
    - 实现 SSE（Server-Sent Events）流式响应
    - 支持 OpenAI 标准的流式响应格式
    - 在 `MockService` 中实现 `generate_stream_response()` 方法
    - 添加流式响应测试用例，验证数据格式和传输
    - 支持非流式和流式响应的统一处理

- ✅ 阶段6：请求日志记录功能实现
    - 创建 `LogManager` 类，管理日志系统
    - 实现3种日志类型：
        - `request.log`：请求日志，记录所有API请求
        - `error.log`：错误日志，记录系统错误
        - `access.log`：访问日志，记录访问信息
    - 实现日志轮转机制：单个文件最大10MB，保留5个备份
    - 添加日志查询API：`GET /v1/logs`，支持按类型、限制、偏移查询
    - 实现日志搜索功能：`POST /v1/logs/search`，支持关键词搜索
    - 添加日志统计API：`GET /v1/logs/stats`，提供日志统计信息
    - 实现日志清空功能：`DELETE /v1/logs`
    - 支持JSON和文本两种日志格式

- ✅ 阶段7：测试+Docker完善
    - 扩展测试体系到129个测试用例
        - 单元测试：62个（test_models.py、test_services.py、test_response_config_manager.py）
        - 集成测试：67个（test_api.py、test_yaml_config_api.py、test_logs_api.py）
    - 添加日志管理测试：26个测试用例
    - 实现测试环境与生产环境的完全隔离
    - 完善 Docker 配置：
        - 多阶段构建，优化镜像大小
        - 非root用户运行，提高安全性
        - 内建健康检查，自动监控服务状态
        - 支持外部配置文件挂载
        - 自动日志轮转（最大10MB，保留5个文件）

- ✅ 阶段8：CI/CD集成准备
    - 创建完整的 GitHub Actions 配置示例
    - 添加自动化测试流程
    - 配置 Docker 镜像自动构建和推送
    - 实现代码质量检查（black、flake8、mypy）

- ✅ 桌面管理应用开发（接近完成）
    - **主窗口框架**：实现完整的主窗口和标签页布局
    - **服务器管理标签页**：
        - 服务器启动/停止/重启功能
        - 实时服务器状态监控
        - 自定义端口配置
        - 健康检查显示
        - 服务器输出实时显示
    - **配置管理标签页**：
        - 延迟注入配置界面
        - 故障注入配置界面
        - YAML配置管理界面
        - 规则编辑对话框
        - 规则表格显示
        - 规则管理功能（添加、编辑、删除、启用/禁用）
    - **日志查看标签页**：
        - 实时日志显示
        - 日志过滤功能
        - 日志搜索功能
        - 日志导出功能
    - **测试界面标签页**：
        - 聊天测试界面
        - 流式响应测试
        - 批量测试功能
        - 性能测试功能
    - **性能监控标签页**：
        - 实时指标显示
        - 统计信息展示
        - 错误显示


**遇到的问题和解决方案**：

1. **打包后服务器启动问题**
    - 问题：打包后启动服务器会打开新的控制台窗口
    - 解决：在打包环境中使用内部线程启动服务器，避免打开新窗口

2. **Docker 构建问题**
    - 问题：Docker 镜像包含不必要的桌面应用依赖
    - 解决：更新 .dockerignore，排除桌面应用相关文件

**项目总结**：

经过多天的开发，LLM Mock Server 项目已经完成了所有核心功能和大部分辅助功能：

**核心功能**：
- ✅ OpenAI API 兼容的聊天接口
- ✅ 流式和非流式响应
- ✅ 延迟注入（可配置随机延迟）
- ✅ 故障注入（4种故障类型）
- ✅ YAML 配置管理（12个API端点）
- ✅ 完整的日志系统
- ✅ 环境隔离机制
- ✅ Docker 支持

**辅助功能**：
- ✅ 功能完善的桌面管理应用（接近完成，在性能监控页面存在小BUG）
- ✅ 完整的打包功能，支持独立分发
- ✅ 129个测试用例


**待完成功能**：
- 端到端测试
- 性能监控页面BUG修复
- 可选：性能监控图表可视化

**今日感受**：笔者今日从早上6点开始的高强度开发，一杯茶一包烟，真真的赛过神仙了...还得考虑后续怎么把另外两个AI项目跟这个工具联动一下...

## 2026-04-22

**目标**：重构项目结构，实现前后端完全分离，每个部分独立管理，互不干扰。

**已完成的工作**：

- ✅ 项目结构重构
    - 创建 `backend/` 目录，包含后端服务器所有代码
    - 创建 `desktop-app/` 目录，包含桌面应用所有代码
    - 实现前后端完全分离，职责明确
    - 每个部分独立管理，互不干扰

- ✅ 后端服务器配置
    - 创建独立的 `backend/pyproject.toml`
    - 包含后端依赖和开发依赖
    - 配置测试框架和代码质量工具
    - 创建 `backend/README.md`，详细说明后端使用方法
    - 创建 `backend/Dockerfile`，支持 Docker 部署
    - 创建 `backend/docker-compose.yml`，简化部署流程
    - 移动后端代码到 `backend/` 目录
    - 移动测试代码到 `backend/tests/` 目录
    - 移动配置文件到 `backend/config/` 目录
    - 移动启动脚本到 `backend/scripts/` 目录

- ✅ 桌面应用配置
    - 创建独立的 `desktop-app/pyproject.toml`
    - 包含桌面应用依赖和打包依赖
    - 配置代码质量工具
    - 创建 `desktop-app/README.md`，详细说明桌面应用使用方法
    - 创建 `desktop-app/build.spec`，优化打包配置
    - 创建 `desktop-app/scripts/build.bat`，Windows 打包脚本
    - 移动桌面应用代码到 `desktop-app/app/` 目录
    - 移动主程序到 `desktop-app/main.py`

- ✅ 项目结构优化
    - 前后端完全分离，职责明确
    - 每个部分独立管理，互不干扰
    - Docker 只负责后端容器化
    - 打包功能独立，只服务于桌面应用
    - 测试体系集中在后端，桌面应用不做测试体系建设

 ✅ 进行压测，评估性能和稳定性
    - 使用工具Locust进行压测
    - 得到压测结果，所有报告保存在: loadtest_reports 目录下
    - 分析压测结果，评估性能和稳定性，总结至loadtest-report.md文件中
    
**新的项目结构**：

```
llm-mock-server/
├── backend/              # 后端服务器
│   ├── app/             # 应用代码
│   │   ├── api/        # API 路由
│   │   ├── services/   # 业务逻辑
│   │   ├── config.py   # 配置管理
│   │   ├── main.py     # 应用入口
│   │   └── models.py   # 数据模型
│   ├── config/          # 配置文件
│   ├── tests/           # 测试代码
│   │   ├── unit/      # 单元测试
│   │   └── integration/ # 集成测试
│   ├── scripts/         # 工具脚本
│   ├── Dockerfile       # Docker 配置
│   ├── docker-compose.yml
│   ├── README.md        # 后端文档
│   └── pyproject.toml  # 后端项目配置
├── desktop-app/         # 桌面应用
│   ├── app/             # 应用代码
│   │   ├── config/    # 配置管理
│   │   ├── services/  # 业务服务
│   │   └── ui/        # 用户界面
│   ├── scripts/         # 工具脚本
│   ├── build.spec       # 打包配置
│   ├── README.md        # 桌面应用文档
│   └── pyproject.toml  # 桌面应用项目配置
├── docs/                # 项目文档
│   ├── api.md          # API 文档
│   └── deployment.md   # 部署指南
├── README.md            # 项目总览
├── LOG.md              # 开发日志
└── .gitignore          # Git 忽略规则
```



**未来优化方向**：

1. 集成到 CI/CD 流程
2. 添加性能预警和告警功能
3. 继续压测，评估系统最大承载能力

**今日感受**：果然还是清晰简单的项目结构令人心旷神怡呀。

## 2026-04-23

**目标**：完成后端压测，评估系统性能和稳定性，生成压测报告

**已完成的工作**：

- ✅ 压测工具实现
    - 使用 Locust 框架实现完整的压测方案
    - 创建 `backend/tests/loadtest/locustfile.py`，包含多种用户类型和测试场景
    - 实现 `LLMChatUser`：模拟正常聊天用户（权重：基础3、流式2、健康检查1）
    - 实现 `StressTestUser`：压力测试用户（权重：快速聊天5、配置查询1）
    - 实现 `LongConversationUser`：长对话用户，模拟多轮对话
    - 创建 `backend/scripts/run_loadtest.py`，自动化压测脚本

- ✅ 压测场景设计
    - **基准测试**：10 users，获取系统性能基线数据
    - **负载测试**：逐步增加用户数（10→25→50→75→100），找到性能拐点
    - **稳定性测试**：50 users，长时间运行（1-2小时），检验系统稳定性
    - **压力测试**：逐步增加用户数（50→100→150→200→250→300），找出系统极限

- ✅ 压测脚本功能
    - 支持单个场景测试和全场景测试
    - 自动生成 HTML 报告和 CSV 统计文件
    - 实现失败率检查和阈值判断
    - 添加详细的调试信息和错误处理
    - 支持自定义测试参数（用户数、生成速率、运行时间）

- ✅ 压测执行和问题修复
    - 修复 Locust 错误：`with` 语句必须传递 `catch_response=True`
    - 修复 CSV 读取逻辑：正确识别 Aggregated 行（Type 为空，Name 为 "Aggregated"）
    - 增加超时时间：从 run_time + 60s 增加到 run_time + 120s
    - 添加异常处理和详细的堆栈跟踪信息
    - 修复循环逻辑，确保测试能够正确继续到下一个级别

- ✅ 压测结果分析
    - 完成所有 6 个压力测试等级（50-300 users）
    - 生成详细的压测报告：`backend/loadtest_reports/压测报告总结.md`
    - 系统在所有等级下表现优秀，失败率极低（0-0.008%）
    - 响应时间稳定（中位数 2-3ms，P95 160ms）
    - 吞吐量线性增长（62-375 RPS）

- ✅ 压测数据汇总

| 等级 | 用户数 | 总请求数 | 失败数 | 失败率 | 平均响应时间 | P95 | P99 | RPS |
|------|--------|-----------|---------|---------|-------------|-----|-----|-----|
| Level 1 | 50 | 7,376 | 0 | 0% | 32.87ms | 160ms | 2000ms | 62.05 |
| Level 2 | 100 | 15,084 | 0 | 0% | 33.02ms | 160ms | 2000ms | 127.12 |
| Level 3 | 150 | 22,463 | 0 | 0% | 33.43ms | 160ms | 2100ms | 189.25 |
| Level 4 | 200 | 29,892 | 0 | 0% | 33.73ms | 160ms | 2100ms | 251.83 |
| Level 5 | 250 | 37,455 | 3 | 0.008% | 33.65ms | 160ms | 2000ms | 315.32 |
| Level 6 | 300 | 45,078 | 1 | 0.002% | ~3-4ms | 160ms | 2100ms | ~375.65 |

- ✅ 性能评估
    - **失败率**：极低（0-0.008%），远低于 5% 阈值
    - **响应时间**：优秀（中位数 2-3ms，P95 160ms）
    - **吞吐量**：线性增长（62-375 RPS），无性能拐点
    - **系统稳定性**：极佳，在 300 users 高并发下仍然表现良好

- ✅ 生产环境建议
    - **安全并发用户数**：200 users
    - **安全 RPS**：250 RPS
    - **最大并发用户数**：250 users
    - **最大 RPS**：315 RPS
    - **监控指标**：P95 > 200ms、P99 > 500ms、失败率 > 1%、CPU > 80%、内存 > 80%

- ✅ 文档更新
    - 创建 `backend/loadtest_reports/压测报告总结.md`，详细记录压测结果和分析
    - 更新 `backend/docs/loadtest_guide.md`，添加压测结果总结
    - 更新 `LOG.md`，记录今日压测工作

**遇到的问题和解决方案**：

1. **Locust 错误：with 语句必须传递 catch_response=True**
    - 问题：`StressTestUser` 和 `LongConversationUser` 中的请求使用了 `with` 语句但没有传递 `catch_response=True`
    - 解决：为所有使用 `with` 语句的请求添加 `catch_response=True` 参数

2. **CSV 文件读取失败**
    - 问题：CSV 文件中 Aggregated 行的 Type 字段为空，Name 字段为 "Aggregated"，原代码只检查 Type 字段
    - 解决：修改读取逻辑，同时检查 Name 和 Type 字段：`if row.get('Name') == 'Aggregated' or row.get('Type') == 'Aggregated'`

3. **测试提前停止**
    - 问题：测试在第一个等级就停止，没有继续运行后续等级
    - 解决：修复失败率计算逻辑，添加详细的调试信息，确保测试能够正确判断成功并继续

4. **超时问题**
    - 问题：测试可能因为超时而停止，间隔时间过长
    - 解决：增加超时时间从 run_time + 60s 到 run_time + 120s