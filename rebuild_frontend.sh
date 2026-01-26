#!/bin/bash

# ==========================================
# 重新构建前端容器
# ==========================================

set -e

echo "=========================================="
echo "重新构建前端容器"
echo "=========================================="

# 1. 加载环境变量
echo ""
echo "[1/6] 加载环境变量..."
if [ -f .env.high_concurrency ]; then
    export $(grep -v '^#' .env.high_concurrency | xargs)
    echo "  ✓ 已加载 .env.high_concurrency"
    echo "  VITE_API_BASE_URL=${VITE_API_BASE_URL}"
else
    echo "  ⚠️  未找到 .env.high_concurrency"
    exit 1
fi

# 2. 停止前端容器
echo ""
echo "[2/6] 停止前端容器..."
docker compose stop frontend

# 3. 删除前端容器
echo ""
echo "[3/6] 删除前端容器..."
docker compose rm -f frontend

# 4. 删除前端镜像（强制重新构建）
echo ""
echo "[4/6] 删除前端镜像..."
docker compose images frontend -q | xargs -r docker rmi -f || echo "  没有找到前端镜像"

# 5. 重新构建前端镜像
echo ""
echo "[5/6] 重新构建前端镜像..."
echo "  使用 API 地址: ${VITE_API_BASE_URL}"
docker compose build --no-cache frontend

# 6. 启动所有服务（保持正确的副本数）
echo ""
echo "[6/6] 启动所有服务..."
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 等待服务启动
echo ""
echo "等待前端启动..."
sleep 10

# 检查服务状态
echo ""
echo "=========================================="
echo "服务状态"
echo "=========================================="
docker compose ps

# 统计容器数量
echo ""
echo "容器统计："
echo "  后端 API: $(docker compose ps backend-api --format '{{.Name}}' | wc -l) 个"
echo "  队列 Worker: $(docker compose ps queue-worker --format '{{.Name}}' | wc -l) 个"

# 测试前端
echo ""
echo "=========================================="
echo "测试前端"
echo "=========================================="
echo "测试前端首页："
curl -I http://192.168.13.6/ 2>&1 | head -1

echo ""
echo "检查前端构建的 API 地址："
echo "  请在浏览器中打开开发者工具，查看 Network 标签"
echo "  应该看到请求发送到: http://192.168.13.6:6080"

echo ""
echo ""
echo "=========================================="
echo "✅ 重建完成！"
echo "=========================================="
echo ""
echo "请刷新浏览器（Ctrl+Shift+R 强制刷新）"
echo ""
echo "如果还有问题："
echo "  1. 清除浏览器缓存"
echo "  2. 检查浏览器控制台的 Network 标签"
echo "  3. 查看前端容器日志: docker compose logs frontend"
