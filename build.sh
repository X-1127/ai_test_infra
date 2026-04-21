#!/bin/bash

echo "========================================"
echo "LLM Mock Server 打包脚本 (Linux/Mac)"
echo "========================================"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python，请先安装 Python 3.13+"
    exit 1
fi

echo "[1/6] 检查 Python 环境... OK"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[2/6] 创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "错误: 创建虚拟环境失败"
        exit 1
    fi
    echo "[2/6] 创建虚拟环境... OK"
else
    echo "[2/6] 虚拟环境已存在... OK"
fi
echo ""

# 激活虚拟环境
source venv/bin/activate
echo "[3/6] 激活虚拟环境... OK"
echo ""

# 安装依赖
echo "[4/6] 安装项目依赖..."
pip install -e ".[desktop,build]" --upgrade
if [ $? -ne 0 ]; then
    echo "错误: 安装依赖失败"
    exit 1
fi
echo "[4/6] 安装项目依赖... OK"
echo ""

# 清理旧的构建文件
echo "[5/6] 清理旧的构建文件..."
rm -rf build dist
echo "[5/6] 清理旧的构建文件... OK"
echo ""

# 开始打包
echo "[6/6] 开始打包（这可能需要几分钟）..."
echo ""
pyinstaller --clean build.spec
if [ $? -ne 0 ]; then
    echo ""
    echo "错误: 打包失败"
    exit 1
fi

echo ""
echo "========================================"
echo "打包完成！"
echo "========================================"
echo ""
echo "可执行文件位置: dist/LLM_Mock_Server"
echo ""
echo "您可以将 dist/LLM_Mock_Server 分发给其他用户"
echo "用户无需安装 Python 即可直接运行"
echo ""