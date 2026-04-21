"""
日志查看标签页
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QComboBox,
    QTextEdit, QMessageBox, QFileDialog, QCheckBox,
    QSpinBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from desktop.services.api_client import APIClient
from desktop.config.settings import settings
import asyncio
from datetime import datetime


class LogsAPIThread(QThread):
    """日志API调用线程"""
    
    logs_loaded = pyqtSignal(list, int)
    logs_searched = pyqtSignal(list, str)
    logs_cleared = pyqtSignal()
    stats_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
    
    def run_get_logs(self, log_type: str = None, limit: int = 100, offset: int = 0):
        """获取日志"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.api_client.get_logs(log_type=log_type, limit=limit, offset=offset)
            )
            self.logs_loaded.emit(result.get('logs', []), result.get('count', 0))
        except Exception as e:
            self.error_occurred.emit(f"获取日志失败: {str(e)}")
        finally:
            loop.close()
    
    def run_search_logs(self, keyword: str, log_type: str = None, limit: int = 100):
        """搜索日志"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.api_client.search_logs(keyword=keyword, log_type=log_type, limit=limit)
            )
            self.logs_searched.emit(result.get('logs', []), keyword)
        except Exception as e:
            self.error_occurred.emit(f"搜索日志失败: {str(e)}")
        finally:
            loop.close()
    
    def run_clear_logs(self):
        """清空日志"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.api_client.clear_logs())
            self.logs_cleared.emit()
        except Exception as e:
            self.error_occurred.emit(f"清空日志失败: {str(e)}")
        finally:
            loop.close()
    
    def run_get_stats(self):
        """获取日志统计"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.api_client.get("/v1/logs/stats"))
            self.stats_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(f"获取日志统计失败: {str(e)}")
        finally:
            loop.close()


class LogsTab(QWidget):
    """日志查看标签页"""
    
    def __init__(self, server_manager):
        super().__init__()
        self.server_manager = server_manager
        self.api_client = APIClient()
        self.api_thread = LogsAPIThread(self.api_client)
        
        self.auto_refresh_enabled = False
        self.auto_refresh_interval = 5  # 默认5秒
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.auto_refresh_logs)
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("日志查看")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 过滤和搜索区域
        filter_group = QGroupBox("过滤和搜索")
        filter_layout = QVBoxLayout()
        
        filter_row = QHBoxLayout()
        
        type_label = QLabel("日志类型:")
        self.log_type_combo = QComboBox()
        self.log_type_combo.addItems(["全部", "请求", "错误", "访问"])
        self.log_type_combo.setMinimumWidth(120)
        filter_row.addWidget(type_label)
        filter_row.addWidget(self.log_type_combo)
        
        search_label = QLabel("搜索:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索日志...")
        self.search_input.setMinimumWidth(200)
        filter_row.addWidget(search_label)
        filter_row.addWidget(self.search_input)
        
        self.search_button = QPushButton("搜索")
        self.search_button.setMaximumWidth(80)
        self.search_button.clicked.connect(self.search_logs)
        filter_row.addWidget(self.search_button)
        
        filter_row.addStretch()
        filter_layout.addLayout(filter_row)
        
        limit_row = QHBoxLayout()
        
        limit_label = QLabel("显示条数:")
        self.limit_spinbox = QSpinBox()
        self.limit_spinbox.setRange(10, 1000)
        self.limit_spinbox.setValue(100)
        self.limit_spinbox.setSuffix(" 条")
        self.limit_spinbox.setMinimumWidth(100)
        limit_row.addWidget(limit_label)
        limit_row.addWidget(self.limit_spinbox)
        
        self.auto_refresh_checkbox = QCheckBox("自动刷新")
        self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
        limit_row.addWidget(self.auto_refresh_checkbox)
        
        refresh_interval_label = QLabel("刷新间隔:")
        self.refresh_interval_spinbox = QSpinBox()
        self.refresh_interval_spinbox.setRange(1, 60)
        self.refresh_interval_spinbox.setValue(5)
        self.refresh_interval_spinbox.setSuffix(" 秒")
        self.refresh_interval_spinbox.setMinimumWidth(100)
        self.refresh_interval_spinbox.setEnabled(False)
        self.refresh_interval_spinbox.valueChanged.connect(self.change_refresh_interval)
        limit_row.addWidget(refresh_interval_label)
        limit_row.addWidget(self.refresh_interval_spinbox)
        
        limit_row.addStretch()
        filter_layout.addLayout(limit_row)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # 操作按钮
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.refresh_button.clicked.connect(self.load_logs)
        
        self.clear_button = QPushButton("清空日志")
        self.clear_button.setMinimumHeight(35)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        self.clear_button.clicked.connect(self.clear_logs)
        
        self.export_button = QPushButton("导出日志")
        self.export_button.setMinimumHeight(35)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.export_button.clicked.connect(self.export_logs)
        
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        # 日志统计信息
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("统计: 总日志: 0 | 请求: 0 | 错误: 0 | 访问: 0")
        self.stats_label.setStyleSheet("font-size: 12px; color: #666;")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # 日志显示区域
        output_group = QGroupBox("日志内容")
        output_layout = QVBoxLayout()
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("""
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
        self.logs_text.setMinimumHeight(400)
        self.logs_text.setPlaceholderText("日志内容将显示在这里...")
        
        output_layout.addWidget(self.logs_text)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
    
    def connect_signals(self):
        """连接信号"""
        self.api_thread.logs_loaded.connect(self.on_logs_loaded)
        self.api_thread.logs_searched.connect(self.on_logs_searched)
        self.api_thread.logs_cleared.connect(self.on_logs_cleared)
        self.api_thread.stats_loaded.connect(self.on_stats_loaded)
        self.api_thread.error_occurred.connect(self.on_error)
    
    def load_logs(self):
        """加载日志"""
        if not self.server_manager.is_running:
            QMessageBox.warning(
                self,
                "服务器未运行",
                "请先启动服务器，然后再查看日志。\n\n您可以切换到'服务器'标签页启动服务器。"
            )
            return
        
        log_type = None
        type_text = self.log_type_combo.currentText()
        if type_text != "全部":
            log_type_map = {"请求": "request", "错误": "error", "访问": "access"}
            log_type = log_type_map.get(type_text)
        
        limit = self.limit_spinbox.value()
        self.api_thread.run_get_logs(log_type=log_type, limit=limit)
    
    def search_logs(self):
        """搜索日志"""
        if not self.server_manager.is_running:
            QMessageBox.warning(
                self,
                "服务器未运行",
                "请先启动服务器，然后再搜索日志。\n\n您可以切换到'服务器'标签页启动服务器。"
            )
            return
        
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索关键词")
            return
        
        log_type = None
        type_text = self.log_type_combo.currentText()
        if type_text != "全部":
            log_type_map = {"请求": "request", "错误": "error", "访问": "access"}
            log_type = log_type_map.get(type_text)
        
        limit = self.limit_spinbox.value()
        self.api_thread.run_search_logs(keyword=keyword, log_type=log_type, limit=limit)
    
    def clear_logs(self):
        """清空日志"""
        if not self.server_manager.is_running:
            QMessageBox.warning(
                self,
                "服务器未运行",
                "请先启动服务器，然后再清空日志。\n\n您可以切换到'服务器'标签页启动服务器。"
            )
            return
        
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有日志吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.api_thread.run_clear_logs()
    
    def export_logs(self):
        """导出日志"""
        if not self.logs_text.toPlainText():
            QMessageBox.warning(self, "提示", "没有可导出的日志")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出日志",
            f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.logs_text.toPlainText())
                QMessageBox.information(self, "成功", f"日志已导出到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出日志失败: {str(e)}")
    
    def toggle_auto_refresh(self, checked: bool):
        """切换自动刷新"""
        self.auto_refresh_enabled = checked
        self.refresh_interval_spinbox.setEnabled(checked)
        
        if checked:
            self.auto_refresh_timer.start(self.auto_refresh_interval * 1000)
        else:
            self.auto_refresh_timer.stop()
    
    def change_refresh_interval(self, value: int):
        """更改刷新间隔"""
        self.auto_refresh_interval = value
        if self.auto_refresh_enabled:
            self.auto_refresh_timer.setInterval(value * 1000)
    
    def auto_refresh_logs(self):
        """自动刷新日志"""
        self.load_logs()
    
    @pyqtSlot(list, int)
    def on_logs_loaded(self, logs: list, count: int):
        """日志加载完成"""
        self.display_logs(logs)
        self.load_stats()
    
    @pyqtSlot(list, str)
    def on_logs_searched(self, logs: list, keyword: str):
        """日志搜索完成"""
        self.display_logs(logs)
        QMessageBox.information(self, "搜索完成", f"找到 {len(logs)} 条包含 '{keyword}' 的日志")
    
    @pyqtSlot()
    def on_logs_cleared(self):
        """日志清空完成"""
        self.logs_text.clear()
        QMessageBox.information(self, "成功", "日志已清空")
        self.load_stats()
    
    @pyqtSlot(dict)
    def on_stats_loaded(self, stats: dict):
        """日志统计加载完成"""
        total = stats.get('total_logs', 0)
        by_type = stats.get('by_type', {})
        request_count = by_type.get('request', 0)
        error_count = by_type.get('error', 0)
        access_count = by_type.get('access', 0)
        
        self.stats_label.setText(
            f"统计: 总日志: {total} | 请求: {request_count} | 错误: {error_count} | 访问: {access_count}"
        )
    
    @pyqtSlot(str)
    def on_error(self, error: str):
        """错误处理"""
        QMessageBox.critical(self, "错误", error)
    
    def display_logs(self, logs: list):
        """显示日志"""
        self.logs_text.clear()
        
        if not logs:
            self.logs_text.append("没有找到日志")
            return
        
        for log in logs:
            log_type = log.get('type', 'unknown')
            timestamp = log.get('timestamp', '')
            message = log.get('message', '')
            
            # 根据日志类型设置不同的颜色
            if log_type == 'error':
                color = '#ff6b6b'
            elif log_type == 'request':
                color = '#4ecdc4'
            elif log_type == 'access':
                color = '#95e1d3'
            else:
                color = '#d4d4d4'
            
            log_line = f'<span style="color: {color};">[{timestamp}] [{log_type.upper()}] {message}</span>'
            self.logs_text.append(log_line)
        
        # 自动滚动到底部
        scrollbar = self.logs_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def load_stats(self):
        """加载日志统计"""
        if self.server_manager.is_running:
            self.api_thread.run_get_stats()
    
    def refresh(self):
        """刷新"""
        self.load_logs()