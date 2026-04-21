"""
桌面应用基础功能测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from desktop.ui.main_window import MainWindow


def test_desktop_app():
    """测试桌面应用"""
    print("开始测试桌面应用...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("LLM Mock Server 管理器测试")
    
    try:
        print("创建主窗口...")
        window = MainWindow()
        print("✓ 主窗口创建成功")
        
        print("检查标签页...")
        assert window.tab_widget.count() == 5, "应该有5个标签页"
        print("✓ 标签页数量正确")
        
        print("检查服务器管理标签页...")
        assert hasattr(window.server_tab, 'server_manager'), "服务器标签页应该有server_manager"
        print("✓ 服务器管理标签页正确")
        
        print("检查配置...")
        from desktop.config.settings import settings
        assert settings.server_port == 8000, "默认端口应该是8000"
        print("✓ 配置加载正确")
        
        print("检查API客户端...")
        from desktop.services.api_client import APIClient
        client = APIClient()
        assert client.base_url == "http://localhost:8000", "API客户端URL应该正确"
        print("✓ API客户端初始化正确")
        
        print("\n所有基础测试通过！")
        print("桌面应用基础框架工作正常。")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_desktop_app()
    sys.exit(0 if success else 1)