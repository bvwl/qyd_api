#!/bin/bash

# ==========================================
# 生产环境快速修复脚本
# ==========================================

set -e

echo "=========================================="
echo "QYD 生产环境快速修复"
echo "=========================================="

# 1. 检查当前状态
echo ""
echo "[1/7] 检查当前服务状态..."
docker compose ps || echo "  ⚠️  Docker Compose 服务未运行"

# 2. 检查代码版本
echo ""
echo "[2/7] 检查代码版本..."
git log --oneline -3

# 3. 拉取最新代码
echo ""
echo "[3/7] 拉取最新代码..."
git pull

# 4. 加载环境变量
echo ""
echo "[4/7] 加载环境变量..."
if [ -f .env.high_concurrency ]; then
    export $(grep -v '^#' .env.high_concurrency | xargs)
    echo "  ✓ 已加载 .env.high_concurrency"
else
    echo "  ⚠️  未找到 .env.high_concurrency，使用默认配置"
fi

# 5. 停止并删除旧容器
echo ""
echo "[5/7] 停止并删除旧容器..."
docker compose down

# 6. 重新构建并启动所有服务
echo ""
echo "[6/7] 重新构建并启动所有服务..."
docker compose build
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 7. 等待服务启动
echo ""
echo "[7/7] 等待服务启动..."
sleep 20

# 检查服务状态
echo ""
echo "=========================================="
echo "服务状态"
echo "=========================================="
docker compose ps

# 检查端口
echo ""
echo "=========================================="
echo "端口检查"
echo "=========================================="
echo "80 端口（前端）："
netstat -tlnp | grep :80 || echo "  ✗ 未监听"

echo ""
echo "6080 端口（后端 API）："
netstat -tlnp | grep :6080 || echo "  ✗ 未监听"

echo ""
echo "6379 端口（Redis）："
netstat -tlnp | grep :6379 || echo "  ✗ 未监听"

# 测试接口
echo ""
echo "=========================================="
echo "接口测试"
echo "=========================================="
echo "测试前端："
curl -I http://192.168.13.6/ 2>&1 | head -1

echo ""
echo "测试后端 API 文档："
curl -I http://192.168.13.6:6080/docs 2>&1 | head -1

echo ""
echo "测试后端 API（需要登录）："
curl -s http://192.168.13.6:6080/v1/user/role/tree 2>&1 | head -c 100

echo ""
echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  前端: http://192.168.13.6/"
echo "  API文档: http://192.168.13.6:6080/docs"
echo ""
echo "如果还有问题，请运行："
echo "  bash diagnose_services.sh"
