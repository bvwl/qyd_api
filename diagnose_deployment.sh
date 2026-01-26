#!/bin/bash

# ==========================================
# 诊断部署问题
# ==========================================

echo "=========================================="
echo "QYD 部署诊断"
echo "=========================================="
echo ""

cd /opt/zy/qyd_api

# 1. 检查容器状态
echo "[1] 容器状态"
echo "=========================================="
docker compose ps
echo ""

# 2. 检查容器日志（最近50行）
echo "[2] 容器日志（最近50行）"
echo "=========================================="

echo ""
echo "--- Redis 日志 ---"
docker compose logs --tail=20 redis
echo ""

echo "--- 后端 API 日志 ---"
docker compose logs --tail=20 backend-api
echo ""

echo "--- 前端日志 ---"
docker compose logs --tail=20 frontend
echo ""

echo "--- Nginx LB 日志 ---"
docker compose logs --tail=20 nginx-lb
echo ""

# 3. 检查网络连接
echo "[3] 网络连接"
echo "=========================================="

echo "检查容器网络..."
docker network ls | grep qyd
echo ""

echo "检查容器 IP..."
docker compose ps -q | xargs -I {} docker inspect {} --format='{{.Name}}: {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
echo ""

# 4. 检查端口监听
echo "[4] 端口监听"
echo "=========================================="

echo "主机端口监听："
netstat -tlnp | grep -E ":(80|6080|6379)" || echo "未找到监听端口"
echo ""

echo "容器端口映射："
docker compose ps --format "table {{.Name}}\t{{.Ports}}"
echo ""

# 5. 测试连接
echo "[5] 连接测试"
echo "=========================================="

echo "测试 Redis..."
if docker compose exec redis redis-cli PING 2>/dev/null | grep -q "PONG"; then
    echo "✓ Redis 连接正常"
else
    echo "✗ Redis 连接失败"
fi
echo ""

echo "测试后端 API（从容器内）..."
if docker compose exec backend-api curl -s http://localhost:6080/docs > /dev/null 2>&1; then
    echo "✓ 后端 API 容器内访问正常"
else
    echo "✗ 后端 API 容器内访问失败"
fi
echo ""

echo "测试后端 API（从主机）..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://192.168.13.6:6080/docs 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ 后端 API 主机访问正常 (HTTP $HTTP_CODE)"
else
    echo "✗ 后端 API 主机访问失败 (HTTP $HTTP_CODE)"
fi
echo ""

echo "测试前端（从主机）..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://192.168.13.6/ 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ 前端主机访问正常 (HTTP $HTTP_CODE)"
else
    echo "✗ 前端主机访问失败 (HTTP $HTTP_CODE)"
fi
echo ""

# 6. 检查 Nginx 配置
echo "[6] Nginx 配置"
echo "=========================================="

echo "测试 Nginx 配置..."
if docker compose exec nginx-lb nginx -t 2>&1 | grep -q "successful"; then
    echo "✓ Nginx 配置正确"
else
    echo "✗ Nginx 配置错误"
    docker compose exec nginx-lb nginx -t
fi
echo ""

# 7. 资源使用
echo "[7] 资源使用"
echo "=========================================="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""

# 8. 建议
echo "[8] 诊断建议"
echo "=========================================="

# 检查是否有容器退出
EXITED=$(docker compose ps -a | grep -c "Exited" || echo "0")
if [ "$EXITED" -gt 0 ]; then
    echo "⚠️  发现 $EXITED 个退出的容器"
    echo "   查看退出原因: docker compose ps -a"
    echo "   查看日志: docker compose logs <容器名>"
fi

# 检查是否有容器重启
RESTARTING=$(docker compose ps | grep -c "Restarting" || echo "0")
if [ "$RESTARTING" -gt 0 ]; then
    echo "⚠️  发现 $RESTARTING 个正在重启的容器"
    echo "   可能是健康检查失败或启动错误"
fi

# 检查是否有健康检查失败
UNHEALTHY=$(docker compose ps | grep -c "unhealthy" || echo "0")
if [ "$UNHEALTHY" -gt 0 ]; then
    echo "⚠️  发现 $UNHEALTHY 个不健康的容器"
    echo "   查看详情: docker compose ps"
fi

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
echo ""

echo "常用修复命令："
echo "  重启所有服务: docker compose restart"
echo "  重启单个服务: docker compose restart <服务名>"
echo "  查看实时日志: docker compose logs -f"
echo "  重新构建: docker compose build && docker compose up -d"
echo ""
