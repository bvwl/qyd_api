#!/bin/bash

echo "=== 重启 Docker 后端服务 ==="
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.backend.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "1. 停止后端服务..."
docker compose -f docker-compose.backend.yml stop backend-api

echo ""
echo "2. 重新构建镜像（包含最新代码）..."
docker compose -f docker-compose.backend.yml build backend-api

echo ""
echo "3. 启动后端服务..."
docker compose -f docker-compose.backend.yml up -d backend-api

echo ""
echo "4. 等待服务启动..."
sleep 5

echo ""
echo "5. 查看服务状态..."
docker compose -f docker-compose.backend.yml ps backend-api

echo ""
echo "6. 查看最近的日志..."
docker compose -f docker-compose.backend.yml logs --tail=20 backend-api

echo ""
echo "=== 完成 ==="
echo "查看实时日志: docker compose -f docker-compose.backend.yml logs -f backend-api"
echo "访问 API 文档: http://192.168.13.6:6080/docs"
