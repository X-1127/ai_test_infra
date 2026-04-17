## 2026-04-17

**目标**：1.用 trae 生成 Mock Server 骨架
          2.学习FastAPI的/chat/completions标准格式

- 做了一个 7 个阶段的规划：

| 阶段 | 内容 |
|------|------|
| 0 | 环境准备 |
| 1 | 固定响应 MVP |
| 2 | 延迟注入 |
| 3 | 故障注入（错误码） |
| 4 | YAML 配置预设回复 |
| 5 | 流式响应 |
| 6 | 请求日志记录 |
| 7 | 单元测试 + Docker |

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

**产出文件**：
llm-mock-server/
| 文件名 | 文件类型 | 用途说明 |
|--------|----------|----------|
| main.py | 主程序 | Mock LLM 服务器核心实现，包含 OpenAI 兼容的 API 接口 |
| requirements.txt | 依赖配置 | 项目所需的 Python 包及其版本 |
| README.md | 项目文档 | 详细的使用说明、API 文档和示例代码 |
| test_main.py | 单元测试 | 完整的 pytest 测试套件，测试所有 API 端点 |
| start.bat | 启动脚本 | Windows 批处理脚本，用于快速启动服务器 |
| check_dependencies.py | 工具脚本 | 检查所有依赖包是否正确安装 |
| simple_test.py | 测试脚本 | 简单的测试脚本，快速验证服务器功能 |
| client_test.py | 测试脚本 | 异步客户端测试脚本，使用 httpx 测试 API |
| manual_test.py | 测试脚本 | 手动测试脚本，支持自定义环境变量 |
| quick_test.py | 测试脚本 | 快速测试脚本，验证基本功能 |
| test_app.py | 测试文件 | 早期测试应用示例 |

**明日计划**：继续用trae完善Mock Server
