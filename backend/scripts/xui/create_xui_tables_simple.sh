#!/bin/bash

# XUI 表创建脚本（最简单方式 - 直接使用 MySQL）

echo "=========================================="
echo "  创建 XUI 数据库表（MySQL 直接执行）"
echo "=========================================="
echo ""

# 检查是否在 backend 目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 错误: 请在 backend 目录下运行此脚本"
    exit 1
fi

# 加载 .env 文件
if [ -f ".env" ]; then
    echo "📄 加载 .env 配置..."
    export $(cat .env | grep -v '^#' | xargs)
    echo ""
fi

# 获取数据库配置
DB_USER=${DB_USER:-qyd}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME:-qyd}
DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3306}

echo "📊 数据库配置:"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   User: $DB_USER"
echo "   Database: $DB_NAME"
echo ""

# 执行 SQL
echo "🚀 执行 SQL 脚本..."
echo ""

# 使用 -p 参数传递密码（注意 -p 和密码之间没有空格）
if [ -n "$DB_PASSWORD" ]; then
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < db/create_xui_tables.sql
else
    mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" "$DB_NAME" < db/create_xui_tables.sql
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "  ✅ 表创建完成！"
    echo "=========================================="
    echo ""
    
    # 验证表
    echo "📊 验证表是否创建:"
    if [ -n "$DB_PASSWORD" ]; then
        mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES LIKE 'xui%';"
    else
        mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" "$DB_NAME" -e "SHOW TABLES LIKE 'xui%';"
    fi
    
    echo ""
    echo "下一步:"
    echo "  1. 查看表结构: mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p\"$DB_PASSWORD\" $DB_NAME -e \"DESC xui_server;\""
    echo "  2. 测试功能: python test_xui_migration.py"
    echo "  3. 启动服务: python start.py"
    echo ""
else
    echo ""
    echo "❌ 表创建失败"
    echo ""
    echo "请检查:"
    echo "  1. 数据库连接是否正常"
    echo "  2. 用户是否有创建表的权限"
    echo "  3. proxy_account 表是否存在"
    echo ""
    exit 1
fi
