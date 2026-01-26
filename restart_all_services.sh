#!/bin/bash

# ==========================================
# 重启所有服务（保持正确的副本数）
# ==========================================

set -e

echo "=========================================="
echo "重启所有服务"
echo "=========================================="

# 1. 加载环境变量
echo ""
echo "[1/3] 加载环境变量..."
if [ -f .env.high_concurrency ]; then
    export $(grep -v '^#' .env.high_concurrency | xargs)
    echo "  ✓ 已加载 .env.high_concurrency"
else
    echo "  ⚠️  未找到 .env.high_concurrency"
    exit 1
fi

# 2. 启动所有服务（指定副本数）
echo ""
echo "[2/3] 启动所有服务..."
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 等待服务启动
echo ""
echo "等待服务启动..."
sleep 15

# 3. 检查服务状态
echo ""
echo "[3/3] 检查服务状态..."
echo ""
docker compose ps

# 统计容器数量
echo ""
echo "=========================================="
echo "容器统计"
echo "=========================================="
echo "后端 API 容器数量："
docker compose ps backend-api --format "{{.Name}}" | wc -l

echo ""
echo "队列 Worker 容器数量："
docker compose ps queue-worker --format "{{.Name}}" | wc -l

echo ""
echo "其他服务："
docker compose ps frontend nginx-lb redis --format "table {{.Name}}\t{{.Status}}"

# 测试接口
echo ""
echo "=========================================="
echo "测试接口"
echo "=========================================="
echo "测试前端（80端口）："
curl -I http://192.168.13.6/ 2>&1 | head -1

echo ""
echo "测试后端 API（6080端口）："
curl -I http://192.168.13.6:6080/docs 2>&1 | head -1

echo ""
echo ""
echo "=========================================="
echo "✅ 完成！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  前端: http://192.168.13.6/"
echo "  API文档: http://192.168.13.6:6080/docs"
