#!/bin/bash

# ==========================================
# 启动所有服务（高并发模式）
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "=========================================="
echo -e "${BLUE}启动所有服务（高并发模式）${NC}"
echo "=========================================="
echo ""

# 配置参数
BACKEND_INSTANCES=5
QUEUE_INSTANCES=5

echo -e "${CYAN}配置：${NC}"
echo "  后端容器: $BACKEND_INSTANCES 个"
echo "  队列容器: $QUEUE_INSTANCES 个"
echo "  前端容器: 1 个"
echo "  Redis 容器: 1 个"
echo ""

# 停止所有服务
echo -e "${YELLOW}停止旧服务...${NC}"
docker compose down
echo ""

# 启动所有服务
echo -e "${YELLOW}启动所有服务...${NC}"
docker compose up -d \
    --scale backend-api=$BACKEND_INSTANCES \
    --scale queue-worker=$QUEUE_INSTANCES

echo ""
echo -e "${GREEN}✓ 服务启动命令已执行${NC}"
echo ""

# 等待服务启动
echo "等待服务启动（30秒）..."
sleep 30

# 检查服务状态
echo ""
echo -e "${CYAN}服务状态：${NC}"
docker compose ps

echo ""
echo -e "${CYAN}资源使用：${NC}"
docker stats --no-stream

echo ""
echo "=========================================="
echo -e "${GREEN}启动完成！${NC}"
echo "=========================================="
echo ""

echo -e "${CYAN}访问地址：${NC}"
echo "  前端: http://192.168.13.6"
echo "  后端: http://192.168.13.6:6080"
echo "  API 文档: http://192.168.13.6:6080/docs"
echo ""

echo -e "${CYAN}管理员账号：${NC}"
echo "  邮箱: zhiyu"
echo "  密码: 2201101122@qq.com"
echo ""

echo -e "${CYAN}检查命令：${NC}"
echo "  查看日志: docker compose logs -f --tail=100"
echo "  查看状态: docker compose ps"
echo "  重启服务: docker compose restart"
echo ""

# 健康检查
echo -e "${YELLOW}执行健康检查...${NC}"
echo ""

# 检查后端
if curl -s http://192.168.13.6:6080/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端 API 正常${NC}"
else
    echo -e "${RED}✗ 后端 API 异常${NC}"
    echo "  查看日志: docker compose logs backend-api --tail=50"
fi

# 检查前端
if curl -s http://192.168.13.6/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端服务正常${NC}"
else
    echo -e "${RED}✗ 前端服务异常${NC}"
    echo "  查看日志: docker compose logs frontend --tail=50"
fi

# 检查 Redis
if docker compose exec redis redis-cli -a redis_fNmAxZ PING 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}✓ Redis 服务正常${NC}"
else
    echo -e "${RED}✗ Redis 服务异常${NC}"
    echo "  查看日志: docker compose logs redis --tail=50"
fi

echo ""
echo -e "${GREEN}所有服务已启动！${NC}"
echo ""
