#!/bin/bash

# ==========================================
# 前端服务器部署脚本
# 服务器: 192.168.1.10
# 服务: Frontend (Nginx)
# ==========================================

set -e

echo "=========================================="
echo "QYD 前端服务器部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
echo -e "\n${YELLOW}[1/5] 检查 Docker 环境...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/engine/install/"
    exit 1
fi

# 检查 Docker Compose 版本并设置命令
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    echo -e "${GREEN}✓ 使用 docker-compose 命令${NC}"
elif docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
    echo -e "${GREEN}✓ 使用 docker compose 命令${NC}"
else
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker 环境检查通过${NC}"

# 配置环境变量
echo -e "\n${YELLOW}[2/5] 配置环境变量...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.frontend ]; then
        cp .env.frontend .env
        echo -e "${GREEN}✓ 已复制 .env.frontend 到 .env${NC}"
    else
        echo -e "${RED}错误: .env.frontend 文件不存在${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}! .env 文件已存在，跳过复制${NC}"
fi

# 提示用户检查配置
echo -e "${YELLOW}请检查 .env 文件中的配置：${NC}"
echo "  - VITE_API_BASE_URL: 后端服务器地址"
echo ""
read -p "是否继续部署？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}部署已取消${NC}"
    exit 0
fi

# 构建镜像
echo -e "\n${YELLOW}[3/5] 构建 Docker 镜像...${NC}"
$DOCKER_COMPOSE -f docker-compose.frontend.yml build

echo -e "${GREEN}✓ 镜像构建完成${NC}"

# 启动服务
echo -e "\n${YELLOW}[4/5] 启动服务...${NC}"
$DOCKER_COMPOSE -f docker-compose.frontend.yml up -d

echo -e "${GREEN}✓ 服务启动完成${NC}"

# 检查服务状态
echo -e "\n${YELLOW}[5/5] 检查服务状态...${NC}"
sleep 3
$DOCKER_COMPOSE -f docker-compose.frontend.yml ps

echo -e "\n${GREEN}=========================================="
echo "前端部署完成！"
echo "==========================================${NC}"
echo ""
echo "访问地址："
echo "  - 前端应用: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "常用命令："
echo "  - 查看状态: $DOCKER_COMPOSE -f docker-compose.frontend.yml ps"
echo "  - 查看日志: $DOCKER_COMPOSE -f docker-compose.frontend.yml logs -f"
echo "  - 重启服务: $DOCKER_COMPOSE -f docker-compose.frontend.yml restart"
echo "  - 停止服务: $DOCKER_COMPOSE -f docker-compose.frontend.yml stop"
echo ""
