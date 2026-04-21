"""
服务器管理服务
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from subprocess import TimeoutExpired


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
            self.process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # 将 stderr 合并到 stdout
                text=True,
                bufsize=1,
                universal_newlines=True
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