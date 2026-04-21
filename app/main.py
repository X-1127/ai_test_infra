import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.models import HealthResponse, RootResponse
from app.api.chat import router as chat_router
from app.api.logs import router as logs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Mock response: {settings.mock_response}")
    yield
    print(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

app.include_router(chat_router)
app.include_router(logs_router)


@app.get("/", response_model=RootResponse)
async def root():
    return RootResponse(
        status="ok",
        message=f"{settings.app_name} is running",
        endpoints={
            "chat_completions": "/v1/chat/completions",
            "chat_completions_stream": "/v1/chat/completions (stream=true)",
            "get_injection_config": "/v1/config/injection",
            "update_injection_config": "/v1/config/injection",
            "reset_injection_config": "/v1/config/injection/reset",
            "get_yaml_config": "/v1/config/yaml",
            "enable_yaml_config": "/v1/config/yaml/enable",
            "disable_yaml_config": "/v1/config/yaml/disable",
            "reload_yaml_config": "/v1/config/yaml/reload",
            "validate_yaml_config": "/v1/config/yaml/validate",
            "add_yaml_rule": "/v1/config/yaml/rules",
            "delete_yaml_rule": "/v1/config/yaml/rules/{index}",
            "update_yaml_rule": "/v1/config/yaml/rules/{index}",
            "enable_yaml_rule": "/v1/config/yaml/rules/{index}/enable",
            "disable_yaml_rule": "/v1/config/yaml/rules/{index}/disable",
            "validate_yaml_rule": "/v1/config/yaml/rules/validate",
            "search_yaml_rules": "/v1/config/yaml/rules/search",
            "get_logs": "/v1/logs",
            "query_logs": "/v1/logs/query",
            "search_logs": "/v1/logs/search",
            "get_log_stats": "/v1/logs/stats",
            "clear_logs": "/v1/logs",
            "get_log_file_path": "/v1/logs/file/{log_type}",
            "health": "/health"
        }
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        debug=settings.debug
    )