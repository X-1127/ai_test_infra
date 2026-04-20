# Docker 部署指南

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Docker 命令

```bash
# 构建镜像
docker build -t mock-llm-server .

# 运行容器
docker run -d -p 8000:8000 \
  -e MOCK_RESPONSE="这是一个模拟响应。" \
  --name mock-llm-server \
  mock-llm-server

# 查看日志
docker logs -f mock-llm-server

# 停止容器
docker stop mock-llm-server
```

## 自定义配置

### 修改端口

在 `docker-compose.yml` 中修改端口映射：
```yaml
ports:
  - "8080:8000"  # 将容器8000端口映射到主机8080端口
```

或使用 Docker 命令：
```bash
docker run -d -p 8080:8000 mock-llm-server
```

### 自定义响应内容

设置环境变量：

```bash
docker run -d -p 8000:8000 \
  -e MOCK_RESPONSE="你的自定义响应内容" \
  mock-llm-server
```

或在 `docker-compose.yml` 中修改：
```yaml
environment:
  - MOCK_RESPONSE=你的自定义响应内容
```

### 配置调试模式

```bash
docker run -d -p 8000:8000 \
  -e DEBUG=true \
  mock-llm-server
```

### 配置日志级别

```bash
docker run -d -p 8000:8000 \
  -e LOG_LEVEL=DEBUG \
  mock-llm-server
```

## 验证服务

### 健康检查

```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy"
}
```

### 测试聊天接口

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

### 查看 API 文档

在浏览器中访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发模式

### 进入容器

```bash
docker exec -it mock-llm-server bash
```

### 在容器中运行测试

```bash
# 进入容器
docker exec -it mock-llm-server bash

# 运行测试
cd /app
pytest tests/ -v

# 运行带覆盖率的测试
pytest tests/ --cov=app --cov-report=html
```

### 挂载本地代码

在 `docker-compose.yml` 中添加卷挂载：
```yaml
volumes:
  - ./app:/app/app
  - ./tests:/app/tests
```

这样可以在本地修改代码，容器中实时生效。

## 生产部署

### 使用环境变量文件

创建 `.env` 文件：
```bash
APP_NAME=Mock LLM Server
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
DEBUG=false
MOCK_RESPONSE=这是一个模拟响应。
LOG_LEVEL=INFO
```

在 `docker-compose.yml` 中引用：
```yaml
services:
  app:
    env_file:
      - .env
```

### 配置资源限制

在 `docker-compose.yml` 中添加：
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### 配置自动重启

```yaml
services:
  app:
    restart: unless-stopped
```

重启策略选项：
- `no`: 不自动重启（默认）
- `always`: 总是重启
- `on-failure`: 仅在失败时重启
- `unless-stopped`: 除非手动停止，否则总是重启

### 配置健康检查

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## 日志管理

### 查看日志

```bash
# 查看所有日志
docker logs mock-llm-server

# 实时查看日志
docker logs -f mock-llm-server

# 查看最近100行日志
docker logs --tail 100 mock-llm-server

# 查看最近10分钟的日志
docker logs --since 10m mock-llm-server
```

### 配置日志驱动

在 `docker-compose.yml` 中配置：
```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 挂载日志目录

```yaml
services:
  app:
    volumes:
      - ./logs:/app/logs
```

## 网络配置

### 自定义网络

```yaml
networks:
  mock-network:
    driver: bridge

services:
  app:
    networks:
      - mock-network
```

### 连接到现有网络

```bash
docker network connect existing-network mock-llm-server
```

### 配置 DNS

```yaml
services:
  app:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

## 数据持久化

### 挂载配置文件

```yaml
services:
  app:
    volumes:
      - ./config:/app/config
```

### 挂载测试数据

```yaml
services:
  app:
    volumes:
      - ./tests/fixtures:/app/tests/fixtures
```

## 多容器部署

### 使用 Docker Compose

```yaml
version: '3.8'

services:
  mock-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MOCK_RESPONSE=服务器1响应
    networks:
      - app-network

  mock-server-2:
    build: .
    ports:
      - "8001:8000"
    environment:
      - MOCK_RESPONSE=服务器2响应
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - mock-server
      - mock-server-2
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### 负载均衡配置

Nginx 配置示例 (`nginx.conf`):
```nginx
upstream mock_servers {
    server mock-server:8000;
    server mock-server-2:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://mock_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 故障排查

### 查看容器状态

```bash
# 查看所有容器
docker ps -a

# 查看特定容器
docker ps | grep mock-llm-server

# 查看容器详细信息
docker inspect mock-llm-server
```

### 查看详细日志

```bash
# 查看容器日志
docker logs mock-llm-server

# 查看Docker Compose日志
docker-compose logs mock-llm-server

# 查看所有服务日志
docker-compose logs
```

### 进入容器调试

```bash
# 进入容器
docker exec -it mock-llm-server bash

# 查看进程
ps aux

# 查看环境变量
env

# 测试网络连接
curl http://localhost:8000/health
```

### 重新构建

```bash
# 清理并重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 或使用Docker命令
docker stop mock-llm-server
docker rm mock-llm-server
docker build -t mock-llm-server .
docker run -d -p 8000:8000 --name mock-llm-server mock-llm-server
```

### 常见问题

#### 端口冲突

**问题**: 端口已被占用

**解决方法**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# 更改端口映射
docker run -d -p 8080:8000 mock-llm-server
```

#### 容器无法启动

**问题**: 容器启动后立即退出

**解决方法**:
```bash
# 查看日志
docker logs mock-llm-server

# 检查镜像
docker images

# 重新构建
docker-compose build --no-cache
```

#### 网络连接问题

**问题**: 无法从主机访问容器

**解决方法**:
```bash
# 检查端口映射
docker port mock-llm-server

# 检查防火墙
# Windows
netsh advfirewall firewall add rule name="Docker" dir=in action=allow protocol=TCP localport=8000

# Linux
sudo ufw allow 8000/tcp
```

## 性能优化

### 使用多阶段构建

```dockerfile
# 构建阶段
FROM python:3.13-slim as builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .[dev]

# 运行阶段
FROM python:3.13-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /app /app
COPY app ./app

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 优化镜像大小

```dockerfile
# 使用更小的基础镜像
FROM python:3.13-alpine

# 清理缓存
RUN pip install --no-cache-dir -e .[dev] && \
    rm -rf /root/.cache/pip

# 合并RUN命令
RUN apk add --no-cache curl && \
    pip install --no-cache-dir -e .[dev]
```

### 使用缓存

```dockerfile
# 先复制依赖文件，利用缓存
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .[dev]

# 再复制应用代码
COPY app ./app
```

## 安全建议

### 使用非 root 用户

```dockerfile
FROM python:3.13-slim

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

WORKDIR /app
COPY --chown=appuser:appuser . .

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 扫描镜像漏洞

```bash
# 使用 Trivy 扫描
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
    aquasec/trivy image mock-llm-server

# 使用 Docker Scout
docker scout quickview mock-llm-server
docker scout cves mock-llm-server
```

### 限制容器权限

```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
```

## 监控和告警

### 使用 Prometheus

```yaml
services:
  mock-server:
    # ... 其他配置
    labels:
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=8000"

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### 使用 Grafana

```yaml
services:
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  grafana-data:
```

## 备份和恢复

### 备份配置

```bash
# 备份环境变量
docker exec mock-llm-server env > backup.env

# 备份配置文件
docker cp mock-llm-server:/app/.env ./backup/
```

### 恢复配置

```bash
# 恢复环境变量
docker run --env-file backup.env mock-llm-server

# 恢复配置文件
docker cp ./backup/.env mock-llm-server:/app/.env
```

## 更新和维护

### 滚动更新

```bash
# 拉取新镜像
docker-compose pull

# 重新创建容器
docker-compose up -d --no-deps --build app

# 或使用滚动更新
docker-compose up -d --scale app=2 --no-recreate
docker-compose up -d --scale app=1 --no-recreate
```

### 清理资源

```bash
# 清理停止的容器
docker container prune

# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 清理未使用的网络
docker network prune

# 清理所有未使用的资源
docker system prune -a
```

## 相关文档

- [项目说明文档](PROJECT_GUIDE.md) - 完整的项目说明
- [API 文档](docs/api.md) - API接口详细说明
- [部署指南](docs/deployment.md) - 部署和运维指南
- [注入功能说明](docs/injection_features.md) - 延迟和故障注入功能详解