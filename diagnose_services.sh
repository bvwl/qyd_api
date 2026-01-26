#!/bin/bash

# ==========================================
# 服务诊断脚本
# ==========================================

echo "=========================================="
echo "QYD 服务诊断"
echo "=========================================="

# 1. 检查 Docker 容器状态
echo ""
echo "[1] Docker 容器状态"
echo "----------------------------------------"
docker compose ps

# 2. 检查端口监听
echo ""
echo "[2] 端口监听状态"
echo "----------------------------------------"
echo "检查 80 端口（前端）："
netstat -tlnp | grep :80 || echo "  ✗ 80 端口未监听"

echo ""
echo "检查 6080 端口（后端 API）："
netstat -tlnp | grep :6080 || echo "  ✗ 6080 端口未监听"

echo ""
echo "检查 6379 端口（Redis）："
netstat -tlnp | grep :6379 || echo "  ✗ 6379 端口未监听"

# 3. 检查 Nginx 配置
echo ""
echo "[3] Nginx 配置检查"
echo "----------------------------------------"
docker compose exec nginx-lb nginx -t 2>&1 || echo "  ✗ Nginx 配置检查失败"

# 4. 测试后端 API（从宿主机）
echo ""
echo "[4] 后端 API 测试（从宿主机）"
echo "----------------------------------------"
echo "测试 /docs 接口："
curl -I http://192.168.13.6:6080/docs 2>&1 | head -3

echo ""
echo "测试 /v1/user/role/tree 接口（需要认证）："
curl -s http://192.168.13.6:6080/v1/user/role/tree 2>&1 | head -c 200

# 5. 测试后端 API（从容器内部）
echo ""
echo ""
echo "[5] 后端 API 测试（从 Nginx 容器内部）"
echo "----------------------------------------"
docker compose exec nginx-lb wget -q -O- http://backend_api/docs 2>&1 | head -c 200 || echo "  ✗ 无法从 Nginx 访问后端"

# 6. 检查后端容器日志
echo ""
echo ""
echo "[6] 后端容器日志（最近 20 行）"
echo "----------------------------------------"
docker compose logs --tail=20 backend-api

# 7. 检查 Nginx 日志
echo ""
echo "[7] Nginx 错误日志（最近 20 行）"
echo "----------------------------------------"
docker compose logs --tail=20 nginx-lb

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
