"""
服务器管理服务
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from subprocess import TimeoutExpired

# 检测是否在打包环境中运行
IS_FROZEN = getattr(sys, 'frozen', False)
if IS_FROZEN:
    # 打包环境
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    # 开发环境
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))


class ServerThread(QThread):
    """服务器线程（打包环境使用）"""
    
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, app, host, port):
        super().__init__()
        self.app = app
        self.host = host
        self.port = port
        self.server = None
    
    def run(self):
        """运行服务器"""
        try:
            import uvicorn
            from app.config import settings
            
            # 发送调试信息
            self.output_received.emit(f"Application path: {APPLICATION_PATH}")
            self.output_received.emit(f"Log directory: {settings.get_log_dir()}")
            self.output_received.emit(f"Config directory: {settings.get_config_dir()}")
            
            # 创建自定义配置以捕获输出
            config = uvicorn.Config(
                self.app,
                host=self.host,
                port=self.port,
                log_level="debug" if settings.debug else "info",
                access_log=True
            )
            
            self.server = uvicorn.Server(config)
            
            # 发送启动信息
            self.output_received.emit(f"Starting {settings.app_name} v{settings.app_version}")
            self.output_received.emit(f"Server will be available at: http://{self.host}:{self.port}")
            
            # 运行服务器
            self.server.run()
            
        except ImportError as e:
            error_msg = f"Import error: {str(e)}"
            self.output_received.emit(error_msg)
            self.output_received.emit(f"Python path: {sys.path}")
            self.error_received.emit(error_msg)
        except Exception as e:
            import traceback
            error_msg = f"Server error: {str(e)}"
            traceback_msg = traceback.format_exc()
            self.output_received.emit(error_msg)
            self.output_received.emit(f"Traceback:\n{traceback_msg}")
            self.error_received.emit(error_msg)
        finally:
            self.finished.emit()
    
    def stop(self):
        """停止服务器"""
        if self.server:
            self.server.should_exit = True


class ServerProcessThread(QThread):
    """服务器进程线程"""
    
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    process_finished = pyqtSignal(int)
    
    def __init__(self, command: list, cwd: Optional[Path] = None):
        super().__init__()
        self.command = command
        self.cwd = cwd
        self.process: Optional[subprocess.Popen] = None
    
    def run(self):
        """运行服务器进程"""
        try:
            # 根据环境设置不同的启动参数
            startupinfo = None
            creationflags = 0
            
            if sys.platform == 'win32':
                # Windows 环境
                if IS_FROZEN:
                    # 打包环境：隐藏控制台窗口
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    creationflags = subprocess.CREATE_NO_WINDOW
                else:
                    # 开发环境：显示控制台窗口
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            self.process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 将 stderr 合并到 stdout
                text=True,
                bufsize=1,
                universal_newlines=True,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            while True:
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    self.output_received.emit(output.strip())
            
            return_code = self.process.poll()
            self.process_finished.emit(return_code)
            
        except Exception as e:
            self.error_received.emit(str(e))
    
    def stop(self):
        """停止服务器进程"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()


class ServerManager(QObject):
    """服务器管理器"""
    
    server_started = pyqtSignal()
    server_stopped = pyqtSignal()
    server_error = pyqtSignal(str)
    output_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.process_thread: Optional[ServerProcessThread] = None
        self.is_running = False
        self._is_stopping = False  # 标记是否正在主动停止
        
        self.server_script = Path(__file__).parent.parent.parent / "scripts" / "start_server.py"
        self.project_root = Path(__file__).parent.parent.parent
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """启动服务器"""
        if self.is_running:
            self.server_error.emit("服务器已经在运行中")
            return
        
        if IS_FROZEN:
            # 打包环境：使用内部模块启动，避免打开新窗口
            try:
                # 添加应用路径到 sys.path
                app_path = os.path.join(APPLICATION_PATH, 'app')
                if app_path not in sys.path:
                    sys.path.insert(0, app_path)
                
                # 导入并启动服务器
                import uvicorn
                from app.main import app
                from app.config import settings
                
                # 创建服务器线程
                self.server_thread = ServerThread(app, host, port)
                self.server_thread.output_received.connect(self._on_output)
                self.server_thread.error_received.connect(self._on_error)
                self.server_thread.finished.connect(self._on_finished)
                
                self.server_thread.start()
                self.is_running = True
                self.server_started.emit()
                
            except Exception as e:
                self.server_error.emit(f"启动服务器失败: {str(e)}")
        else:
            # 开发环境：使用子进程启动
            if not self.server_script.exists():
                self.server_error.emit(f"服务器脚本不存在: {self.server_script}")
                return
            
            command = [
                sys.executable,
                str(self.server_script),
                "--host", host,
                "--port", str(port)
            ]
            
            print(f"启动命令: {' '.join(command)}")
            
            self.process_thread = ServerProcessThread(command, self.project_root)
            self.process_thread.output_received.connect(self._on_output)
            self.process_thread.error_received.connect(self._on_error)
            self.process_thread.process_finished.connect(self._on_finished)
            
            self.process_thread.start()
            self.is_running = True
            self.server_started.emit()
    
    def stop_server(self):
        """停止服务器"""
        if not self.is_running:
            self.server_error.emit("服务器未运行")
            return
        
        self._is_stopping = True  # 标记正在主动停止
        
        if IS_FROZEN:
            # 打包环境：停止服务器线程
            if hasattr(self, 'server_thread') and self.server_thread:
                self.server_thread.stop()
                self.server_thread.wait()
                self.server_thread = None
        else:
            # 开发环境：停止子进程
            if self.process_thread:
                self.process_thread.stop()
                self.process_thread.wait()
                self.process_thread = None
        
        self.is_running = False
        self.server_stopped.emit()
    
    def restart_server(self, host: str = "0.0.0.0", port: int = 8000):
        """重启服务器"""
        self.stop_server()
        self.start_server(host, port)
    
    def _on_output(self, output: str):
        """处理服务器输出"""
        self.output_received.emit(output)
    
    def _on_error(self, error: str):
        """处理服务器错误"""
        self.server_error.emit(error)
    
    def _on_finished(self, return_code: int):
        """处理服务器进程结束"""
        self.is_running = False
        
        # 如果是主动停止，不报错
        if self._is_stopping:
            self._is_stopping = False
            self.server_stopped.emit()
            return
        
        # 如果返回码不为0，报错
        if return_code != 0:
            self.server_error.emit(f"服务器异常退出，返回码: {return_code}")
        else:
            self.server_stopped.emit()