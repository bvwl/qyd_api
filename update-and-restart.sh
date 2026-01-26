#!/bin/bash

# ==========================================
# 更新代码并重启服务脚本
# ==========================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "更新代码并重启服务"
echo "=========================================="

# 1. 拉取最新代码
echo ""
echo "[1/4] 拉取最新代码..."
git pull

# 2. 加载环境变量
echo ""
echo "[2/4] 加载环境变量..."
export $(grep -v '^#' .env.high_concurrency | xargs)

# 3. 重启后端容器
echo ""
echo "[3/4] 重启后端容器..."
docker compose restart backend-api

# 4. 等待服务启动
echo ""
echo "[4/4] 等待服务启动..."
sleep 10

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
