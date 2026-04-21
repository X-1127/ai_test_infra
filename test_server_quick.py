"""
快速测试服务器是否正常工作
"""

import requests
import time


def test_server():
    """测试服务器"""
    base_url = "http://localhost:8000"
    
    print("测试 LLM Mock Server...")
    print(f"服务器地址: {base_url}")
    print()
    
    # 测试健康检查
    print("1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ 健康检查通过: {response.json()}")
        else:
            print(f"✗ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 健康检查异常: {e}")
        return False
    
    print()
    
    # 测试根路径
    print("2. 测试根路径...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print(f"✓ 根路径访问成功")
        else:
            print(f"✗ 根路径访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 根路径访问异常: {e}")
        return False
    
    print()
    
    # 测试聊天完成
    print("3. 测试聊天完成...")
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json={
                "messages": [
                    {"role": "user", "content": "你好"}
                ]
            },
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 聊天完成成功")
            print(f"  响应: {data.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
        else:
            print(f"✗ 聊天完成失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 聊天完成异常: {e}")
        return False
    
    print()
    print("=" * 50)
    print("所有测试通过！服务器工作正常。")
    print("=" * 50)
    return True


if __name__ == "__main__":
    success = test_server()
    if not success:
        print("\n请检查服务器是否正在运行。")