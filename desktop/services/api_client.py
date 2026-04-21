"""
API客户端，用于与LLM Mock Server通信
"""

import httpx
from typing import Dict, Any, Optional, List,Union
from desktop.config.settings import settings


class APIClient:
    """API客户端类"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.server_url
        self.timeout = 30.0
    
    def update_base_url(self, url: str):
        """更新基础URL"""
        self.base_url = url
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送GET请求"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送POST请求"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送PUT请求"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(f"{self.base_url}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """发送DELETE请求"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(f"{self.base_url}{endpoint}")
            response.raise_for_status()
            return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return await self.get("/health")
    
    async def get_injection_config(self) -> Dict[str, Any]:
        """获取注入配置"""
        return await self.get("/v1/config/injection")
    
    async def update_injection_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """更新注入配置"""
        return await self.put("/v1/config/injection", config)
    
    async def reset_injection_config(self) -> Dict[str, Any]:
        """重置注入配置"""
        return await self.post("/v1/config/injection/reset")
    
    async def get_yaml_config(self) -> Dict[str, Any]:
        """获取YAML配置"""
        return await self.get("/v1/config/yaml")
    
    async def enable_yaml_config(self) -> Dict[str, Any]:
        """启用YAML配置"""
        return await self.put("/v1/config/yaml/enable")
    
    async def disable_yaml_config(self) -> Dict[str, Any]:
        """禁用YAML配置"""
        return await self.put("/v1/config/yaml/disable")
    
    async def reload_yaml_config(self) -> Dict[str, Any]:
        """重载YAML配置"""
        return await self.post("/v1/config/yaml/reload")
    
    async def add_yaml_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """添加YAML规则"""
        return await self.post("/v1/config/yaml/rules", rule)
    
    async def delete_yaml_rule(self, index: int) -> Dict[str, Any]:
        """删除YAML规则"""
        return await self.delete(f"/v1/config/yaml/rules/{index}")
    
    async def update_yaml_rule(self, index: int, rule: Dict[str, Any]) -> Dict[str, Any]:
        """更新YAML规则"""
        return await self.put(f"/v1/config/yaml/rules/{index}", rule)
    
    async def enable_yaml_rule(self, index: int) -> Dict[str, Any]:
        """启用YAML规则"""
        return await self.put(f"/v1/config/yaml/rules/{index}/enable")
    
    async def disable_yaml_rule(self, index: int) -> Dict[str, Any]:
        """禁用YAML规则"""
        return await self.put(f"/v1/config/yaml/rules/{index}/disable")
    
    async def get_logs(self, log_type: Optional[str] = None, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """获取日志"""
        params = {"limit": limit, "offset": offset}
        if log_type:
            params["log_type"] = log_type
        return await self.get("/v1/logs", params)
    
    async def search_logs(self, keyword: str, log_type: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """搜索日志"""
        data = {"keyword": keyword, "limit": limit}
        if log_type:
            data["log_type"] = log_type
        return await self.post("/v1/logs/search", data)
    
    async def clear_logs(self) -> Dict[str, Any]:
        """清空日志"""
        return await self.delete("/v1/logs")
    
    async def chat_completion(self, messages: List[Dict[str, str]], stream: bool = False) -> Union[Dict[str, Any], str]:
        """聊天完成"""
        data = {
            "messages": messages,
            "stream": stream
        }
    
        if stream:
            # 流式响应
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/v1/chat/completions", json=data)
                response.raise_for_status()
                # 返回原始文本内容
                return response.text
        else:
            # 非流式响应
            return await self.post("/v1/chat/completions", data)
