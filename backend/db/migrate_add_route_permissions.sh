#!/bin/bash
# 添加路由权限字段的数据库迁移脚本

echo "=========================================="
echo "  添加路由权限字段"
echo "=========================================="
echo ""

# 1. 生成迁移文件
echo "1. 生成迁移文件..."
cd /path/to/backend
aerich migrate --name "add_route_permissions"

# 2. 应用迁移
echo ""
echo "2. 应用迁移..."
aerich upgrade

echo ""
echo "=========================================="
echo "  迁移完成"
echo "=========================================="
echo ""
echo "新增字段："
echo "  - route_type: 路由类型(1:菜单,2:按钮,3:接口)"
echo "  - permission: 权限标识"
echo "  - api_method: API方法"
echo "  - api_path: API路径"
echo ""
