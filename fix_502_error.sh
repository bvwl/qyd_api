#!/bin/bash

# ==========================================
# 修复 502 错误 - 完全重启所有服务
# ==========================================

set -e

echo "=========================================="
echo "修复 502 错误"
echo "=========================================="

# 1. 加载环境变量
echo ""
echo "[1/5] 加载环境变量..."
if [ -f .env.high_concurrency ]; then
    export $(grep -v '^#' .env.high_concurrency | xargs)
    echo "  ✓ 已加载 .env.high_concurrency"
else
    echo "  ⚠️  未找到 .env.high_concurrency"
    exit 1
fi

# 2. 停止所有服务
echo ""
echo "[2/5] 停止所有服务..."
docker compose down

# 3. 清理网络（可能有残留）
echo ""
echo "[3/5] 清理 Docker 网络..."
docker network prune -f

# 4. 重新启动所有服务
echo ""
echo "[4/5] 启动所有服务..."
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 5. 等待服务启动
echo ""
echo "[5/5] 等待服务启动..."
sleep 20

# 检查服务状态
echo ""
echo "=========================================="
echo "服务状态"
echo "=========================================="
docker compose ps

# 测试连接
echo ""
echo "=========================================="
echo "测试连接"
echo "=========================================="

echo ""
echo "1. 测试前端容器内部："
docker compose exec frontend wget -q -O- http://localhost/ | head -c 100 && echo "  ✓ 前端容器内部正常" || echo "  ✗ 前端容器内部失败"

echo ""
echo "2. 测试 Nginx LB 到前端的连接："
docker compose exec nginx-lb wget -q -O- http://frontend/ | head -c 100 && echo "  ✓ Nginx 可以连接到前端" || echo "  ✗ Nginx 无法连接到前端"

echo ""
echo "3. 测试 Nginx LB 到后端的连接："
docker compose exec nginx-lb wget -q -O- http://backend-api:6080/docs | head -c 100 && echo "  ✓ Nginx 可以连接到后端" || echo "  ✗ Nginx 无法连接到后端"

echo ""
echo "4. 测试外部访问前端："
curl -I http://192.168.13.6/ 2>&1 | head -1

echo ""
echo "5. 测试外部访问后端："
curl -I http://192.168.13.6:6080/docs 2>&1 | head -1

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "如果还有问题，请查看："
echo "  1. 前端日志: docker compose logs frontend"
echo "  2. Nginx 日志: docker compose logs nginx-lb"
echo "  3. Nginx 错误日志: docker compose exec nginx-lb cat /var/log/nginx/qyd_error.log"
