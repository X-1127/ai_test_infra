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
  -e MOCK_RESPONSE="This is a mock response." \
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

## 验证服务

### 健康检查
```bash
curl http://localhost:8000/health
```

### 测试聊天接口
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'
```

## 开发模式

如果需要在容器中运行测试：

```bash
# 进入容器
docker exec -it mock-llm-server bash

# 运行测试
cd /app
pytest tests/ -v
```

## 故障排查

### 查看容器状态
```bash
docker ps
docker-compose ps
```

### 查看详细日志
```bash
docker logs mock-llm-server
docker-compose logs mock-llm-server
```

### 重新构建
```bash
docker-compose build --no-cache
```