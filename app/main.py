import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.models import HealthResponse, RootResponse
from app.api.chat import router as chat_router


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


@app.get("/", response_model=RootResponse)
async def root():
    return RootResponse(
        status="ok",
        message=f"{settings.app_name} is running",
        endpoints={
            "chat_completions": "/v1/chat/completions",
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