#!/bin/bash

echo "=== 后端服务诊断工具 ==="
echo ""

# 检查是否在正确的目录
if [ ! -f "docker-compose.backend.yml" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

echo "1. 检查 Docker 服务状态..."
echo "================================"
docker compose -f docker-compose.backend.yml ps
echo ""

echo "2. 检查容器是否存在..."
echo "================================"
echo "Backend API:"
docker ps -a --filter "name=qyd-backend-api" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Queue Worker:"
docker ps -a --filter "name=qyd-queue-worker" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "3. 检查镜像..."
echo "================================"
docker images | grep -E "qyd_api|REPOSITORY"
echo ""

echo "4. 检查 Backend API 日志（最近50行）..."
echo "================================"
docker compose -f docker-compose.backend.yml logs --tail=50 backend-api
echo ""

echo "5. 检查 Queue Worker 日志（最近50行）..."
echo "================================"
docker compose -f docker-compose.backend.yml logs --tail=50 queue-worker
echo ""

echo "6. 检查 Redis 连接..."
echo "================================"
REDIS_HOST=$(grep REDIS_HOST .env.backend 2>/dev/null | cut -d'=' -f2 || echo "192.168.1.20")
REDIS_PORT=$(grep REDIS_PORT .env.backend 2>/dev/null | cut -d'=' -f2 || echo "6379")
REDIS_PASSWORD=$(grep REDIS_PASSWORD .env.backend 2>/dev/null | cut -d'=' -f2 || echo "redis_password")

echo "Redis 配置: ${REDIS_HOST}:${REDIS_PORT}"
if command -v redis-cli &> /dev/null; then
    echo "测试 Redis 连接..."
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" PING 2>&1
else
    echo "⚠️  redis-cli 未安装，跳过 Redis 连接测试"
fi
echo ""

echo "7. 检查数据库连接..."
echo "================================"
DB_HOST=$(grep DB_HOST .env.backend 2>/dev/null | cut -d'=' -f2 || echo "192.168.1.30")
DB_PORT=$(grep DB_PORT .env.backend 2>/dev/null | cut -d'=' -f2 || echo "3306")
echo "数据库配置: ${DB_HOST}:${DB_PORT}"
if command -v nc &> /dev/null; then
    echo "测试数据库端口..."
    nc -zv "$DB_HOST" "$DB_PORT" 2>&1 | head -1
else
    echo "⚠️  nc 未安装，跳过数据库连接测试"
fi
echo ""

echo "8. 检查磁盘空间..."
echo "================================"
df -h | grep -E "Filesystem|/$"
echo ""

echo "9. 检查日志目录..."
echo "================================"
if [ -d "logs" ]; then
    echo "日志目录大小:"
    du -sh logs
    echo ""
    echo "最近的日志文件:"
    ls -lht logs/*.log 2>/dev/null | head -5
else
    echo "⚠️  logs 目录不存在"
fi
echo ""

echo "=== 诊断完成 ==="
echo ""
echo "常用命令:"
echo "  查看实时日志:     docker compose -f docker-compose.backend.yml logs -f"
echo "  重启服务:         docker compose -f docker-compose.backend.yml restart"
echo "  重启 worker:      bash restart-queue-worker.sh"
echo "  强制重建:         bash force-rebuild-backend.sh"
