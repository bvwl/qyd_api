#!/bin/bash

# 修复 CORS 配置，添加 8080 端口支持

echo "=========================================="
echo "修复 CORS 配置"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${YELLOW}检查当前 CORS 配置...${NC}"
if [ -f .env ]; then
    current_cors=$(grep "^CORS_ORIGINS=" .env | cut -d'=' -f2)
    echo "当前配置: $current_cors"
    
    # 检查是否已包含 8080 端口
    if echo "$current_cors" | grep -q ":8080"; then
        echo -e "${GREEN}✓ CORS 配置已包含 8080 端口${NC}"
    else
        echo -e "${YELLOW}! CORS 配置缺少 8080 端口${NC}"
        
        # 获取服务器 IP
        server_ip=$(grep "^VITE_API_BASE_URL=" .env | cut -d'/' -f3 | cut -d':' -f1)
        if [ -z "$server_ip" ]; then
            server_ip="192.168.13.6"
        fi
        
        # 添加 8080 端口
        new_cors="${current_cors},http://${server_ip}:8080"
        
        echo -e "\n${YELLOW}更新 CORS 配置...${NC}"
        sed -i "s|^CORS_ORIGINS=.*|CORS_ORIGINS=${new_cors}|" .env
        
        echo -e "${GREEN}✓ CORS 配置已更新${NC}"
        echo "新配置: $new_cors"
        
        # 重启后端服务
        echo -e "\n${YELLOW}重启后端服务以应用配置...${NC}"
        
        # 检查使用的 Docker Compose 命令
        if command -v docker-compose &> /dev/null; then
            DOCKER_COMPOSE="docker-compose"
        else
            DOCKER_COMPOSE="docker compose"
        fi
        
        $DOCKER_COMPOSE -f docker-compose.backend.yml restart backend-api
        
        echo -e "${GREEN}✓ 后端服务已重启${NC}"
        
        echo -e "\n${GREEN}=========================================="
        echo "CORS 配置修复完成！"
        echo "==========================================${NC}"
        echo ""
        echo "现在可以刷新前端页面重试"
    fi
else
    echo -e "${RED}✗ .env 文件不存在${NC}"
    exit 1
fi

echo ""
echo "=========================================="
