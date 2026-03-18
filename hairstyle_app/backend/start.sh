#!/bin/bash
# 发型 AI 后端 - 快速启动脚本

echo "======================================"
echo "  AI 发型生成 API - 快速启动"
echo "======================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 需要 Python 3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"
echo ""

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt -q

# 创建上传目录
mkdir -p uploads

# 启动服务
echo ""
echo "🚀 启动服务..."
echo "   API 地址：http://localhost:8000"
echo "   文档地址：http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 main.py
