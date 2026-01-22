#!/bin/bash

echo "=========================================="
echo "前端重启脚本"
echo "=========================================="
echo ""

# 1. 停止前端进程
echo "1. 停止前端进程..."
pkill -f "vite" 2>/dev/null
sleep 2
echo "✓ 前端进程已停止"
echo ""

# 2. 清理缓存
echo "2. 清理前端缓存..."
rm -rf frontend/node_modules/.vite
rm -rf frontend/dist
rm -rf frontend/.vite
echo "✓ 缓存已清理"
echo ""

# 3. 检查端口
echo "3. 检查端口3000..."
PORT_IN_USE=$(lsof -ti:3000)
if [ ! -z "$PORT_IN_USE" ]; then
    echo "⚠ 端口3000被占用，正在释放..."
    kill -9 $PORT_IN_USE 2>/dev/null
    sleep 1
    echo "✓ 端口已释放"
else
    echo "✓ 端口3000空闲"
fi
echo ""

echo "=========================================="
echo "准备完成！"
echo "=========================================="
echo ""
echo "请手动执行以下命令启动前端："
echo ""
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "然后访问: http://localhost:3000/user/permission"
echo ""
