"""
性能监控标签页
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGroupBox, QCheckBox, QSpinBox,
    QTextEdit, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from desktop.services.api_client import APIClient
from desktop.config.settings import settings
import asyncio
from datetime import datetime
from collections import deque


class MonitorAPIThread(QThread):
    """监控API调用线程"""
    
    stats_loaded = pyqtSignal(dict)
    logs_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
    
    def run_get_stats(self):
        """获取统计信息"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.api_client.get("/v1/logs/stats"))
            self.stats_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(f"获取统计信息失败: {str(e)}")
        finally:
            loop.close()
    
    def run_get_logs(self, log_type: str = "request", limit: int = 100):
        """获取日志"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.api_client.get_logs(log_type=log_type, limit=limit)
            )
            self.logs_loaded.emit(result.get('logs', []))
        except Exception as e:
            self.error_occurred.emit(f"获取日志失败: {str(e)}")
        finally:
            loop.close()


class MonitorTab(QWidget):
    """性能监控标签页"""
    
    def __init__(self, server_manager):
        super().__init__()
        self.server_manager = server_manager
        self.api_client = APIClient()
        self.api_thread = MonitorAPIThread(self.api_client)
        
        self.auto_refresh_enabled = False
        self.auto_refresh_interval = 5  # 默认5秒
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.auto_refresh)
        
        # 历史数据（用于趋势显示）
        self.response_time_history = deque(maxlen=60)  # 保存最近60个数据点
        self.request_count_history = deque(maxlen=60)
        self.error_count_history = deque(maxlen=60)
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("性能监控")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 控制区域
        control_group = QGroupBox("监控设置")
        control_layout = QHBoxLayout()
        
        self.auto_refresh_checkbox = QCheckBox("自动刷新")
        self.auto_refresh_checkbox.setStyleSheet("font-size: 14px;")
        self.auto_refresh_checkbox.toggled.connect(self.toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh_checkbox)
        
        refresh_interval_label = QLabel("刷新间隔:")
        self.refresh_interval_spinbox = QSpinBox()
        self.refresh_interval_spinbox.setRange(1, 60)
        self.refresh_interval_spinbox.setValue(5)
        self.refresh_interval_spinbox.setSuffix(" 秒")
        self.refresh_interval_spinbox.setMinimumWidth(100)
        self.refresh_interval_spinbox.setEnabled(False)
        self.refresh_interval_spinbox.valueChanged.connect(self.change_refresh_interval)
        control_layout.addWidget(refresh_interval_label)
        control_layout.addWidget(self.refresh_interval_spinbox)
        
        self.refresh_button = QPushButton("立即刷新")
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
        self.refresh_button.clicked.connect(self.refresh)
        control_layout.addWidget(self.refresh_button)
        
        control_layout.addStretch()
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 实时指标
        metrics_group = QGroupBox("实时性能指标")
        metrics_layout = QGridLayout()
        
        # 总请求数
        total_label = QLabel("总请求数:")
        total_label.setStyleSheet("font-size: 12px; color: #666;")
        self.total_requests_label = QLabel("0")
        self.total_requests_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2196F3;")
        metrics_layout.addWidget(total_label, 0, 0)
        metrics_layout.addWidget(self.total_requests_label, 1, 0)
        
        # 成功请求数
        success_label = QLabel("成功请求:")
        success_label.setStyleSheet("font-size: 12px; color: #666;")
        self.success_requests_label = QLabel("0")
        self.success_requests_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #4CAF50;")
        metrics_layout.addWidget(success_label, 0, 1)
        metrics_layout.addWidget(self.success_requests_label, 1, 1)
        
        # 错误请求数
        error_label = QLabel("错误请求:")
        error_label.setStyleSheet("font-size: 12px; color: #666;")
        self.error_requests_label = QLabel("0")
        self.error_requests_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f44336;")
        metrics_layout.addWidget(error_label, 0, 2)
        metrics_layout.addWidget(self.error_requests_label, 1, 2)
        
        # 平均响应时间
        avg_time_label = QLabel("平均响应时间:")
        avg_time_label.setStyleSheet("font-size: 12px; color: #666;")
        self.avg_response_time_label = QLabel("0 ms")
        self.avg_response_time_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF9800;")
        metrics_layout.addWidget(avg_time_label, 0, 3)
        metrics_layout.addWidget(self.avg_response_time_label, 1, 3)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        # 请求统计
        stats_group = QGroupBox("请求统计")
        stats_layout = QGridLayout()
        
        # 按类型统计
        type_label = QLabel("按类型:")
        type_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(type_label, 0, 0)
        
        self.request_count_label = QLabel("请求: 0")
        self.request_count_label.setStyleSheet("font-size: 13px; color: #2196F3;")
        stats_layout.addWidget(self.request_count_label, 0, 1)
        
        self.error_count_label = QLabel("错误: 0")
        self.error_count_label.setStyleSheet("font-size: 13px; color: #f44336;")
        stats_layout.addWidget(self.error_count_label, 0, 2)
        
        self.access_count_label = QLabel("访问: 0")
        self.access_count_label.setStyleSheet("font-size: 13px; color: #4CAF50;")
        stats_layout.addWidget(self.access_count_label, 0, 3)
        
        # 错误率
        error_rate_label = QLabel("错误率:")
        error_rate_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        stats_layout.addWidget(error_rate_label, 1, 0)
        
        self.error_rate_label = QLabel("0.00%")
        self.error_rate_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f44336;")
        stats_layout.addWidget(self.error_rate_label, 1, 1, 1, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # 响应时间统计
        response_time_group = QGroupBox("响应时间统计")
        response_time_layout = QGridLayout()
        
        min_label = QLabel("最小:")
        min_label.setStyleSheet("font-size: 12px; color: #666;")
        self.min_response_time_label = QLabel("0 ms")
        self.min_response_time_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4CAF50;")
        response_time_layout.addWidget(min_label, 0, 0)
        response_time_layout.addWidget(self.min_response_time_label, 0, 1)
        
        max_label = QLabel("最大:")
        max_label.setStyleSheet("font-size: 12px; color: #666;")
        self.max_response_time_label = QLabel("0 ms")
        self.max_response_time_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f44336;")
        response_time_layout.addWidget(max_label, 0, 2)
        response_time_layout.addWidget(self.max_response_time_label, 0, 3)
        
        avg_label = QLabel("平均:")
        avg_label.setStyleSheet("font-size: 12px; color: #666;")
        self.avg_time_detail_label = QLabel("0 ms")
        self.avg_time_detail_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #FF9800;")
        response_time_layout.addWidget(avg_label, 1, 0)
        response_time_layout.addWidget(self.avg_time_detail_label, 1, 1)
        
        p95_label = QLabel("P95:")
        p95_label.setStyleSheet("font-size: 12px; color: #666;")
        self.p95_response_time_label = QLabel("0 ms")
        self.p95_response_time_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #9C27B0;")
        response_time_layout.addWidget(p95_label, 1, 2)
        response_time_layout.addWidget(self.p95_response_time_label, 1, 3)
        
        response_time_group.setLayout(response_time_layout)
        layout.addWidget(response_time_group)
        
        # 最近错误
        recent_errors_group = QGroupBox("最近错误")
        recent_errors_layout = QVBoxLayout()
        
        self.recent_errors_text = QTextEdit()
        self.recent_errors_text.setReadOnly(True)
        self.recent_errors_text.setStyleSheet("""
            QTextEdit {
                background-color: #fff5f5;
                color: #d32f2f;
                padding: 10px;
                border-radius: 4px;
                font-size: 12px;
                border: 1px solid #ffcdd2;
            }
        """)
        self.recent_errors_text.setMinimumHeight(150)
        self.recent_errors_text.setPlaceholderText("最近没有错误")
        recent_errors_layout.addWidget(self.recent_errors_text)
        
        recent_errors_group.setLayout(recent_errors_layout)
        layout.addWidget(recent_errors_group)
        
        # 状态信息
        status_layout = QHBoxLayout()
        self.last_update_label = QLabel("最后更新: -")
        self.last_update_label.setStyleSheet("color: #666; font-size: 12px;")
        status_layout.addWidget(self.last_update_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
    
    def connect_signals(self):
        """连接信号"""
        self.api_thread.stats_loaded.connect(self.on_stats_loaded)
        self.api_thread.logs_loaded.connect(self.on_logs_loaded)
        self.api_thread.error_occurred.connect(self.on_error)
    
    def refresh(self):
        """刷新"""
        self.load_stats()
        self.load_recent_errors()
        self.load_request_logs()
    
    def auto_refresh(self):
        """自动刷新"""
        self.refresh()
    
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
    
    def load_stats(self):
        """加载统计信息"""
        if not self.server_manager.is_running:
            QMessageBox.warning(
                self,
                "服务器未运行",
                "请先启动服务器，然后再查看监控。\n\n您可以切换到'服务器'标签页启动服务器。"
            )
            return
        
        self.api_thread.run_get_stats()
    
    def load_recent_errors(self):
        """加载最近错误"""
        if not self.server_manager.is_running:
            return
        
        self.api_thread.run_get_logs(log_type="error", limit=10)
    
    def load_request_logs(self):
        """加载请求日志用于响应时间统计"""
        if not self.server_manager.is_running:
            return
        
        self.api_thread.run_get_logs(log_type="request", limit=100)
    
    @pyqtSlot(dict)
    def on_stats_loaded(self, stats: dict):
        """统计信息加载完成"""
        total_logs = stats.get('total_logs', 0)
        by_type = stats.get('by_type', {})
        request_count = by_type.get('request', 0)
        error_count = by_type.get('error', 0)
        access_count = by_type.get('access', 0)
        recent_errors = stats.get('recent_errors', 0)
        avg_response_time = stats.get('avg_response_time', 0)
        
        # 更新实时指标
        self.total_requests_label.setText(str(total_logs))
        self.success_requests_label.setText(str(request_count))
        self.error_requests_label.setText(str(error_count))
        self.avg_response_time_label.setText(f"{avg_response_time:.1f} ms")
        
        # 更新请求统计
        self.request_count_label.setText(f"请求: {request_count}")
        self.error_count_label.setText(f"错误: {error_count}")
        self.access_count_label.setText(f"访问: {access_count}")
        
        # 计算错误率
        if total_logs > 0:
            error_rate = (error_count / total_logs) * 100
            self.error_rate_label.setText(f"{error_rate:.2f}%")
        else:
            self.error_rate_label.setText("0.00%")
        
        # 更新最后更新时间
        self.last_update_label.setText(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 保存历史数据
        self.response_time_history.append(avg_response_time)
        self.request_count_history.append(request_count)
        self.error_count_history.append(error_count)
    
    @pyqtSlot(list)
    def on_logs_loaded(self, logs: list):
        """日志加载完成"""
        # 判断日志类型
        if not logs:
            return
        
        log_type = logs[0].get('type', '')
        
        if log_type == 'error':
            # 处理错误日志
            self.recent_errors_text.clear()
            
            if not logs:
                self.recent_errors_text.append("最近没有错误")
                return
            
            for log in logs:
                timestamp = log.get('timestamp', '')
                message = log.get('message', '')
                error_line = f"[{timestamp}] {message}"
                self.recent_errors_text.append(error_line)
            
            # 自动滚动到底部
            scrollbar = self.recent_errors_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        elif log_type == 'request':
            # 处理请求日志，更新响应时间统计
            self.update_response_time_stats(logs)
    
    def update_response_time_stats(self, logs: list):
        """更新响应时间统计"""
        print(f"[DEBUG] update_response_time_stats called with {len(logs)} logs")
        
        request_logs = [log for log in logs if log.get('type') == 'request']
        print(f"[DEBUG] Found {len(request_logs)} request logs")
    
        request_logs = [log for log in logs if log.get('type') == 'request']
        print(f"[DEBUG] Found {len(request_logs)} request logs")
    
        if not request_logs:
            print("[DEBUG] No request logs found, returning")
            return
    
        response_times = [log.get('duration_ms', 0) for log in request_logs]
        print(f"[DEBUG] Response times: {response_times}")
    
        if response_times:
            min_time = min(response_times)
            max_time = max(response_times)
            avg_time = sum(response_times) / len(response_times)
        
            sorted_times = sorted(response_times)
            p95_time = sorted_times[int(len(sorted_times) * 0.95)]
        
            print(f"[DEBUG] Min: {min_time}, Max: {max_time}, Avg: {avg_time}, P95: {p95_time}")
        
            # 确保标签存在
            if hasattr(self, 'min_response_time_label'):
                self.min_response_time_label.setText(f"{min_time:.1f} ms")
            if hasattr(self, 'max_response_time_label'):
                self.max_response_time_label.setText(f"{max_time:.1f} ms")
            if hasattr(self, 'avg_time_detail_label'):
                self.avg_time_detail_label.setText(f"{avg_time:.1f} ms")
            if hasattr(self, 'p95_response_time_label'):
                self.p95_response_time_label.setText(f"{p95_time:.1f} ms")
    
    @pyqtSlot(str)
    def on_error(self, error: str):
        """错误处理"""
        QMessageBox.critical(self, "错误", error)