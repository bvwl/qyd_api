#!/bin/bash

# 更新部署脚本
# 用于在服务器上拉取最新的部署脚本

echo "=========================================="
echo "更新部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\n${YELLOW}拉取最新代码...${NC}"
git pull origin main

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 代码更新成功${NC}"
    
    # 赋予执行权限
    echo -e "\n${YELLOW}设置执行权限...${NC}"
    chmod +x deploy-backend.sh
    chmod +x deploy-frontend.sh
    chmod +x deploy-backend-native.sh
    chmod +x deploy-frontend-native.sh
    
    echo -e "${GREEN}✓ 权限设置完成${NC}"
    
    echo -e "\n${GREEN}=========================================="
    echo "更新完成！"
    echo "==========================================${NC}"
    echo ""
    echo "现在可以运行部署脚本："
    echo "  - 后端 Docker 部署: bash deploy-backend.sh"
    echo "  - 前端 Docker 部署: bash deploy-frontend.sh"
    echo "  - 后端原生部署: bash deploy-backend-native.sh"
    echo "  - 前端原生部署: bash deploy-frontend-native.sh"
    echo ""
else
    echo -e "${RED}✗ 代码更新失败${NC}"
    exit 1
fi
