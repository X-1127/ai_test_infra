# 部署指南

## 桌面应用部署

### 桌面应用使用

1. **启动应用**：双击运行可执行文件
2. **服务器管理**：在"服务器"标签页启动/停止服务器
3. **配置管理**：在"配置"标签页设置延迟、故障、YAML规则
4. **日志查看**：在"日志"标签页查看服务器日志
5. **测试功能**：在"测试"标签页测试API功能
6. **性能监控**：在"监控"标签页查看服务器性能指标

详细的桌面应用说明请查看 [desktop/README.md](../desktop/README.md)

## 本地开发部署

### 前置要求

- Python 3.13 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆仓库**
```bash
git clone <repository-url>
cd llm-mock-server
```

2. **安装依赖**
```bash
pip install -e .[dev]
```

3. **配置环境变量（可选）**
```bash
cp .env.example .env
# 编辑 .env 文件设置你的配置
```

4. **启动服务器**
```bash
python scripts/start_server.py
```

或者使用批处理文件：
```bash
scripts\start.bat
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行带覆盖率报告的测试
pytest tests/ --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/unit/test_services.py -v
```

## 测试环境配置

### 环境隔离

项目实现了测试环境与生产环境的完全隔离，确保测试不会污染生产数据。

#### 环境变量

- `TESTING`: 测试模式标识（默认: false）
  - 设置为 `1` 或 `true` 启用测试模式
  - 测试模式会使用独立的日志目录 `logs_test/`

#### 日志目录隔离

- **生产环境**: `logs/` 目录
- **测试环境**: `logs_test/` 目录

#### 测试文件配置

在测试文件中设置环境变量（必须在导入 app 之前）：

```python
import os

# 必须在导入app之前设置环境变量
os.environ['TESTING'] = '1'

from app.main import app
```

#### .gitignore 配置

```gitignore
# Logs
logs/
logs_test/
*.log
```

## Docker 部署

### 使用 Docker Compose（推荐）

1. **构建并启动服务**
```bash
docker-compose up -d
```

2. **查看日志**
```bash
docker-compose logs -f
```

3. **停止服务**
```bash
docker-compose down
```

4. **重启服务**
```bash
docker-compose restart
```

### 使用 Docker 命令

1. **构建镜像**
```bash
docker build -t mock-llm-server .
```

2. **运行容器**
```bash
docker run -d -p 8000:8000 \
  -e MOCK_RESPONSE="你的自定义响应" \
  --name mock-llm-server \
  mock-llm-server
```

3. **查看日志**
```bash
docker logs -f mock-llm-server
```

4. **停止容器**
```bash
docker stop mock-llm-server
```

### Docker 配置说明

**Dockerfile 特性**：
- **多阶段构建**：使用builder和运行阶段分离，减小最终镜像大小
- **非root用户**：使用appuser运行应用，提高安全性
- **内建健康检查**：直接在镜像中集成健康检查，不依赖外部工具
- **精确复制**：只复制必要的文件（app、config目录），优化镜像体积
- **依赖管理**：通过 pyproject.toml 管理依赖，确保一致性

**docker-compose.yml 配置**：
- **自动重启**：`restart: unless-stopped`，失败时自动重启
- **健康检查**：每30秒检查一次，超时10秒，重试3次
- **日志管理**：自动日志轮转，最大10MB，保留3个文件
- **配置挂载**：支持外部配置文件挂载（只读模式）
- **网络隔离**：使用专用网络`mock-network`，提高安全性
- **环境变量**：支持`.env`文件和直接环境变量配置
- **日志目录**：将日志目录挂载到宿主机，便于查看和管理

**注意**：Docker 部署仅包含后端服务器，不包含桌面应用。如需使用桌面应用，请使用本地部署或打包的可执行文件。

### 外部配置文件管理

**挂载自定义配置文件**：
```yaml
# docker-compose.yml 中已配置
volumes:
  - ./config/responses.yaml:/app/config/responses.yaml:ro
```

**使用步骤**：
1. 修改本地配置文件：`vim config/responses.yaml`
2. 重启服务应用新配置：`docker-compose restart`
3. 验证配置生效：`curl http://localhost:8000/v1/config/yaml`

### 健康检查

**Docker健康检查**：
```bash
# 检查容器状态
docker-compose ps

# 查看健康检查日志
docker inspect mock-llm-server | grep -A 10 Health
```

**应用健康检查端点**：
```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy"
}
```

## 生产环境部署

### 环境变量配置

为生产环境设置以下环境变量：

```bash
APP_NAME=Mock LLM Server
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
DEBUG=false
MOCK_RESPONSE=这是一个模拟响应。
LOG_LEVEL=INFO
TESTING=false
```

### 安全考虑

1. **不要以 root 用户运行**: 在 Docker 中创建非 root 用户
2. **使用 HTTPS**: 添加 SSL/TLS 终止
3. **速率限制**: 为生产环境启用速率限制
4. **日志管理**: 配置适当的日志轮转
5. **监控**: 添加健康检查和监控
6. **环境隔离**: 确保测试和生产环境完全隔离

### 扩展性考虑

为了实现高可用性，建议：

1. **负载均衡**: 使用 Nginx 或云负载均衡器
2. **多实例**: 运行多个容器实例
3. **容器编排**: 使用 Kubernetes 或 Docker Swarm
4. **自动扩展**: 基于 CPU/内存使用情况配置自动扩展

### 监控建议

添加以下监控指标：

- 服务器运行时间
- 响应时间
- 错误率
- 资源使用情况（CPU、内存、磁盘）
- 请求计数
- 日志统计信息

## 故障排查

### 常见问题

1. **端口已被占用**
   - 更改 `PORT` 环境变量
   - 停止冲突的服务

2. **权限错误**
   - 检查文件权限
   - 确保具有适当的用户权限

3. **容器无法启动**
   - 查看 Docker 日志：`docker logs mock-llm-server`
   - 验证环境变量
   - 检查资源可用性

4. **测试环境污染**
   - 确认 `TESTING` 环境变量设置正确
   - 检查日志是否写入 `logs_test/` 目录
   - 验证 `.gitignore` 包含 `logs_test/`

### 健康检查

服务器提供健康检查端点：

```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy"
}
```

## 备份和恢复

### 配置备份

定期备份以下内容：
- `.env` 文件
- 自定义配置
- 测试数据
- 生产日志（logs/ 目录）

### 恢复步骤

1. 恢复配置文件
2. 重启服务
3. 验证健康检查端点
4. 检查日志目录是否正确

## 更新和维护

### 更新应用程序

1. 拉取最新代码
2. 更新依赖：`pip install -e .[dev]`
3. 运行测试：`pytest tests/`
4. 重启服务

### 依赖更新

```bash
# 检查可用的更新
pip list --outdated

# 更新特定包
pip install package-name --upgrade

# 更新所有依赖
pip install -e .[dev] --upgrade
```

## 性能优化

### 建议配置

- **生产环境**: 关闭 DEBUG 模式，设置适当的日志级别
- **高并发**: 使用多个容器实例，配置负载均衡
- **资源限制**: 在 Docker 中设置 CPU 和内存限制
- **日志管理**: 配置日志轮转，避免日志文件过大

### 性能测试

使用延迟注入功能测试应用性能：

```bash
# 启用延迟注入
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

## 日志管理

### 日志级别

- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 日志查看

```bash
# Docker 环境
docker logs -f mock-llm-server

# 本地环境
# 日志输出到控制台和文件
```

### 日志目录

- **生产环境**: `logs/` 目录
  - `request.log`: 请求日志
  - `error.log`: 错误日志
  - `access.log`: 访问日志

- **测试环境**: `logs_test/` 目录
  - 与生产环境相同的文件结构
  - 完全独立，避免污染

### 日志轮转

在生产环境中，建议配置日志轮转以避免日志文件过大。

- 单个日志文件最大 10MB
- 保留 5 个备份文件
- 自动轮转机制

## 网络配置

### 防火墙设置

确保防火墙允许以下端口：
- `8000`: 应用端口（默认）

### 反向代理配置

使用 Nginx 作为反向代理的示例配置：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.13'
    - name: Install dependencies
      run: |
        pip install -e .[dev]
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v2
    - name: Build and push Docker image
      run: |
        docker build -t mock-llm-server .
        # 添加推送逻辑
```

## 故障恢复

### 自动重启

Docker Compose 配置了自动重启策略：

```yaml
restart: unless-stopped
```

### 数据恢复

如果需要恢复配置：

1. 从备份恢复 `.env` 文件
2. 重启容器
3. 验证服务状态
4. 检查日志目录是否正确

## 监控和告警

### 建议监控指标

- 请求响应时间
- 错误率
- CPU 使用率
- 内存使用率
- 磁盘使用率
- 日志统计信息

### 告警设置

建议设置以下告警：
- 服务器宕机
- 响应时间过长
- 错误率过高
- 资源使用率超过阈值
- 日志错误数量异常增加

## 安全加固

### 安全建议

1. **定期更新依赖**: 保持依赖包最新
2. **使用 HTTPS**: 保护 API 通信
3. **实施速率限制**: 防止滥用
4. **输入验证**: 验证所有输入数据
5. **错误处理**: 不要暴露敏感信息
6. **环境隔离**: 确保测试和生产环境完全分离

### 环境变量保护

- 不要将 `.env` 文件提交到版本控制
- 使用密钥管理服务存储敏感信息
- 定期轮换密钥和密码
- 区分测试和生产环境变量

## 扩展功能

### 添加新的 API 端点

1. 在 `app/api/` 中创建新的路由文件
2. 在 `app/main.py` 中注册路由
3. 添加相应的测试用例
4. 更新 API 文档

### 自定义响应

通过环境变量 `MOCK_RESPONSE` 自定义响应内容：

```bash
export MOCK_RESPONSE="你的自定义响应内容"
```

或在 `.env` 文件中设置：

```bash
MOCK_RESPONSE=你的自定义响应内容
```

## 支持和维护

### 获取帮助

- 查看项目文档
- 检查 GitHub Issues
- 提交新的 Issue

### 贡献代码

欢迎贡献代码、报告问题或提出建议！

## 相关文档

- [项目说明文档](../PROJECT_GUIDE.md)
- [桌面应用文档](../desktop/README.md)
- [打包指南](../BUILD_GUIDE.md)
- [API 文档](api.md)
- [注入功能说明](injection_features.md)
- [性能分析](performance_analysis.md)
- [性能指南](performance_guide.md)
- [测试系统](test_system.md)
- [YAML配置功能](yaml_config_features.md)
