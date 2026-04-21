"""
主窗口
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QStatusBar, QMenuBar, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon
from desktop.config.settings import settings
from desktop.ui.server_tab import ServerTab
from desktop.ui.config_tab import ConfigTab
from desktop.ui.logs_tab import LogsTab
from desktop.ui.test_tab import TestTab
from desktop.ui.monitor_tab import MonitorTab


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.settings = settings
        self.settings.load_config()
        
        self.init_ui()
        self.init_menu()
        self.init_status_bar()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("LLM Mock Server 管理器")
        self.setMinimumSize(1000, 700)
        self.resize(self.settings.window_width, self.settings.window_height)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        self.server_tab = ServerTab()
        self.config_tab = ConfigTab(self.server_tab.server_manager)
        self.logs_tab = LogsTab(self.server_tab.server_manager)
        self.test_tab = TestTab(self.server_tab.server_manager)
        self.monitor_tab = MonitorTab(self.server_tab.server_manager)
        
        self.tab_widget.addTab(self.server_tab, "服务器")
        self.tab_widget.addTab(self.config_tab, "配置")
        self.tab_widget.addTab(self.logs_tab, "日志")
        self.tab_widget.addTab(self.test_tab, "测试")
        self.tab_widget.addTab(self.monitor_tab, "监控")
        
        layout.addWidget(self.tab_widget)
        
        self.apply_styles()
    
    def init_menu(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件(&F)")
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu("视图(&V)")
        
        refresh_action = QAction("刷新(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_current_tab)
        view_menu.addAction(refresh_action)
        
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_bar.showMessage("就绪")
    
    def apply_styles(self):
        """应用样式"""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #e0e0e0;
            color: #333;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            color: #0078d4;
            font-weight: bold;
        }
        
        QTabBar::tab:hover {
            background-color: #f0f0f0;
        }
        
        QStatusBar {
            background-color: #0078d4;
            color: white;
        }
        """
        self.setStyleSheet(style)
    
    def refresh_current_tab(self):
        """刷新当前标签页"""
        current_tab = self.tab_widget.currentWidget()
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()
    
    def show_about(self):
        """显示关于对话框"""
        from PyQt6.QtWidgets import QMessageBox
        
        QMessageBox.about(
            self,
            "关于 LLM Mock Server 管理器",
            """
            <h3>LLM Mock Server 管理器</h3>
            <p>版本: 1.0.0</p>
            <p>一个功能完整的LLM模拟服务器管理工具</p>
            <p>作者: XY</p>
            <p>© 2026 All rights reserved</p>
            """
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        self.settings.window_width = self.width()
        self.settings.window_height = self.height()
        self.settings.save_config()
        
        if hasattr(self.server_tab, 'server_manager'):
            if self.server_tab.server_manager.is_running:
                from PyQt6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "确认退出",
                    "服务器正在运行，确定要退出吗？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.server_tab.server_manager.stop_server()
                    event.accept()
                else:
                    event.ignore()
            else:
                event.accept()
        else:
            event.accept()