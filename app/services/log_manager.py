import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from app.config import settings


class LogManager:
    def __init__(self):
        if settings.testing:
            self.log_dir = Path(settings.get_log_dir())
        else:
            self.log_dir = Path(settings.get_log_dir())
        
        # 确保日志目录存在
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # 如果无法创建日志目录，使用临时目录
            import tempfile
            self.log_dir = Path(tempfile.gettempdir()) / "llm_mock_server_logs"
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.request_logger = self._setup_logger("request", "request.log")
        self.error_logger = self._setup_logger("error", "error.log")
        self.access_logger = self._setup_logger("access", "access.log")
        
        self._logs = []
        self._max_logs = 1000
    
    def _setup_logger(self, name: str, filename: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        if not logger.handlers:
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / filename,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            
            if settings.log_format == "json":
                formatter = logging.Formatter(
                    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}'
                )
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def log_request(self, method: str, path: str, status_code: int, 
                   duration_ms: float, client_ip: Optional[str] = None,
                   user_agent: Optional[str] = None, body: Optional[str] = None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "request",
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "body": body
        }
        
        self._add_to_memory(log_entry)
        self.request_logger.info(log_entry)
    
    def log_error(self, error_type: str, error_message: str, 
                  path: Optional[str] = None, method: Optional[str] = None,
                  traceback: Optional[str] = None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "path": path,
            "method": method,
            "traceback": traceback
        }
        
        self._add_to_memory(log_entry)
        self.error_logger.error(log_entry)
    
    def log_access(self, method: str, path: str, status_code: int,
                   client_ip: Optional[str] = None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "access",
            "method": method,
            "path": path,
            "status_code": status_code,
            "client_ip": client_ip
        }
        
        self._add_to_memory(log_entry)
        self.access_logger.info(log_entry)
    
    def _add_to_memory(self, log_entry: dict):
        self._logs.append(log_entry)
        if len(self._logs) > self._max_logs:
            self._logs.pop(0)
    
    def get_logs(self, log_type: Optional[str] = None, 
                 limit: int = 100, offset: int = 0) -> list:
        filtered_logs = self._logs
        
        if log_type:
            filtered_logs = [log for log in filtered_logs if log.get("type") == log_type]
        
        return filtered_logs[offset:offset + limit]
    
    def search_logs(self, keyword: str, log_type: Optional[str] = None,
                    limit: int = 100) -> list:
        filtered_logs = self._logs
        
        if log_type:
            filtered_logs = [log for log in filtered_logs if log.get("type") == log_type]
        
        keyword_lower = keyword.lower()
        results = []
        
        for log in filtered_logs:
            log_str = str(log).lower()
            if keyword_lower in log_str:
                results.append(log)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_log_stats(self) -> dict:
        stats = {
            "total_logs": len(self._logs),
            "by_type": {},
            "recent_errors": 0,
            "avg_response_time": 0
        }
        
        request_logs = [log for log in self._logs if log.get("type") == "request"]
        error_logs = [log for log in self._logs if log.get("type") == "error"]
        access_logs = [log for log in self._logs if log.get("type") == "access"]
        
        stats["by_type"] = {
            "request": len(request_logs),
            "error": len(error_logs),
            "access": len(access_logs)
        }
        
        recent_time = datetime.now().timestamp() - 3600  # 最近1小时
        stats["recent_errors"] = len([
            log for log in error_logs
            if datetime.fromisoformat(log["timestamp"]).timestamp() > recent_time
        ])
        
        if request_logs:
            total_duration = sum(log.get("duration_ms", 0) for log in request_logs)
            stats["avg_response_time"] = total_duration / len(request_logs)
        
        return stats
    
    def clear_logs(self):
        self._logs.clear()
    
    def get_log_file_path(self, log_type: str) -> Optional[str]:
        file_map = {
            "request": "request.log",
            "error": "error.log",
            "access": "access.log"
        }
        
        filename = file_map.get(log_type)
        if filename:
            return str(self.log_dir / filename)
        
        return None


_log_manager_instance = None


def get_log_manager():
    global _log_manager_instance
    if _log_manager_instance is None:
        _log_manager_instance = LogManager()
    return _log_manager_instance


log_manager = get_log_manager()