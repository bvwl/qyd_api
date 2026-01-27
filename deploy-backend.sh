#!/bin/bash

# ==========================================
# 后端服务器部署脚本
# 服务器: 192.168.1.20
# 服务: Backend API + Queue Worker + Redis
# ==========================================

set -e

echo "=========================================="
echo "QYD 后端服务器部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker
echo -e "\n${YELLOW}[1/6] 检查 Docker 环境...${NC}"
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
echo -e "\n${YELLOW}[2/6] 配置环境变量...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.backend ]; then
        cp .env.backend .env
        echo -e "${GREEN}✓ 已复制 .env.backend 到 .env${NC}"
    else
        echo -e "${RED}错误: .env.backend 文件不存在${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}! .env 文件已存在，跳过复制${NC}"
fi

# 提示用户检查配置
echo -e "${YELLOW}请编辑 .env 文件配置以下参数：${NC}"
echo "  - DB_HOST: MySQL 服务器地址"
echo "  - DB_PASSWORD: MySQL 密码"
echo "  - REDIS_HOST: Redis 服务器地址"
echo "  - REDIS_PASSWORD: Redis 密码"
echo "  - JWT_SECRET_KEY: JWT 密钥"
echo "  - CORS_ORIGINS: 前端服务器地址"
echo ""
read -p "是否继续部署？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}部署已取消${NC}"
    exit 0
fi

# 构建镜像
echo -e "\n${YELLOW}[3/6] 构建 Docker 镜像...${NC}"
read -p "是否强制重新构建（不使用缓存）？代码更新后建议选 y (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "正在强制重新构建（不使用缓存）..."
    $DOCKER_COMPOSE -f docker-compose.backend.yml build --no-cache
else
    echo "正在构建（使用缓存）..."
    $DOCKER_COMPOSE -f docker-compose.backend.yml build
fi

echo -e "${GREEN}✓ 镜像构建完成${NC}"

# 初始化数据库（仅首次部署）
echo -e "\n${YELLOW}[4/6] 初始化数据库...${NC}"
read -p "是否需要初始化数据库？(首次部署选 y) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $DOCKER_COMPOSE -f docker-compose.backend.yml run --rm backend-api python deploy_init.py
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
else
    echo -e "${YELLOW}! 跳过数据库初始化${NC}"
fi

# 启动服务
echo -e "\n${YELLOW}[5/6] 启动服务...${NC}"
$DOCKER_COMPOSE -f docker-compose.backend.yml up -d

echo -e "${GREEN}✓ 服务启动完成${NC}"

# 检查服务状态
echo -e "\n${YELLOW}[6/6] 检查服务状态...${NC}"
sleep 5
$DOCKER_COMPOSE -f docker-compose.backend.yml ps

# 显示日志
echo -e "\n${YELLOW}查看服务日志（按 Ctrl+C 退出）：${NC}"
echo "docker-compose -f docker-compose.backend.yml logs -f"

echo -e "\n${GREEN}=========================================="
echo "后端部署完成！"
echo "==========================================${NC}"
echo ""
echo "服务地址："
echo "  - API 文档: http://$(hostname -I | awk '{print $1}'):6080/docs"
echo "  - API 地址: http://$(hostname -I | awk '{print $1}'):6080"
echo ""
echo "常用命令："
echo "  - 查看状态: $DOCKER_COMPOSE -f docker-compose.backend.yml ps"
echo "  - 查看日志: $DOCKER_COMPOSE -f docker-compose.backend.yml logs -f"
echo "  - 重启服务: $DOCKER_COMPOSE -f docker-compose.backend.yml restart"
echo "  - 停止服务: $DOCKER_COMPOSE -f docker-compose.backend.yml stop"
echo ""
