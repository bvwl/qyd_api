#!/bin/bash

# XUI 数据库迁移脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  XUI 数据库迁移"
echo "=========================================="
echo ""

# 检查是否在 backend 目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 请在 backend 目录下运行此脚本"
    exit 1
fi

# 1. 生成迁移文件
echo "📝 步骤 1: 生成迁移文件..."
aerich migrate --name "add_xui_tables"
echo ""

# 2. 应用迁移
echo "🚀 步骤 2: 应用迁移..."
aerich upgrade
echo ""

# 3. 验证表
echo "✅ 步骤 3: 验证表结构..."
echo ""

# 读取数据库配置
DB_USER=$(grep DB_USER .env | cut -d '=' -f2)
DB_PASSWORD=$(grep DB_PASSWORD .env | cut -d '=' -f2)
DB_NAME=$(grep DB_NAME .env | cut -d '=' -f2)

echo "检查 XUI 相关表..."
mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES LIKE 'xui%';" 2>/dev/null || {
    echo "⚠️  无法连接数据库，跳过表验证"
    echo "   请手动检查: mysql -u $DB_USER -p $DB_NAME"
}
echo ""

# 4. 运行测试
echo "🧪 步骤 4: 运行迁移测试..."
python test_xui_migration.py
echo ""

echo "=========================================="
echo "  ✅ 迁移完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 启动服务: python start.py"
echo "2. 访问 API 文档: http://localhost:6080/docs"
echo "3. 测试 XUI 功能"
echo ""
