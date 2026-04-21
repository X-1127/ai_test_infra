"""
LLM Mock Server 桌面应用入口
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from desktop.ui.main_window import MainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("LLM Mock Server 管理器")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("XY")
    
    app.setStyle("Fusion")
    
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()