#!/bin/bash

echo "=========================================="
echo "邮件查看器完整修复脚本"
echo "=========================================="
echo ""

# 1. 安装依赖
echo "步骤 1/3: 安装前端依赖..."
cd frontend
npm install
echo "✓ 依赖安装完成"
echo ""

# 2. 检查路由初始化
echo "步骤 2/3: 检查数据库路由..."
cd ..
python backend/db/init_routes.py
echo "✓ 路由初始化完成"
echo ""

# 3. 提示重启
echo "步骤 3/3: 重启服务"
echo "=========================================="
echo ""
echo "请执行以下操作："
echo ""
echo "1. 如果前端正在运行，请重启："
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "2. 清除浏览器缓存："
echo "   - Mac: Cmd + Shift + R"
echo "   - Windows: Ctrl + Shift + R"
echo ""
echo "3. 或者在浏览器控制台执行："
echo "   localStorage.clear()"
echo "   location.reload()"
echo ""
echo "=========================================="
echo "修复完成！"
echo "=========================================="
