#!/bin/bash

# ==========================================
# QYD 项目 Docker 快速部署脚本
# 使用国内镜像加速
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo -e "${BLUE}QYD 项目 Docker 快速部署${NC}"
echo "=========================================="
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ==========================================
# 1. 检查 Docker
# ==========================================
echo -e "${YELLOW}[1/6] 检查 Docker 环境...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未找到 Docker${NC}"
    echo "请先安装 Docker"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}错误: Docker 未运行或当前用户无权限${NC}"
    echo "解决方法："
    echo "  1. 启动 Docker: sudo systemctl start docker"
    echo "  2. 添加用户到 docker 组: sudo usermod -aG docker \$USER"
    echo "  3. 重新登录"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✓ Docker: $DOCKER_VERSION${NC}"

if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    echo -e "${GREEN}✓ Docker Compose: $COMPOSE_VERSION${NC}"
else
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    exit 1
fi
echo ""

# ==========================================
# 2. 配置 Docker 国内镜像
# ==========================================
echo -e "${YELLOW}[2/6] 配置 Docker 国内镜像加速...${NC}"

DOCKER_DAEMON_FILE="/etc/docker/daemon.json"

if [ -f "$DOCKER_DAEMON_FILE" ]; then
    echo "Docker 配置文件已存在"
    cat "$DOCKER_DAEMON_FILE"
else
    echo "创建 Docker 镜像加速配置..."
    
    # 需要 root 权限
    if [ "$EUID" -ne 0 ]; then
        echo -e "${YELLOW}需要 root 权限配置 Docker 镜像${NC}"
        sudo tee "$DOCKER_DAEMON_FILE" > /dev/null << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
        
        echo "重启 Docker 服务..."
        sudo systemctl daemon-reload
        sudo systemctl restart docker
        
        echo -e "${GREEN}✓ Docker 镜像加速已配置${NC}"
    else
        tee "$DOCKER_DAEMON_FILE" > /dev/null << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
        
        echo "重启 Docker 服务..."
        systemctl daemon-reload
        systemctl restart docker
        
        echo -e "${GREEN}✓ Docker 镜像加速已配置${NC}"
    fi
fi
echo ""

# ==========================================
# 3. 配置环境变量
# ==========================================
echo -e "${YELLOW}[3/6] 配置环境变量...${NC}"

if [ ! -f ".env" ]; then
    echo "从 .env.docker 复制配置..."
    cp .env.docker .env
    
    echo -e "${YELLOW}请编辑 .env 文件配置以下参数：${NC}"
    echo "  - DB_HOST（MySQL 主库地址）"
    echo "  - DB_PASSWORD（MySQL 密码）"
    echo "  - REDIS_PASSWORD（Redis 密码）"
    echo "  - JWT_SECRET_KEY（JWT 密钥，至少32字符）"
    echo ""
    
    read -p "按回车键继续编辑 .env 文件..." 
    ${EDITOR:-vim} .env
else
    echo -e "${GREEN}✓ .env 文件已存在${NC}"
fi
echo ""

# ==========================================
# 4. 清理旧容器和镜像（可选）
# ==========================================
echo -e "${YELLOW}[4/6] 清理旧容器...${NC}"

read -p "是否清理旧容器和镜像？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "停止并删除旧容器..."
    docker compose down -v 2>/dev/null || true
    
    echo "删除旧镜像..."
    docker images | grep qyd_api | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
    
    echo -e "${GREEN}✓ 清理完成${NC}"
else
    echo "跳过清理"
fi
echo ""

# ==========================================
# 5. 构建镜像
# ==========================================
echo -e "${YELLOW}[5/6] 构建 Docker 镜像...${NC}"
echo "使用国内镜像源加速构建..."
echo ""

# 显示构建进度
docker compose build --progress=plain

echo ""
echo -e "${GREEN}✓ 镜像构建完成${NC}"
echo ""

# ==========================================
# 6. 启动服务
# ==========================================
echo -e "${YELLOW}[6/6] 启动服务...${NC}"

# 首次部署需要初始化数据库
if [ ! -f ".initialized" ]; then
    echo "首次部署，初始化数据库..."
    
    # 先启动 Redis
    docker compose up -d redis
    sleep 5
    
    # 初始化数据库
    docker compose run --rm backend-api python deploy_init.py
    
    # 标记已初始化
    touch .initialized
    
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
fi

# 启动所有服务
echo "启动所有服务..."
docker compose up -d

echo ""
echo -e "${GREEN}✓ 服务启动完成${NC}"
echo ""

# ==========================================
# 7. 验证部署
# ==========================================
echo -e "${YELLOW}验证部署...${NC}"
echo ""

# 等待服务启动
echo "等待服务启动（30秒）..."
sleep 30

# 检查服务状态
echo "服务状态："
docker compose ps

echo ""
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "访问地址："
echo "  前端: http://your-server-ip"
echo "  后端: http://your-server-ip:6080"
echo "  API 文档: http://your-server-ip:6080/docs"
echo ""
echo "默认管理员账号："
echo "  邮箱: zhiyu"
echo "  密码: 2201101122@qq.com"
echo ""
echo "常用命令："
echo "  查看日志: docker compose logs -f"
echo "  查看状态: docker compose ps"
echo "  重启服务: docker compose restart"
echo "  停止服务: docker compose stop"
echo "  删除服务: docker compose down"
echo ""
echo "如果服务未正常启动，请查看日志："
echo "  docker compose logs backend-api"
echo "  docker compose logs frontend"
echo "  docker compose logs redis"
echo ""
