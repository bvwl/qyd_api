#!/bin/bash

# ==========================================
# 重启高并发服务
# ==========================================

set -e

echo "=========================================="
echo "重启 QYD 高并发服务"
echo "=========================================="
echo ""

cd /opt/zy/qyd_api

# 配置
BACKEND_INSTANCES=5
QUEUE_INSTANCES=5

echo "配置："
echo "  后端实例: $BACKEND_INSTANCES"
echo "  队列实例: $QUEUE_INSTANCES"
echo ""

# 1. 停止所有服务
echo "[1/4] 停止所有服务..."
docker compose down
echo ""

# 2. 清理旧容器（可选）
echo "[2/4] 清理旧容器..."
docker compose rm -f
echo ""

# 3. 启动服务（高并发模式）
echo "[3/4] 启动服务（高并发模式）..."
echo "启动 Redis..."
docker compose up -d redis

echo "等待 Redis 启动..."
sleep 10

echo "启动后端和队列..."
docker compose up -d \
    --scale backend-api=$BACKEND_INSTANCES \
    --scale queue-worker=$QUEUE_INSTANCES

echo "启动前端和负载均衡..."
docker compose up -d frontend nginx-lb

echo ""
echo "等待服务启动（30秒）..."
sleep 30

# 4. 检查服务状态
echo ""
echo "[4/4] 检查服务状态"
echo "=========================================="
docker compose ps
echo ""

# 统计容器数量
RUNNING=$(docker compose ps --filter "status=running" | grep -c "Up" || echo "0")
echo "运行中的容器: $RUNNING"
echo ""

# 检查关键服务
echo "检查关键服务："
echo ""

# 检查 Redis
if docker compose ps redis | grep -q "Up"; then
    echo "✓ Redis: 运行中"
else
    echo "✗ Redis: 未运行"
fi

# 检查后端
BACKEND_COUNT=$(docker compose ps backend-api | grep -c "Up" || echo "0")
echo "✓ 后端 API: $BACKEND_COUNT/$BACKEND_INSTANCES 运行中"

# 检查队列
QUEUE_COUNT=$(docker compose ps queue-worker | grep -c "Up" || echo "0")
echo "✓ 队列 Worker: $QUEUE_COUNT/$QUEUE_INSTANCES 运行中"

# 检查前端
if docker compose ps frontend | grep -q "Up"; then
    echo "✓ 前端: 运行中"
else
    echo "✗ 前端: 未运行"
fi

# 检查 Nginx
if docker compose ps nginx-lb | grep -q "Up"; then
    echo "✓ Nginx LB: 运行中"
else
    echo "✗ Nginx LB: 未运行"
fi

echo ""
echo "=========================================="
echo "访问地址："
echo "  前端: http://192.168.13.6"
echo "  后端: http://192.168.13.6:6080"
echo "  API 文档: http://192.168.13.6:6080/docs"
echo ""

echo "查看日志："
echo "  docker compose logs -f"
echo "  docker compose logs -f backend-api"
echo "  docker compose logs -f nginx-lb"
echo ""

# 测试连接
echo "测试连接..."
echo ""

# 测试后端
if curl -s -o /dev/null -w "%{http_code}" http://192.168.13.6:6080/docs | grep -q "200"; then
    echo "✓ 后端 API 可访问"
else
    echo "✗ 后端 API 不可访问"
    echo "  查看日志: docker compose logs backend-api"
fi

# 测试前端
if curl -s -o /dev/null -w "%{http_code}" http://192.168.13.6/ | grep -q "200"; then
    echo "✓ 前端可访问"
else
    echo "✗ 前端不可访问"
    echo "  查看日志: docker compose logs frontend nginx-lb"
fi

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="
