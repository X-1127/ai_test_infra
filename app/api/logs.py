from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.log_manager import log_manager


router = APIRouter()


class LogQueryRequest(BaseModel):
    log_type: Optional[str] = Field(None, pattern="^(request|error|access)$")
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class LogSearchRequest(BaseModel):
    keyword: str = Field(..., min_length=1)
    log_type: Optional[str] = Field(None, pattern="^(request|error|access)$")
    limit: int = Field(default=100, ge=1, le=1000)


class LogStatsResponse(BaseModel):
    total_logs: int
    by_type: dict
    recent_errors: int
    avg_response_time: float


@router.get("/v1/logs")
async def get_logs(log_type: Optional[str] = None, limit: int = 100, offset: int = 0):
    try:
        logs = log_manager.get_logs(log_type=log_type, limit=limit, offset=offset)
        return {
            "logs": logs,
            "count": len(logs),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志失败: {str(e)}")


@router.post("/v1/logs/query")
async def query_logs(request: LogQueryRequest):
    try:
        logs = log_manager.get_logs(
            log_type=request.log_type,
            limit=request.limit,
            offset=request.offset
        )
        return {
            "logs": logs,
            "count": len(logs),
            "limit": request.limit,
            "offset": request.offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询日志失败: {str(e)}")


@router.post("/v1/logs/search")
async def search_logs(request: LogSearchRequest):
    try:
        logs = log_manager.search_logs(
            keyword=request.keyword,
            log_type=request.log_type,
            limit=request.limit
        )
        return {
            "logs": logs,
            "count": len(logs),
            "keyword": request.keyword
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索日志失败: {str(e)}")


@router.get("/v1/logs/stats", response_model=LogStatsResponse)
async def get_log_stats():
    try:
        return log_manager.get_log_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志统计失败: {str(e)}")


@router.delete("/v1/logs")
async def clear_logs():
    try:
        log_manager.clear_logs()
        return {"message": "日志已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空日志失败: {str(e)}")


@router.get("/v1/logs/file/{log_type}")
async def get_log_file_path(log_type: str):
    try:
        file_path = log_manager.get_log_file_path(log_type)
        if file_path:
            return {"file_path": file_path}
        else:
            raise HTTPException(status_code=400, detail=f"无效的日志类型: {log_type}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取日志文件路径失败: {str(e)}")