# Deployment Guide

## Local Development

### Prerequisites

- Python 3.13+
- pip

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -e .[dev]
```

3. Configure environment (optional):
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run the server:
```bash
python scripts/start_server.py
```

Or using the batch file:
```bash
scripts\start.bat
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_services.py -v
```

## Docker Deployment

### Using Docker Compose (Recommended)

1. Build and start:
```bash
docker-compose up -d
```

2. View logs:
```bash
docker-compose logs -f
```

3. Stop the service:
```bash
docker-compose down
```

### Using Docker Commands

1. Build the image:
```bash
docker build -t mock-llm-server .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 \
  -e MOCK_RESPONSE="Your custom response" \
  --name mock-llm-server \
  mock-llm-server
```

3. View logs:
```bash
docker logs -f mock-llm-server
```

4. Stop the container:
```bash
docker stop mock-llm-server
```

### Docker Configuration

The `docker-compose.yml` file includes:
- Automatic restart on failure
- Health checks
- Log volume mounting
- Environment variable support

## Production Deployment

### Environment Variables

Set these environment variables for production:

```bash
APP_NAME=Mock LLM Server
APP_VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
DEBUG=false
MOCK_RESPONSE=This is a mock response.
LOG_LEVEL=INFO
```

### Security Considerations

1. **Do not run as root**: Create a non-root user in Docker
2. **Use HTTPS**: Add SSL/TLS termination
3. **Rate limiting**: Enable rate limiting for production
4. **Logging**: Configure proper log rotation
5. **Monitoring**: Add health checks and monitoring

### Scaling

For high availability, consider:

1. **Load Balancing**: Use Nginx or cloud load balancer
2. **Multiple Instances**: Run multiple container instances
3. **Container Orchestration**: Use Kubernetes or Docker Swarm
4. **Auto-scaling**: Configure based on CPU/memory usage

### Monitoring

Add monitoring for:

- Server uptime
- Response times
- Error rates
- Resource usage (CPU, memory, disk)
- Request counts

## Troubleshooting

### Common Issues

1. **Port already in use**:
   - Change the `PORT` environment variable
   - Stop the conflicting service

2. **Permission errors**:
   - Check file permissions
   - Ensure proper user rights

3. **Container not starting**:
   - Check Docker logs: `docker logs mock-llm-server`
   - Verify environment variables
   - Check resource availability

### Health Checks

The server provides a health check endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

## Backup and Recovery

### Configuration Backup

Regularly backup:
- `.env` file
- Custom configurations
- Test data

### Recovery

1. Restore configuration files
2. Restart the service
3. Verify health check endpoint

## Updates and Maintenance

### Updating the Application

1. Pull latest changes
2. Update dependencies: `pip install -e .[dev]`
3. Run tests: `pytest tests/`
4. Restart the service

### Dependency Updates

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install package-name --upgrade

# Update all dependencies
pip install -e .[dev] --upgrade
```