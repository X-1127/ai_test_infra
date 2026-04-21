"""
用户界面模块
"""

from desktop.ui.main_window import MainWindow
from desktop.ui.server_tab import ServerTab
from desktop.ui.config_tab import ConfigTab
from desktop.ui.logs_tab import LogsTab
from desktop.ui.test_tab import TestTab
from desktop.ui.monitor_tab import MonitorTab

__all__ = [
    'MainWindow',
    'ServerTab',
    'ConfigTab',
    'LogsTab',
    'TestTab',
    'MonitorTab'
]