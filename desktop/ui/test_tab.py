"""
测试界面标签页
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QCheckBox,
    QTextEdit, QMessageBox, QTabWidget, QSpinBox,
    QProgressBar, QFileDialog, QComboBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from desktop.services.api_client import APIClient
from desktop.config.settings import settings
import asyncio
from datetime import datetime
import time


class ChatTestThread(QThread):
    """聊天测试线程"""
    
    response_received = pyqtSignal(str, float)
    stream_chunk_received = pyqtSignal(str)
    stream_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client: APIClient, messages: list, stream: bool = False):
        super().__init__()
        self.api_client = api_client
        self.messages = messages
        self.stream = stream
    
    def run(self):
        """运行聊天测试"""
        try:
            start_time = time.time()
            
            if self.stream:
                self.run_stream_chat()
            else:
                self.run_normal_chat()
            
            duration = time.time() - start_time
            self.response_received.emit("完成", duration)
            
        except Exception as e:
            self.error_occurred.emit(f"聊天测试失败: {str(e)}")
    
    def run_normal_chat(self):
        """普通聊天"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.api_client.chat_completion(self.messages, stream=False)
            )
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                self.response_received.emit(content, 0)
            else:
                self.response_received.emit("无响应内容", 0)
        finally:
            loop.close()
    
    def run_stream_chat(self):
        """流式聊天"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.api_client.chat_completion(self.messages, stream=True)
            )
            
            if isinstance(result, str):
                for line in result.split('\n'):
                    if line.startswith('data: '):
                        data_str = line[6:]
                        if data_str == '[DONE]':
                            self.stream_finished.emit()
                            break
                        
                        try:
                            import json
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    self.stream_chunk_received.emit(content)
                        except json.JSONDecodeError:
                            pass
        finally:
            loop.close()


class BatchTestThread(QThread):
    """批量测试线程"""
    
    progress_updated = pyqtSignal(int, int)
    test_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client: APIClient, messages: list, count: int):
        super().__init__()
        self.api_client = api_client
        self.messages = messages
        self.count = count
    
    def run(self):
        """运行批量测试"""
        try:
            results = {
                'total': self.count,
                'success': 0,
                'failed': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0
            }
            
            for i in range(self.count):
                try:
                    start_time = time.time()
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.api_client.chat_completion(self.messages, stream=False)
                    )
                    loop.close()
                    
                    duration = time.time() - start_time
                    
                    results['success'] += 1
                    results['total_time'] += duration
                    results['min_time'] = min(results['min_time'], duration)
                    results['max_time'] = max(results['max_time'], duration)
                    
                except Exception as e:
                    results['failed'] += 1
                
                self.progress_updated.emit(i + 1, self.count)
            
            if results['success'] > 0:
                results['avg_time'] = results['total_time'] / results['success']
            if results['min_time'] == float('inf'):
                results['min_time'] = 0
            
            self.test_completed.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(f"批量测试失败: {str(e)}")


class PerformanceTestThread(QThread):
    """性能测试线程"""
    
    progress_updated = pyqtSignal(int, int)
    test_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client: APIClient, messages: list, duration: int, concurrent: int):
        super().__init__()
        self.api_client = api_client
        self.messages = messages
        self.duration = duration
        self.concurrent = concurrent
    
    def run(self):
        """运行性能测试"""
        try:
            results = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'requests_per_second': 0,
                'avg_response_time': 0,
                'min_response_time': float('inf'),
                'max_response_time': 0,
                'p95_response_time': 0,
                'p99_response_time': 0
            }
            
            response_times = []
            start_time = time.time()
            end_time = start_time + self.duration
            
            request_count = 0
            
            while time.time() < end_time:
                try:
                    req_start = time.time()
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.api_client.chat_completion(self.messages, stream=False)
                    )
                    loop.close()
                    
                    req_duration = time.time() - req_start
                    
                    results['successful_requests'] += 1
                    response_times.append(req_duration)
                    
                except Exception as e:
                    results['failed_requests'] += 1
                
                request_count += 1
                results['total_requests'] = request_count
                
                elapsed = time.time() - start_time
                self.progress_updated.emit(int(elapsed), self.duration)
            
            results['requests_per_second'] = results['total_requests'] / self.duration
            
            if response_times:
                results['avg_response_time'] = sum(response_times) / len(response_times)
                results['min_response_time'] = min(response_times)
                results['max_response_time'] = max(response_times)
                
                sorted_times = sorted(response_times)
                results['p95_response_time'] = sorted_times[int(len(sorted_times) * 0.95)]
                results['p99_response_time'] = sorted_times[int(len(sorted_times) * 0.99)]
            
            self.test_completed.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(f"性能测试失败: {str(e)}")


class TestTab(QWidget):
    """测试界面标签页"""
    
    def __init__(self, server_manager):
        super().__init__()
        self.server_manager = server_manager
        self.api_client = APIClient()
        
        self.chat_history = []
        
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("测试界面")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        self.tab_widget = QTabWidget()
        
        self.chat_test_tab = ChatTestTab(self.server_manager, self.api_client)
        self.batch_test_tab = BatchTestTab(self.server_manager, self.api_client)
        self.performance_test_tab = PerformanceTestTab(self.server_manager, self.api_client)
        
        self.tab_widget.addTab(self.chat_test_tab, "聊天测试")
        self.tab_widget.addTab(self.batch_test_tab, "批量测试")
        self.tab_widget.addTab(self.performance_test_tab, "性能测试")
        
        layout.addWidget(self.tab_widget)
    
    def refresh(self):
        """刷新"""
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()


class ChatTestTab(QWidget):
    """聊天测试标签页"""
    
    def __init__(self, server_manager, api_client: APIClient):
        super().__init__()
        self.server_manager = server_manager
        self.api_client = api_client
        self.chat_test_thread = None
        self.chat_history = []
        
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        settings_group = QGroupBox("测试设置")
        settings_layout = QHBoxLayout()
        
        self.stream_checkbox = QCheckBox("启用流式响应")
        self.stream_checkbox.setStyleSheet("font-size: 14px;")
        settings_layout.addWidget(self.stream_checkbox)
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("模型名称 (可选)")
        self.model_input.setMaximumWidth(200)
        settings_layout.addWidget(QLabel("模型:"))
        settings_layout.addWidget(self.model_input)
        
        self.clear_button = QPushButton("清空对话")
        self.clear_button.setMaximumWidth(100)
        self.clear_button.clicked.connect(self.clear_chat)
        settings_layout.addWidget(self.clear_button)
        
        settings_layout.addStretch()
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        chat_group = QGroupBox("聊天对话")
        chat_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                font-size: 13px;
            }
        """)
        self.chat_display.setMinimumHeight(300)
        chat_layout.addWidget(self.chat_display)
        
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入消息...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("发送")
        self.send_button.setMinimumWidth(80)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        chat_layout.addLayout(input_layout)
        chat_group.setLayout(chat_layout)
        layout.addWidget(chat_group)
        
        info_layout = QHBoxLayout()
        self.info_label = QLabel("提示: 输入消息后按回车或点击发送按钮")
        self.info_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
    
    def send_message(self):
        """发送消息"""
        if not self.server_manager.is_running:
            QMessageBox.warning(
                self,
                "服务器未运行",
                "请先启动服务器，然后再进行测试。\n\n您可以切换到'服务器'标签页启动服务器。"
            )
            return
        
        message = self.message_input.text().strip()
        if not message:
            QMessageBox.warning(self, "提示", "请输入消息")
            return
        
        self.message_input.clear()
        
        self.chat_history.append({"role": "user", "content": message})
        self.append_message("user", message)
        
        self.send_button.setEnabled(False)
        self.message_input.setEnabled(False)
        
        if self.stream_checkbox.isChecked():
            self.append_message("assistant", "正在生成响应...")
            self.chat_test_thread = ChatTestThread(
                self.api_client, 
                self.chat_history.copy(), 
                stream=True
            )
            self.chat_test_thread.stream_chunk_received.connect(self.on_stream_chunk)
            self.chat_test_thread.stream_finished.connect(self.on_stream_finished)
            self.chat_test_thread.response_received.connect(self.on_response_received)
            self.chat_test_thread.error_occurred.connect(self.on_error)
            self.chat_test_thread.start()
        else:
            self.append_message("assistant", "正在生成响应...")
            self.chat_test_thread = ChatTestThread(
                self.api_client, 
                self.chat_history.copy(), 
                stream=False
            )
            self.chat_test_thread.response_received.connect(self.on_response_received)
            self.chat_test_thread.error_occurred.connect(self.on_error)
            self.chat_test_thread.start()
    
    def append_message(self, role: str, content: str):
        """添加消息到显示区域"""
        if role == "user":
            color = "#2196F3"
            label = "用户"
        else:
            color = "#4CAF50"
            label = "助手"
        
        html = f'<div style="margin: 10px 0;"><span style="color: {color}; font-weight: bold;">[{label}]</span> {content}</div>'
        self.chat_display.append(html)
        
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @pyqtSlot(str)
    def on_stream_chunk(self, chunk: str):
        """接收到流式响应片段"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(chunk)
        self.chat_display.setTextCursor(cursor)
        
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @pyqtSlot()
    def on_stream_finished(self):
        """流式响应完成"""
        self.send_button.setEnabled(True)
        self.message_input.setEnabled(True)
        self.message_input.setFocus()
    
    @pyqtSlot(str, float)
    def on_response_received(self, content: str, duration: float):
        """接收到响应"""
        if content != "完成":
            self.chat_display.append(f'<div style="margin: 10px 0;"><span style="color: #4CAF50; font-weight: bold;">[助手]</span> {content}</div>')
        
        self.send_button.setEnabled(True)
        self.message_input.setEnabled(True)
        self.message_input.setFocus()
    
    @pyqtSlot(str)
    def on_error(self, error: str):
        """错误处理"""
        QMessageBox.critical(self, "错误", error)
        self.send_button.setEnabled(True)
        self.message_input.setEnabled(True)
    
    def clear_chat(self):
        """清空对话"""
        self.chat_display.clear()
        self.chat_history = []
    
    def refresh(self):
        """刷新"""
        pass


class BatchTestTab(QWidget):
    """批量测试标签页"""
    
    def __init__(self, server_manager, api_client: APIClient):
        super().__init__()
        self.server_manager = server_manager
        self.api_client = api_client
        self.batch_test_thread = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        settings_group = QGroupBox("测试设置")
        settings_layout = QVBoxLayout()
        
        count_row = QHBoxLayout()
        count_label = QLabel("测试次数:")
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(1, 1000)
        self.count_spinbox.setValue(10)
        self.count_spinbox.setSuffix(" 次")
        self.count_spinbox.setMinimumWidth(150)
        count_row.addWidget(count_label)
        count_row.addWidget(self.count_spinbox)
        count_row.addStretch()
        settings_layout.addLayout(count_row)
        
        message_row = QHBoxLayout()
        message_label = QLabel("测试消息:")
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入测试消息...")
        self.message_input.setText("你好，请介绍一下自己")
        message_row.addWidget(message_label)
        message_row.addWidget(self.message_input)
        settings_layout.addLayout(message_row)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("开始批量测试")
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
        self.start_button.clicked.connect(self.start_batch_test)
        control_layout.addWidget(self.start_button)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        progress_group = QGroupBox("测试进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("准备就绪")
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        results_group = QGroupBox("测试结果")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                font-size: 13px;
            }
        """)
        self.results_text.setMinimumHeight(200)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
    
    def start_batch_test(self):
        """开始批量测试"""
        if not self.server_manager.is_running:
            QMessageBox.warning(
                self,
                "服务器未运行",
                "请先启动服务器，然后再进行测试。\n\n您可以切换到'服务器'标签页启动服务器。"
            )
            return
        
        message = self.message_input.text().strip()
        if not message:
            QMessageBox.warning(self, "提示", "请输入测试消息")
            return
        
        count = self.count_spinbox.value()
        messages = [{"role": "user", "content": message}]
        
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.results_text.clear()
        self.progress_label.setText(f"正在测试 0/{count}...")
        
        self.batch_test_thread = BatchTestThread(self.api_client, messages, count)
        self.batch_test_thread.progress_updated.connect(self.on_progress_updated)
        self.batch_test_thread.test_completed.connect(self.on_test_completed)
        self.batch_test_thread.error_occurred.connect(self.on_error)
        self.batch_test_thread.start()
    
    @pyqtSlot(int, int)
    def on_progress_updated(self, current: int, total: int):
        """进度更新"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"正在测试 {current}/{total}...")
    
    @pyqtSlot(dict)
    def on_test_completed(self, results: dict):
        """测试完成"""
        self.progress_bar.setValue(100)
        self.progress_label.setText("测试完成")
        self.start_button.setEnabled(True)
        
        result_text = f"""
批量测试结果
{'=' * 50}
总测试次数: {results['total']}
成功次数: {results['success']}
失败次数: {results['failed']}
成功率: {(results['success'] / results['total'] * 100):.2f}%

响应时间统计:
- 总耗时: {results['total_time']:.2f} 秒
- 平均响应时间: {results['avg_time']:.3f} 秒
- 最小响应时间: {results['min_time']:.3f} 秒
- 最大响应时间: {results['max_time']:.3f} 秒
        """
        self.results_text.setText(result_text)
    
    @pyqtSlot(str)
    def on_error(self, error: str):
        """错误处理"""
        QMessageBox.critical(self, "错误", error)
        self.start_button.setEnabled(True)
        self.progress_label.setText("测试失败")
    
    def refresh(self):
        """刷新"""
        pass


class PerformanceTestTab(QWidget):
    """性能测试标签页"""
    
    def __init__(self, server_manager, api_client: APIClient):
        super().__init__()
        self.server_manager = server_manager
        self.api_client = api_client
        self.performance_test_thread = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        settings_group = QGroupBox("测试设置")
        settings_layout = QVBoxLayout()
        
        duration_row = QHBoxLayout()
        duration_label = QLabel("测试时长:")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(10, 300)
        self.duration_spinbox.setValue(30)
        self.duration_spinbox.setSuffix(" 秒")
        self.duration_spinbox.setMinimumWidth(150)
        duration_row.addWidget(duration_label)
        duration_row.addWidget(self.duration_spinbox)
        duration_row.addStretch()
        settings_layout.addLayout(duration_row)
        
        message_row = QHBoxLayout()
        message_label = QLabel("测试消息:")
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入测试消息...")
        self.message_input.setText("你好")
        message_row.addWidget(message_label)
        message_row.addWidget(self.message_input)
        settings_layout.addLayout(message_row)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("开始性能测试")
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
        self.start_button.clicked.connect(self.start_performance_test)
        control_layout.addWidget(self.start_button)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        progress_group = QGroupBox("测试进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("准备就绪")
        progress_layout.addWidget(self.progress_label)
        
        self.rps_label = QLabel("当前 RPS: 0")
        self.rps_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
        progress_layout.addWidget(self.rps_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        results_group = QGroupBox("测试结果")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                padding: 10px;
                border-radius: 4px;
                font-size: 13px;
            }
        """)
        self.results_text.setMinimumHeight(250)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
    
    def start_performance_test(self):
        """开始性能测试"""
        if not self.server_manager.is_running:
            QMessageBox.warning(
                self,
                "服务器未运行",
                "请先启动服务器，然后再进行测试。\n\n您可以切换到'服务器'标签页启动服务器。"
            )
            return
        
        message = self.message_input.text().strip()
        if not message:
            QMessageBox.warning(self, "提示", "请输入测试消息")
            return
        
        duration = self.duration_spinbox.value()
        messages = [{"role": "user", "content": message}]
        
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.results_text.clear()
        self.progress_label.setText(f"正在测试 0/{duration} 秒...")
        self.rps_label.setText("当前 RPS: 0")
        
        self.performance_test_thread = PerformanceTestThread(
            self.api_client, 
            messages, 
            duration, 
            concurrent=1
        )
        self.performance_test_thread.progress_updated.connect(self.on_progress_updated)
        self.performance_test_thread.test_completed.connect(self.on_test_completed)
        self.performance_test_thread.error_occurred.connect(self.on_error)
        self.performance_test_thread.start()
    
    @pyqtSlot(int, int)
    def on_progress_updated(self, current: int, total: int):
        """进度更新"""
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"正在测试 {current}/{total} 秒...")
    
    @pyqtSlot(dict)
    def on_test_completed(self, results: dict):
        """测试完成"""
        self.progress_bar.setValue(100)
        self.progress_label.setText("测试完成")
        self.start_button.setEnabled(True)
        self.rps_label.setText("当前 RPS: 0")
        
        result_text = f"""
性能测试结果
{'=' * 50}
测试时长: {self.duration_spinbox.value()} 秒

请求统计:
- 总请求数: {results['total_requests']}
- 成功请求数: {results['successful_requests']}
- 失败请求数: {results['failed_requests']}
- 成功率: {(results['successful_requests'] / results['total_requests'] * 100):.2f}%

性能指标:
- 每秒请求数 (RPS): {results['requests_per_second']:.2f}

响应时间统计:
- 平均响应时间: {results['avg_response_time']:.3f} 秒
- 最小响应时间: {results['min_response_time']:.3f} 秒
- 最大响应时间: {results['max_response_time']:.3f} 秒
- P95 响应时间: {results['p95_response_time']:.3f} 秒
- P99 响应时间: {results['p99_response_time']:.3f} 秒
        """
        self.results_text.setText(result_text)
    
    @pyqtSlot(str)
    def on_error(self, error: str):
        """错误处理"""
        QMessageBox.critical(self, "错误", error)
        self.start_button.setEnabled(True)
        self.progress_label.setText("测试失败")
    
    def refresh(self):
        """刷新"""
        pass