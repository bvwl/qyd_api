#!/bin/bash

# 修复前端端口冲突问题

echo "=========================================="
echo "修复前端端口冲突"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${YELLOW}检查 80 端口占用情况...${NC}"
if lsof -i :80 > /dev/null 2>&1; then
    echo -e "${RED}✗ 端口 80 已被占用${NC}"
    echo ""
    lsof -i :80
    echo ""
    
    echo -e "${YELLOW}请选择解决方案：${NC}"
    echo "  1. 停止占用 80 端口的服务（推荐）"
    echo "  2. 修改前端端口为 8080"
    echo ""
    read -p "请输入选项 (1/2): " choice
    
    if [ "$choice" = "1" ]; then
        echo -e "\n${YELLOW}停止占用 80 端口的服务...${NC}"
        
        # 检查是否是 Nginx
        if systemctl is-active --quiet nginx; then
            echo -e "${YELLOW}停止 Nginx...${NC}"
            sudo systemctl stop nginx
            sudo systemctl disable nginx
            echo -e "${GREEN}✓ Nginx 已停止${NC}"
        fi
        
        # 检查是否是 Docker 容器
        containers=$(docker ps --filter "publish=80" --format "{{.Names}}")
        if [ -n "$containers" ]; then
            echo -e "${YELLOW}停止 Docker 容器...${NC}"
            echo "$containers" | while read container; do
                docker stop "$container"
                echo -e "${GREEN}✓ 已停止容器: $container${NC}"
            done
        fi
        
        echo -e "\n${GREEN}✓ 端口 80 已释放${NC}"
        echo -e "\n${YELLOW}现在可以重新部署前端：${NC}"
        echo "bash deploy-frontend.sh"
        
    elif [ "$choice" = "2" ]; then
        echo -e "\n${YELLOW}前端端口已修改为 8080${NC}"
        echo -e "${YELLOW}请重新部署前端：${NC}"
        echo "bash deploy-frontend.sh"
        echo ""
        echo -e "${YELLOW}访问地址将变为：${NC}"
        echo "http://$(hostname -I | awk '{print $1}'):8080"
    else
        echo -e "${RED}无效的选项${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 端口 80 未被占用${NC}"
    echo "可以直接部署前端"
fi

echo ""
echo "=========================================="
