#!/bin/bash

# XUI 表创建脚本（使用 Python + aiomysql）

set -e

echo "=========================================="
echo "  创建 XUI 数据库表"
echo "=========================================="
echo ""

# 检查是否在 backend 目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 请在 backend 目录下运行此脚本"
    exit 1
fi

# 检查 aiomysql 是否安装
echo "🔍 检查依赖..."
python -c "import aiomysql" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  未安装 aiomysql"
    echo ""
    read -p "是否现在安装? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 安装 aiomysql..."
        pip install aiomysql
        echo ""
    else
        echo "❌ 需要 aiomysql 才能继续"
        exit 1
    fi
fi

echo "✅ 依赖检查通过"
echo ""

# 执行 Python 脚本
python db/apply_xui_tables.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  🎉 完成！"
    echo "=========================================="
else
    echo ""
    echo "❌ 创建失败"
    exit 1
fi
