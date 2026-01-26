#!/bin/bash

# ==========================================
# 重新构建并启动后端服务
# ==========================================

set -e

echo "=========================================="
echo "重新构建并启动后端服务"
echo "=========================================="

# 加载环境变量
echo ""
echo "[1/5] 加载环境变量..."
export $(grep -v '^#' .env.high_concurrency | xargs)

# 停止后端容器
echo ""
echo "[2/5] 停止后端容器..."
docker compose stop backend-api

# 删除后端容器
echo ""
echo "[3/5] 删除后端容器..."
docker compose rm -f backend-api

# 重新构建后端镜像
echo ""
echo "[4/5] 重新构建后端镜像..."
docker compose build backend-api

# 启动后端容器（5个实例）
echo ""
echo "[5/5] 启动后端容器..."
docker compose up -d --scale backend-api=5

# 等待服务启动
echo ""
echo "等待服务启动..."
sleep 15

# 检查服务状态
echo ""
echo "=========================================="
echo "服务状态"
echo "=========================================="
docker compose ps backend-api

# 测试接口
echo ""
echo "=========================================="
echo "测试接口"
echo "=========================================="
echo "测试 /v1/user/role/tree 接口："
curl -s -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk0OTkyMzQsImlhdCI6MTc2OTQxMjgzNCwianRpIjoiYzY0MjYzZGQtNDVmYy00ZmVlLWI5NDEtMmRiMzgzMmZlYzA1IiwiaWQiOiJlMzRkZjY1Zi04ZjVkLTRiMTQtYWNlOS1jYmQ4M2NkNDA1ZjAiLCJlbWFpbCI6InpoaXl1Iiwicm9sZXMiOlsiQURNSU4iXX0.jtycmJCOLdrQymjaGKY80gbQZ2tupo99tVPYskuvQPY" http://192.168.13.6:6080/v1/user/role/tree | head -c 200
echo "..."

echo ""
echo ""
echo "✅ 重建完成！"
