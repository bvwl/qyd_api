#!/bin/bash

echo "=== 强制重新构建后端服务（不使用缓存） ==="
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.backend.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "⚠️  警告: 此操作将清除构建缓存并重新构建镜像"
echo "⚠️  这可能需要几分钟时间"
echo ""
read -p "是否继续？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 1
fi

echo ""
echo "1. 停止后端服务..."
docker compose -f docker-compose.backend.yml stop backend-api queue-worker

echo ""
echo "2. 删除旧镜像..."
docker rmi qyd_api-backend-api:latest 2>/dev/null || echo "  (backend-api 镜像不存在，跳过)"
docker rmi qyd_api-queue-worker:latest 2>/dev/null || echo "  (queue-worker 镜像不存在，跳过)"

echo ""
echo "3. 强制重新构建镜像（不使用缓存）..."
docker compose -f docker-compose.backend.yml build --no-cache backend-api queue-worker log-compressor

echo ""
echo "4. 启动后端服务（包含日志压缩服务）..."
docker compose -f docker-compose.backend.yml up -d backend-api queue-worker log-compressor

echo ""
echo "5. 等待服务启动..."
sleep 5

echo ""
echo "6. 查看服务状态..."
docker compose -f docker-compose.backend.yml ps

echo ""
echo "7. 查看 backend-api 日志..."
echo "--- Backend API ---"
docker compose -f docker-compose.backend.yml logs --tail=20 backend-api

echo ""
echo "8. 查看 queue-worker 日志..."
echo "--- Queue Worker ---"
docker compose -f docker-compose.backend.yml logs --tail=20 queue-worker

echo ""
echo "9. 查看 log-compressor 日志..."
echo "--- Log Compressor ---"
docker compose -f docker-compose.backend.yml logs --tail=20 log-compressor

echo ""
echo "=== 完成 ==="
echo ""
echo "查看实时日志:"
echo "  Backend API:    docker compose -f docker-compose.backend.yml logs -f backend-api"
echo "  Queue Worker:   docker compose -f docker-compose.backend.yml logs -f queue-worker"
echo "  Log Compressor: docker compose -f docker-compose.backend.yml logs -f log-compressor"
echo "  所有服务:       docker compose -f docker-compose.backend.yml logs -f"
echo ""
echo "访问 API 文档: http://192.168.13.6:6080/docs"
echo ""
echo "检查服务状态:"
echo "  docker compose -f docker-compose.backend.yml ps"

