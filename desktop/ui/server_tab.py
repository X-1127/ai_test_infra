"""
服务器管理标签页
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QFrame, QMessageBox,
    QTextEdit, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from desktop.services.server_manager import ServerManager
from desktop.config.settings import settings
import requests
from datetime import datetime


class ServerTab(QWidget):
    """服务器管理标签页"""
    
    def __init__(self):
        super().__init__()
        self.server_manager = ServerManager()
        self.settings = settings
        
        self.health_check_timer = QTimer()
        self.health_check_timer.timeout.connect(self.check_server_health)
        self.health_check_interval = 5000  # 5秒检查一次
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("服务器管理")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        control_group = QGroupBox("控制")
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("启动服务器")
        self.start_button.setMinimumHeight(40)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.stop_button = QPushButton("停止服务器")
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.restart_button = QPushButton("重启服务器")
        self.restart_button.setMinimumHeight(40)
        self.restart_button.setEnabled(False)
        self.restart_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.restart_button)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        status_group = QGroupBox("状态")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("状态: ⚫ 未启动")
        status_font = QFont()
        status_font.setPointSize(12)
        self.status_label.setFont(status_font)
        status_layout.addWidget(self.status_label)
        
        port_layout = QHBoxLayout()
        port_label = QLabel("端口:")
        self.port_input = QLineEdit(str(self.settings.server_port))
        self.port_input.setMaximumWidth(100)
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        port_layout.addStretch()
        status_layout.addLayout(port_layout)
        
        url_label = QLabel(f"地址: {self.settings.server_url}")
        status_layout.addWidget(url_label)
        
        health_layout = QHBoxLayout()
        self.health_label = QLabel("健康检查: ⚪ 未检查")
        health_layout.addWidget(self.health_label)
        
        self.check_health_button = QPushButton("检查")
        self.check_health_button.setMaximumWidth(60)
        self.check_health_button.clicked.connect(self.check_server_health)
        health_layout.addWidget(self.check_health_button)
        health_layout.addStretch()
        status_layout.addLayout(health_layout)
        
        self.start_time_label = QLabel("启动时间: -")
        status_layout.addWidget(self.start_time_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        output_group = QGroupBox("服务器输出")
        output_layout = QVBoxLayout()
        
        output_control_layout = QHBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                padding: 10px;
                border-radius: 4px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 10px;
                border: 1px solid #3c3c3c;
            }
        """)
        self.output_text.setMinimumHeight(200)
        self.output_text.setPlaceholderText("服务器输出将显示在这里...")
        
        self.clear_output_button = QPushButton("清空输出")
        self.clear_output_button.setMaximumWidth(80)
        self.clear_output_button.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #546E7A;
            }
            QPushButton:pressed {
                background-color: #455A64;
            }
        """)
        self.clear_output_button.clicked.connect(self.clear_output)
        
        output_control_layout.addStretch()
        output_control_layout.addWidget(self.clear_output_button)
        
        output_layout.addWidget(self.output_text)
        output_layout.addLayout(output_control_layout)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        layout.addStretch()
    
    def connect_signals(self):
        """连接信号"""
        self.start_button.clicked.connect(self.start_server)
        self.stop_button.clicked.connect(self.stop_server)
        self.restart_button.clicked.connect(self.restart_server)
        
        self.server_manager.server_started.connect(self.on_server_started)
        self.server_manager.server_stopped.connect(self.on_server_stopped)
        self.server_manager.server_error.connect(self.on_server_error)
        self.server_manager.output_received.connect(self.on_output_received)
    
    @pyqtSlot()
    def start_server(self):
        """启动服务器"""
        try:
            port = int(self.port_input.text())
            self.settings.update_server_url(port=port)
            self.server_manager.start_server(port=port)
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的端口号")
    
    @pyqtSlot()
    def stop_server(self):
        """停止服务器"""
        self.server_manager.stop_server()
    
    @pyqtSlot()
    def restart_server(self):
        """重启服务器"""
        try:
            port = int(self.port_input.text())
            self.settings.update_server_url(port=port)
            self.server_manager.restart_server(port=port)
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的端口号")
    
    @pyqtSlot()
    def on_server_started(self):
        """服务器启动事件"""
        self.status_label.setText("状态: 🟢 运行中")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.restart_button.setEnabled(True)
        self.port_input.setEnabled(False)
        self.output_text.clear()
        self.output_text.append("服务器正在启动...")
        
        # 记录启动时间
        self.start_time_label.setText(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 启动健康检查定时器
        self.health_check_timer.start(self.health_check_interval)
    
    @pyqtSlot()
    def on_server_stopped(self):
        """服务器停止事件"""
        self.status_label.setText("状态: ⚫ 未启动")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.restart_button.setEnabled(False)
        self.port_input.setEnabled(True)
        self.health_label.setText("健康检查: ⚪ 未检查")
        self.start_time_label.setText("启动时间: -")
        
        # 停止健康检查定时器
        self.health_check_timer.stop()
    
    @pyqtSlot(str)
    def on_server_error(self, error: str):
        """服务器错误事件"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "服务器错误", error)
        self.output_text.append(f"错误: {error}")
    
    @pyqtSlot(str)
    def on_output_received(self, output: str):
        """服务器输出事件"""
        self.output_text.append(output)
        # 自动滚动到底部
        scrollbar = self.output_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_output(self):
        """清空输出"""
        self.output_text.clear()
    
    def check_server_health(self):
        """检查服务器健康状态"""
        if not self.server_manager.is_running:
            self.health_label.setText("健康检查: ⚪ 未检查")
            return
        
        try:
            url = f"{self.settings.server_url}/health"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                self.health_label.setText("健康检查: 🟢 正常")
            else:
                self.health_label.setText(f"健康检查: 🟡 异常 (状态码: {response.status_code})")
        except requests.exceptions.Timeout:
            self.health_label.setText("健康检查: 🟡 超时")
        except requests.exceptions.ConnectionError:
            self.health_label.setText("健康检查: 🔴 连接失败")
        except Exception as e:
            error_msg = str(e)[:20]
            self.health_label.setText(f"健康检查: 🔴 错误 ({error_msg})")
    
    def refresh(self):
        """刷新"""
        self.check_server_health()