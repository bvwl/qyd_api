#!/bin/bash

# 检查 80 端口占用情况

echo "=========================================="
echo "检查 80 端口占用情况"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${YELLOW}1. 检查 80 端口占用...${NC}"
if lsof -i :80 > /dev/null 2>&1; then
    echo -e "${RED}✗ 端口 80 已被占用${NC}"
    echo ""
    echo "占用进程信息："
    lsof -i :80
    
    echo -e "\n${YELLOW}2. 检查是否是 Nginx...${NC}"
    if systemctl is-active --quiet nginx; then
        echo -e "${YELLOW}! Nginx 正在运行${NC}"
        echo ""
        echo "解决方案："
        echo "  1. 停止 Nginx: sudo systemctl stop nginx"
        echo "  2. 或修改前端端口为 8080"
    fi
    
    echo -e "\n${YELLOW}3. 检查是否是 Docker 容器...${NC}"
    docker ps --filter "publish=80" --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}"
    
else
    echo -e "${GREEN}✓ 端口 80 未被占用${NC}"
fi

echo ""
echo "=========================================="
