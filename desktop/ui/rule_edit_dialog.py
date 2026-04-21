"""
规则编辑对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt


class RuleEditDialog(QDialog):
    """规则编辑对话框"""
    
    def __init__(self, parent=None, rule_data=None):
        super().__init__(parent)
        self.rule_data = rule_data
        self.init_ui()
        
        if rule_data:
            self.setWindowTitle("编辑规则")
            self.load_rule_data()
        else:
            self.setWindowTitle("添加规则")
    
    def init_ui(self):
        """初始化用户界面"""
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 触发词
        trigger_layout = QHBoxLayout()
        trigger_label = QLabel("触发词:")
        trigger_label.setMinimumWidth(80)
        self.trigger_input = QLineEdit()
        self.trigger_input.setPlaceholderText("输入触发词或正则表达式")
        trigger_layout.addWidget(trigger_label)
        trigger_layout.addWidget(self.trigger_input)
        layout.addLayout(trigger_layout)
        
        # 回复内容
        response_layout = QHBoxLayout()
        response_label = QLabel("回复内容:")
        response_label.setMinimumWidth(80)
        self.response_input = QLineEdit()
        self.response_input.setPlaceholderText("输入回复内容")
        response_layout.addWidget(response_label)
        response_layout.addWidget(self.response_input)
        layout.addLayout(response_layout)
        
        # 匹配类型
        match_type_layout = QHBoxLayout()
        match_type_label = QLabel("匹配类型:")
        match_type_label.setMinimumWidth(80)
        self.match_type_combo = QComboBox()
        self.match_type_combo.addItems(["exact", "contains", "regex"])
        match_type_layout.addWidget(match_type_label)
        match_type_layout.addWidget(self.match_type_combo)
        layout.addLayout(match_type_layout)
        
        # 启用状态
        enabled_layout = QHBoxLayout()
        self.enabled_checkbox = QCheckBox("启用此规则")
        self.enabled_checkbox.setChecked(True)
        enabled_layout.addWidget(self.enabled_checkbox)
        enabled_layout.addStretch()
        layout.addLayout(enabled_layout)
        
        # 按钮
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setMinimumWidth(80)
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)
        
        self.ok_button = QPushButton("确定")
        self.ok_button.setMinimumWidth(80)
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)
        
        layout.addLayout(buttons_layout)
    
    def load_rule_data(self):
        """加载规则数据"""
        if self.rule_data:
            self.trigger_input.setText(self.rule_data.get('trigger', ''))
            self.response_input.setText(self.rule_data.get('response', ''))
            self.match_type_combo.setCurrentText(self.rule_data.get('match_type', 'contains'))
            self.enabled_checkbox.setChecked(self.rule_data.get('enabled', True))
    
    def get_rule_data(self):
        """获取规则数据"""
        trigger = self.trigger_input.text().strip()
        response = self.response_input.text().strip()
        
        if not trigger:
            QMessageBox.warning(self, "错误", "请输入触发词！")
            return None
        
        if not response:
            QMessageBox.warning(self, "错误", "请输入回复内容！")
            return None
        
        return {
            "trigger": trigger,
            "response": response,
            "match_type": self.match_type_combo.currentText(),
            "enabled": self.enabled_checkbox.isChecked()
        }
    
    def accept(self):
        """确定按钮点击"""
        rule_data = self.get_rule_data()
        if rule_data:
            super().accept()