#!/bin/bash

echo "=== 重启 Queue Worker 服务 ==="
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.backend.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "1. 停止 queue-worker..."
docker compose -f docker-compose.backend.yml stop queue-worker

echo ""
echo "2. 删除旧容器..."
docker compose -f docker-compose.backend.yml rm -f queue-worker

echo ""
echo "3. 启动 queue-worker..."
docker compose -f docker-compose.backend.yml up -d queue-worker

echo ""
echo "4. 等待服务启动..."
sleep 3

echo ""
echo "5. 查看服务状态..."
docker compose -f docker-compose.backend.yml ps queue-worker

echo ""
echo "6. 查看最近的日志..."
docker compose -f docker-compose.backend.yml logs --tail=30 queue-worker

echo ""
echo "=== 完成 ==="
echo ""
echo "查看实时日志: docker compose -f docker-compose.backend.yml logs -f queue-worker"
echo "检查服务状态: docker compose -f docker-compose.backend.yml ps"
