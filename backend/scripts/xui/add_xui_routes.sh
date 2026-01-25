#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "${SCRIPT_DIR}"

echo "==========================================
  添加 XUI 管理路由到数据库
=========================================="
echo

# 检查 Python 环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到 Python"
    exit 1
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: 未找到 .env 文件"
    echo "请确保数据库配置正确"
    echo
fi

# 执行脚本
echo "🚀 开始添加 XUI 路由..."
echo

python db/add_xui_routes.py

echo
echo "==========================================
  ✅ 完成！
=========================================="
echo
echo "下一步:"
echo "  1. 重启后端服务"
echo "  2. 刷新前端页面"
echo "  3. 在角色管理中为相应角色分配 XUI 路由权限"
echo
