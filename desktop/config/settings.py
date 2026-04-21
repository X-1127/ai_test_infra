"""
桌面应用配置管理
"""

from pathlib import Path
from typing import Optional


class DesktopSettings:
    """桌面应用设置类"""
    
    def __init__(self):
        self.server_host: str = "localhost"
        self.server_port: int = 8000
        self.server_url: str = f"http://{self.server_host}:{self.server_port}"
        
        self.auto_start_server: bool = False
        self.minimize_to_tray: bool = True
        self.show_notifications: bool = True
        
        self.log_auto_refresh: bool = True
        self.log_refresh_interval: int = 5
        
        self.theme: str = "default"
        self.language: str = "zh_CN"
        
        self.window_width: int = 1200
        self.window_height: int = 800
        
        self.config_dir: Path = Path.home() / ".llm-mock-server"
        self.config_dir.mkdir(exist_ok=True)
    
    def update_server_url(self, host: Optional[str] = None, port: Optional[int] = None):
        """更新服务器URL"""
        if host is not None:
            self.server_host = host
        if port is not None:
            self.server_port = port
        self.server_url = f"http://{self.server_host}:{self.server_port}"
    
    def get_config_file_path(self) -> Path:
        """获取配置文件路径"""
        return self.config_dir / "desktop_config.json"
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            import json
            config = {
                "server_host": self.server_host,
                "server_port": self.server_port,
                "auto_start_server": self.auto_start_server,
                "minimize_to_tray": self.minimize_to_tray,
                "show_notifications": self.show_notifications,
                "log_auto_refresh": self.log_auto_refresh,
                "log_refresh_interval": self.log_refresh_interval,
                "theme": self.theme,
                "language": self.language,
                "window_width": self.window_width,
                "window_height": self.window_height,
            }
            
            with open(self.get_config_file_path(), 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def load_config(self) -> bool:
        """从文件加载配置"""
        try:
            import json
            config_file = self.get_config_file_path()
            if not config_file.exists():
                return False
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.server_host = config.get("server_host", self.server_host)
            self.server_port = config.get("server_port", self.server_port)
            self.auto_start_server = config.get("auto_start_server", self.auto_start_server)
            self.minimize_to_tray = config.get("minimize_to_tray", self.minimize_to_tray)
            self.show_notifications = config.get("show_notifications", self.show_notifications)
            self.log_auto_refresh = config.get("log_auto_refresh", self.log_auto_refresh)
            self.log_refresh_interval = config.get("log_refresh_interval", self.log_refresh_interval)
            self.theme = config.get("theme", self.theme)
            self.language = config.get("language", self.language)
            self.window_width = config.get("window_width", self.window_width)
            self.window_height = config.get("window_height", self.window_height)
            
            self.update_server_url()
            return True
        except Exception as e:
            print(f"加载配置失败: {e}")
            return False


settings = DesktopSettings()