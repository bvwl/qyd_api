#!/bin/bash

# ==========================================
# 前端容器诊断脚本
# ==========================================

echo "=========================================="
echo "前端容器诊断"
echo "=========================================="

# 1. 检查前端容器状态
echo ""
echo "[1] 前端容器状态"
echo "----------------------------------------"
docker compose ps frontend

# 2. 检查前端容器日志
echo ""
echo "[2] 前端容器日志（最近 30 行）"
echo "----------------------------------------"
docker compose logs frontend --tail=30

# 3. 进入前端容器检查
echo ""
echo "[3] 前端容器内部检查"
echo "----------------------------------------"
echo "检查 Nginx 进程："
docker compose exec frontend ps aux | grep nginx || echo "  ✗ 无法检查进程"

echo ""
echo "检查静态文件："
docker compose exec frontend ls -la /usr/share/nginx/html | head -10 || echo "  ✗ 无法检查文件"

echo ""
echo "检查 Nginx 配置："
docker compose exec frontend nginx -t 2>&1 || echo "  ✗ Nginx 配置错误"

# 4. 测试前端容器内部访问
echo ""
echo "[4] 测试前端容器内部访问"
echo "----------------------------------------"
docker compose exec frontend wget -q -O- http://localhost/ | head -c 200 || echo "  ✗ 无法访问"

# 5. 检查 Nginx LB 日志
echo ""
echo "[5] Nginx LB 日志（最近 20 行）"
echo "----------------------------------------"
docker compose logs nginx-lb --tail=20

# 6. 测试 Nginx LB 到前端的连接
echo ""
echo "[6] 测试 Nginx LB 到前端的连接"
echo "----------------------------------------"
docker compose exec nginx-lb wget -q -O- http://frontend/ | head -c 200 || echo "  ✗ 无法连接到前端"

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
