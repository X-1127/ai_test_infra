"""
配置管理标签页
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QGroupBox, QCheckBox,
    QSpinBox, QComboBox, QMessageBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont
from desktop.services.api_client import APIClient
from desktop.config.settings import settings
from desktop.ui.rule_edit_dialog import RuleEditDialog
import asyncio
from PyQt6.QtCore import QThread, pyqtSignal


class ConfigAPIThread(QThread):
    """配置API调用线程"""
    
    config_loaded = pyqtSignal(dict)
    config_updated = pyqtSignal(dict)
    config_reset = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
    
    def run_get_config(self):
        """获取配置"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            config = loop.run_until_complete(self.api_client.get_injection_config())
            self.config_loaded.emit(config)
        except Exception as e:
            self.error_occurred.emit(f"获取配置失败: {str(e)}")
        finally:
            loop.close()
    
    def run_update_config(self, config: dict):
        """更新配置"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.api_client.update_injection_config(config))
            self.config_updated.emit(result)
        except Exception as e:
            self.error_occurred.emit(f"更新配置失败: {str(e)}")
        finally:
            loop.close()
    
    def run_reset_config(self):
        """重置配置"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.api_client.reset_injection_config())
            self.config_reset.emit(result)
        except Exception as e:
            self.error_occurred.emit(f"重置配置失败: {str(e)}")
        finally:
            loop.close()


class ConfigTab(QWidget):
    """配置管理标签页"""
    
    def __init__(self, server_manager):
        super().__init__()
        self.server_manager = server_manager
        self.api_client = APIClient()
        self.api_thread = ConfigAPIThread(self.api_client)
        
        self.init_ui()
        self.connect_signals()
        # 不在初始化时自动加载配置，避免弹出警告
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel("配置管理")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 添加操作按钮
        buttons_layout = QHBoxLayout()
        
        self.load_config_button = QPushButton("加载配置")
        self.load_config_button.setMinimumHeight(35)
        self.load_config_button.setStyleSheet("""
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
        self.load_config_button.clicked.connect(self.load_config)
        
        self.reset_config_button = QPushButton("重置配置")
        self.reset_config_button.setMinimumHeight(35)
        self.reset_config_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #c66900;
            }
        """)
        self.reset_config_button.clicked.connect(self.reset_config)
        
        buttons_layout.addWidget(self.load_config_button)
        buttons_layout.addWidget(self.reset_config_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.tab_widget = QTabWidget()
        
        self.delay_tab = DelayConfigTab(self.api_thread)
        self.fault_tab = FaultConfigTab(self.api_thread)
        self.yaml_tab = YAMLConfigTab(self.api_client)
        
        self.tab_widget.addTab(self.delay_tab, "延迟注入")
        self.tab_widget.addTab(self.fault_tab, "故障注入")
        self.tab_widget.addTab(self.yaml_tab, "YAML配置")
        
        layout.addWidget(self.tab_widget)
    
    def connect_signals(self):
        """连接信号"""
        self.api_thread.config_loaded.connect(self.on_config_loaded)
        self.api_thread.config_updated.connect(self.on_config_updated)
        self.api_thread.config_reset.connect(self.on_config_reset)
        self.api_thread.error_occurred.connect(self.on_error)
    
    def load_config(self):
        """加载配置"""
        # 检查服务器是否在运行
        if not self.server_manager.is_running:
            QMessageBox.warning(
                self, 
                "服务器未运行", 
                "请先启动服务器，然后再加载配置。\n\n您可以切换到'服务器'标签页启动服务器。"
            )
            return
        
        # 服务器运行中，尝试加载配置
        try:
            self.api_thread.run_get_config()
        except Exception as e:
            QMessageBox.critical(
                self, 
                "加载配置失败", 
                f"无法连接到服务器：{str(e)}\n\n请检查：\n1. 服务器是否正在运行\n2. 服务器地址是否正确\n3. 网络连接是否正常"
            )
    
    def reset_config(self):
        """重置配置"""
        # 检查服务器是否在运行
        if not self.server_manager.is_running:
            QMessageBox.warning(
                self, 
                "服务器未运行", 
                "请先启动服务器，然后再重置配置。\n\n您可以切换到'服务器'标签页启动服务器。"
            )
            return
        
        # 确认重置
        reply = QMessageBox.question(
            self, 
            "确认重置", 
            "确定要将所有配置重置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_thread.run_reset_config()
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "重置配置失败", 
                    f"无法重置配置：{str(e)}"
                )
    
    @pyqtSlot(dict)
    def on_config_loaded(self, config: dict):
        """配置加载完成"""
        self.delay_tab.load_config(config.get('delay', {}))
        self.fault_tab.load_config(config.get('fault', {}))
         # 同时加载 YAML 配置
        self.load_yaml_config()

    @pyqtSlot(dict)
    def on_config_updated(self, config: dict):
        """配置更新完成"""
        QMessageBox.information(self, "成功", "配置更新成功！")
    
    @pyqtSlot(dict)
    def on_config_reset(self, config: dict):
        """配置重置完成"""
        QMessageBox.information(self, "成功", "配置已重置为默认值！")
        self.on_config_loaded(config)
    
    @pyqtSlot(str)
    def on_error(self, error: str):
        """错误处理"""
        QMessageBox.critical(self, "错误", error)
    
    def refresh(self):
        """刷新配置"""
        self.load_config()
        self.load_yaml_config()
    
    def load_yaml_config(self):
        """加载YAML配置"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.api_client.get_yaml_config())
            loop.close()
        
            # API 返回的数据结构是 {"enabled": bool, "config": {...}}
            # 需要传递 config 部分给 yaml_tab.load_config
            if 'config' in result:
                self.yaml_tab.load_config(result['config'])
            else:
                self.yaml_tab.load_config(result)
        except Exception as e:
            # YAML配置加载失败不影响其他配置
            import traceback
            print(f"加载YAML配置失败: {str(e)}")
            traceback.print_exc()


class DelayConfigTab(QWidget):
    """延迟注入配置标签页"""
    
    def __init__(self, api_thread: ConfigAPIThread):
        super().__init__()
        self.api_thread = api_thread
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        enabled_group = QGroupBox("启用延迟注入")
        enabled_layout = QHBoxLayout()
        
        self.enabled_checkbox = QCheckBox("启用延迟注入")
        self.enabled_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: bold;
            }
        """)
        enabled_layout.addWidget(self.enabled_checkbox)
        enabled_layout.addStretch()
        enabled_group.setLayout(enabled_layout)
        layout.addWidget(enabled_group)
        
        delay_group = QGroupBox("延迟设置")
        delay_layout = QVBoxLayout()
        
        min_layout = QHBoxLayout()
        min_label = QLabel("最小延迟（毫秒）:")
        self.min_spinbox = QSpinBox()
        self.min_spinbox.setRange(0, 10000)
        self.min_spinbox.setValue(0)
        self.min_spinbox.setSuffix(" ms")
        self.min_spinbox.setMinimumWidth(150)
        min_layout.addWidget(min_label)
        min_layout.addWidget(self.min_spinbox)
        min_layout.addStretch()
        delay_layout.addLayout(min_layout)
        
        max_layout = QHBoxLayout()
        max_label = QLabel("最大延迟（毫秒）:")
        self.max_spinbox = QSpinBox()
        self.max_spinbox.setRange(0, 10000)
        self.max_spinbox.setValue(1000)
        self.max_spinbox.setSuffix(" ms")
        self.max_spinbox.setMinimumWidth(150)
        max_layout.addWidget(max_label)
        max_layout.addWidget(self.max_spinbox)
        max_layout.addStretch()
        delay_layout.addLayout(max_layout)
        
        delay_group.setLayout(delay_layout)
        layout.addWidget(delay_group)
        
        buttons_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("应用配置")
        self.apply_button.setMinimumHeight(40)
        self.apply_button.setStyleSheet("""
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
        """)
        self.apply_button.clicked.connect(self.apply_config)
        
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
    
    def load_config(self, config: dict):
        """加载配置"""
        self.enabled_checkbox.setChecked(config.get('enabled', False))
        self.min_spinbox.setValue(config.get('min_delay_ms', 0))
        self.max_spinbox.setValue(config.get('max_delay_ms', 1000))
    
    def apply_config(self):
        """应用配置"""
        config = {
            "delay": {
                "enabled": self.enabled_checkbox.isChecked(),
                "min_delay_ms": self.min_spinbox.value(),
                "max_delay_ms": self.max_spinbox.value()
            }
        }
        self.api_thread.run_update_config(config)


class FaultConfigTab(QWidget):
    """故障注入配置标签页"""
    
    def __init__(self, api_thread: ConfigAPIThread):
        super().__init__()
        self.api_thread = api_thread
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        enabled_group = QGroupBox("启用故障注入")
        enabled_layout = QHBoxLayout()
        
        self.enabled_checkbox = QCheckBox("启用故障注入")
        self.enabled_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                font-weight: bold;
            }
        """)
        enabled_layout.addWidget(self.enabled_checkbox)
        enabled_layout.addStretch()
        enabled_group.setLayout(enabled_layout)
        layout.addWidget(enabled_group)
        
        fault_type_group = QGroupBox("故障类型")
        fault_type_layout = QVBoxLayout()
        
        type_layout = QHBoxLayout()
        type_label = QLabel("故障类型:")
        self.fault_type_combo = QComboBox()
        self.fault_type_combo.addItems([
            "none",
            "http_error",
            "timeout",
            "invalid_response",
            "empty_response"
        ])
        self.fault_type_combo.setMinimumWidth(200)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.fault_type_combo)
        type_layout.addStretch()
        fault_type_layout.addLayout(type_layout)
        
        fault_type_group.setLayout(fault_type_layout)
        layout.addWidget(fault_type_group)
        
        http_group = QGroupBox("HTTP错误设置")
        http_layout = QVBoxLayout()
        
        status_layout = QHBoxLayout()
        status_label = QLabel("HTTP状态码:")
        self.status_spinbox = QSpinBox()
        self.status_spinbox.setRange(400, 599)
        self.status_spinbox.setValue(500)
        self.status_spinbox.setMinimumWidth(100)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_spinbox)
        status_layout.addStretch()
        http_layout.addLayout(status_layout)
        
        message_layout = QHBoxLayout()
        message_label = QLabel("错误消息:")
        self.message_input = QLineEdit("Internal server error")
        message_layout.addWidget(message_label)
        message_layout.addWidget(self.message_input)
        http_layout.addLayout(message_layout)
        
        http_group.setLayout(http_layout)
        layout.addWidget(http_group)
        
        probability_group = QGroupBox("故障概率")
        probability_layout = QHBoxLayout()
        
        prob_label = QLabel("故障注入概率:")
        self.probability_spinbox = QSpinBox()
        self.probability_spinbox.setRange(0, 100)
        self.probability_spinbox.setValue(100)
        self.probability_spinbox.setSuffix("%")
        self.probability_spinbox.setMinimumWidth(100)
        probability_layout.addWidget(prob_label)
        probability_layout.addWidget(self.probability_spinbox)
        probability_layout.addStretch()
        probability_group.setLayout(probability_layout)
        layout.addWidget(probability_group)
        
        buttons_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("应用配置")
        self.apply_button.setMinimumHeight(40)
        self.apply_button.setStyleSheet("""
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
        """)
        self.apply_button.clicked.connect(self.apply_config)
        
        buttons_layout.addWidget(self.apply_button)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
    
    def load_config(self, config: dict):
        """加载配置"""
        self.enabled_checkbox.setChecked(config.get('enabled', False))
        self.fault_type_combo.setCurrentText(config.get('fault_type', 'none'))
        self.status_spinbox.setValue(config.get('http_status_code', 500))
        self.message_input.setText(config.get('error_message', 'Internal server error'))
        self.probability_spinbox.setValue(int(config.get('probability', 1.0) * 100))
    
    def apply_config(self):
        """应用配置"""
        config = {
            "fault": {
                "enabled": self.enabled_checkbox.isChecked(),
                "fault_type": self.fault_type_combo.currentText(),
                "http_status_code": self.status_spinbox.value(),
                "error_message": self.message_input.text(),
                "probability": self.probability_spinbox.value() / 100.0
            }
        }
        self.api_thread.run_update_config(config)


class YAMLConfigTab(QWidget):
    """YAML配置标签页"""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.config_data = None
        self.rules = []
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # YAML配置状态
        status_group = QGroupBox("YAML配置状态")
        status_layout = QVBoxLayout()
        
        status_row = QHBoxLayout()
        self.status_label = QLabel("状态: ⚪ 未加载")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        status_layout.addLayout(status_row)
        
        buttons_row = QHBoxLayout()
        
        self.enable_button = QPushButton("启用YAML配置")
        self.enable_button.setMinimumHeight(35)
        self.enable_button.setStyleSheet("""
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
        self.enable_button.clicked.connect(self.enable_yaml_config)
        
        self.disable_button = QPushButton("禁用YAML配置")
        self.disable_button.setMinimumHeight(35)
        self.disable_button.setStyleSheet("""
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
        self.disable_button.clicked.connect(self.disable_yaml_config)
        
        self.reload_button = QPushButton("重载配置")
        self.reload_button.setMinimumHeight(35)
        self.reload_button.setStyleSheet("""
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
        self.reload_button.clicked.connect(self.reload_yaml_config)
        
        buttons_row.addWidget(self.enable_button)
        buttons_row.addWidget(self.disable_button)
        buttons_row.addWidget(self.reload_button)
        status_layout.addLayout(buttons_row)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 规则管理
        rules_group = QGroupBox("预设回复规则")
        rules_layout = QVBoxLayout()
        
        # 规则表格
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(4)
        self.rules_table.setHorizontalHeaderLabels(["状态", "类型", "触发词", "回复"])
        self.rules_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.rules_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.rules_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.rules_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.rules_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.rules_table.setMinimumHeight(300)
        rules_layout.addWidget(self.rules_table)
        
        # 规则操作按钮
        rule_buttons_layout = QHBoxLayout()
        
        self.add_rule_button = QPushButton("添加规则")
        self.add_rule_button.setMinimumHeight(35)
        self.add_rule_button.setStyleSheet("""
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
        self.add_rule_button.clicked.connect(self.add_rule)
        
        self.edit_rule_button = QPushButton("编辑规则")
        self.edit_rule_button.setMinimumHeight(35)
        self.edit_rule_button.setEnabled(False)
        self.edit_rule_button.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.edit_rule_button.clicked.connect(self.edit_rule)
        
        self.delete_rule_button = QPushButton("删除规则")
        self.delete_rule_button.setMinimumHeight(35)
        self.delete_rule_button.setEnabled(False)
        self.delete_rule_button.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.delete_rule_button.clicked.connect(self.delete_rule)
        
        self.toggle_rule_button = QPushButton("启用/禁用")
        self.toggle_rule_button.setMinimumHeight(35)
        self.toggle_rule_button.setEnabled(False)
        self.toggle_rule_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #c66900;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.toggle_rule_button.clicked.connect(self.toggle_rule)
        
        rule_buttons_layout.addWidget(self.add_rule_button)
        rule_buttons_layout.addWidget(self.edit_rule_button)
        rule_buttons_layout.addWidget(self.delete_rule_button)
        rule_buttons_layout.addWidget(self.toggle_rule_button)
        rule_buttons_layout.addStretch()
        rules_layout.addLayout(rule_buttons_layout)
        
        rules_group.setLayout(rules_layout)
        layout.addWidget(rules_group)
        
        # 连接表格选择信号
        self.rules_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addStretch()
    
    def load_config(self, config: dict):
        """加载配置"""
        self.config_data = config
        
        if config.get('enabled', False):
            self.status_label.setText("状态: 🟢 已启用")
        else:
            self.status_label.setText("状态: ⚫ 已禁用")
        
        # 加载规则列表
        self.rules = config.get('rules', [])
        self.update_rules_table()
    
    def update_rules_table(self):
        """更新规则表格"""
        self.rules_table.setRowCount(len(self.rules))
        
        for row, rule in enumerate(self.rules):
            # 状态
            enabled = rule.get('enabled', True)
            status_item = QTableWidgetItem("✅" if enabled else "❌")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rules_table.setItem(row, 0, status_item)
            
            # 类型
            match_type = rule.get('match_type', 'contains')
            type_item = QTableWidgetItem(match_type)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.rules_table.setItem(row, 1, type_item)
            
            # 触发词
            trigger = rule.get('trigger', '')
            trigger_item = QTableWidgetItem(trigger)
            self.rules_table.setItem(row, 2, trigger_item)
            
            # 回复
            response = rule.get('response', '')
            response_item = QTableWidgetItem(response)
            self.rules_table.setItem(row, 3, response_item)
    
    def on_selection_changed(self):
        """表格选择改变"""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        has_selection = len(selected_rows) > 0
        
        self.edit_rule_button.setEnabled(has_selection)
        self.delete_rule_button.setEnabled(has_selection)
        self.toggle_rule_button.setEnabled(has_selection)
    
    def add_rule(self):
        """添加规则"""
        dialog = RuleEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            rule_data = dialog.get_rule_data()
            if rule_data:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self.api_client.add_yaml_rule(rule_data))
                    loop.close()
                    
                    self.load_config(result)
                    QMessageBox.information(self, "成功", "规则添加成功！")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"添加规则失败：{str(e)}")
    
    def edit_rule(self):
        """编辑规则"""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        rule_data = self.rules[row]
        
        dialog = RuleEditDialog(self, rule_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_rule_data = dialog.get_rule_data()
            if new_rule_data:
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self.api_client.update_yaml_rule(row, new_rule_data))
                    loop.close()
                    
                    self.load_config(result)
                    QMessageBox.information(self, "成功", "规则更新成功！")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"更新规则失败：{str(e)}")
    
    def delete_rule(self):
        """删除规则"""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        rule = self.rules[row]
        
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除规则 '{rule.get('trigger', '')}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.api_client.delete_yaml_rule(row))
                loop.close()
                
                self.load_config(result)
                QMessageBox.information(self, "成功", "规则删除成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除规则失败：{str(e)}")
    
    def toggle_rule(self):
        """切换规则启用状态"""
        selected_rows = self.rules_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        rule = self.rules[row]
        current_enabled = rule.get('enabled', True)
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            if current_enabled:
                result = loop.run_until_complete(self.api_client.disable_yaml_rule(row))
            else:
                result = loop.run_until_complete(self.api_client.enable_yaml_rule(row))
            loop.close()
            
            self.load_config(result)
            QMessageBox.information(self, "成功", "规则状态已更新！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新规则状态失败：{str(e)}")
    
    def enable_yaml_config(self):
        """启用YAML配置"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.api_client.enable_yaml_config())
            loop.close()
            
            self.load_config(result)
            QMessageBox.information(self, "成功", "YAML配置已启用！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"启用YAML配置失败：{str(e)}")
    
    def disable_yaml_config(self):
        """禁用YAML配置"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.api_client.disable_yaml_config())
            loop.close()
            
            self.load_config(result)
            QMessageBox.information(self, "成功", "YAML配置已禁用！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"禁用YAML配置失败：{str(e)}")
    
    def reload_yaml_config(self):
        """重载YAML配置"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.api_client.reload_yaml_config())
            loop.close()
            
            self.load_config(result)
            QMessageBox.information(self, "成功", "YAML配置已重载！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重载YAML配置失败：{str(e)}")