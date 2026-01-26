#!/bin/bash

# ==========================================
# 重启 Nginx 并测试
# ==========================================

set -e

echo "=========================================="
echo "重启 Nginx"
echo "=========================================="

# 1. 检查配置文件
echo ""
echo "[1/3] 检查 Nginx 配置..."
docker compose exec nginx-lb nginx -t

# 2. 重启 Nginx
echo ""
echo "[2/3] 重启 Nginx 容器..."
docker compose restart nginx-lb

# 等待启动
echo "  等待 Nginx 启动..."
sleep 5

# 3. 测试接口
echo ""
echo "[3/3] 测试接口..."
echo ""
echo "测试前端（80端口）："
curl -I http://192.168.13.6/ 2>&1 | head -1

echo ""
echo "测试后端 API 文档（6080端口）："
curl -I http://192.168.13.6:6080/docs 2>&1 | head -1

echo ""
echo "测试后端 API 接口（需要认证）："
curl -s http://192.168.13.6:6080/v1/user/role/tree 2>&1 | head -c 100

echo ""
echo ""
echo "=========================================="
echo "✅ 完成！"
echo "=========================================="
echo ""
echo "如果还有问题，查看 Nginx 日志："
echo "  docker compose logs -f nginx-lb"
