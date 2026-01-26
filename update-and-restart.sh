#!/bin/bash

# ==========================================
# 更新代码并重新构建服务脚本
# ==========================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "更新代码并重新构建服务"
echo "=========================================="

# 1. 拉取最新代码
echo ""
echo "[1/6] 拉取最新代码..."
git pull

# 2. 加载环境变量
echo ""
echo "[2/6] 加载环境变量..."
export $(grep -v '^#' .env.high_concurrency | xargs)

# 3. 停止后端容器
echo ""
echo "[3/6] 停止后端容器..."
docker compose stop backend-api queue-worker

# 4. 删除后端容器
echo ""
echo "[4/6] 删除后端容器..."
docker compose rm -f backend-api queue-worker

# 5. 重新构建后端镜像
echo ""
echo "[5/6] 重新构建后端镜像..."
docker compose build backend-api queue-worker

# 6. 启动后端容器（5个API实例 + 5个队列实例）
echo ""
echo "[6/6] 启动后端容器..."
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 等待服务启动
echo ""
echo "等待服务启动..."
sleep 15

# 检查服务状态
echo ""
echo "=========================================="
echo "服务状态检查"
echo "=========================================="
docker compose ps backend-api

# 测试接口
echo ""
echo "=========================================="
echo "测试接口"
echo "=========================================="
echo "测试 /docs 接口："
curl -I http://192.168.13.6:6080/docs 2>/dev/null | head -1

echo ""
echo "测试 /v1/user/role/tree 接口："
curl -s http://192.168.13.6:6080/v1/user/role/tree 2>/dev/null | head -c 100
echo "..."

echo ""
echo ""
echo "✅ 更新完成！"
echo ""
echo "访问地址："
echo "  前端: http://192.168.13.6/"
echo "  API文档: http://192.168.13.6:6080/docs"
