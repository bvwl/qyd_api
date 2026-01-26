#!/bin/bash

# ==========================================
# QYD 项目环境安装脚本
# 适用于 Ubuntu Server 24.04
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo -e "${BLUE}QYD 项目环境安装${NC}"
echo "Ubuntu Server 24.04"
echo "=========================================="
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}错误: 请使用 root 用户或 sudo 运行此脚本${NC}"
    echo "使用方法: sudo bash setup_environment.sh"
    exit 1
fi

# 获取实际用户（如果使用 sudo）
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo -e "${YELLOW}当前用户: $ACTUAL_USER${NC}"
echo -e "${YELLOW}用户目录: $ACTUAL_HOME${NC}"
echo ""

# ==========================================
# 1. 更新系统
# ==========================================
echo -e "${BLUE}[1/7] 更新系统包...${NC}"
apt-get update -qq
apt-get upgrade -y -qq
echo -e "${GREEN}✓ 系统更新完成${NC}"
echo ""

# ==========================================
# 2. 安装基础工具
# ==========================================
echo -e "${BLUE}[2/7] 安装基础工具...${NC}"
apt-get install -y -qq \
    curl \
    wget \
    git \
    vim \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

echo -e "${GREEN}✓ 基础工具安装完成${NC}"
echo ""

# ==========================================
# 3. 安装 Python 3.11
# ==========================================
echo -e "${BLUE}[3/7] 安装 Python 3.11...${NC}"

if command -v python3.11 &> /dev/null; then
    PYTHON_VERSION=$(python3.11 --version)
    echo -e "${GREEN}✓ Python 已安装: $PYTHON_VERSION${NC}"
else
    echo "安装 Python 3.11..."
    apt-get install -y -qq \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        python3-pip
    
    # 设置 python3 默认版本
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
    
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python 安装完成: $PYTHON_VERSION${NC}"
fi

# 安装 pip
if ! command -v pip3 &> /dev/null; then
    echo "安装 pip..."
    apt-get install -y -qq python3-pip
fi

PIP_VERSION=$(pip3 --version)
echo -e "${GREEN}✓ pip: $PIP_VERSION${NC}"
echo ""

# ==========================================
# 4. 安装 Node.js 18
# ==========================================
echo -e "${BLUE}[4/7] 安装 Node.js 18...${NC}"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js 已安装: $NODE_VERSION${NC}"
else
    echo "安装 Node.js 18..."
    
    # 添加 NodeSource 仓库
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    
    # 安装 Node.js
    apt-get install -y -qq nodejs
    
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ Node.js 安装完成: $NODE_VERSION${NC}"
    echo -e "${GREEN}✓ npm: $NPM_VERSION${NC}"
fi

# 配置 npm 国内镜像（可选，加速下载）
read -p "是否配置 npm 淘宝镜像？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    npm config set registry https://registry.npmmirror.com
    echo -e "${GREEN}✓ npm 镜像已配置为淘宝镜像${NC}"
fi
echo ""

# ==========================================
# 5. 检查 Docker
# ==========================================
echo -e "${BLUE}[5/7] 检查 Docker...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未找到 Docker${NC}"
    echo "请先安装 Docker"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✓ Docker 已安装: $DOCKER_VERSION${NC}"

# 检查 Docker 是否运行
if ! docker ps &> /dev/null; then
    echo -e "${RED}错误: Docker 未运行或当前用户无权限${NC}"
    echo "解决方法："
    echo "  1. 启动 Docker: sudo systemctl start docker"
    echo "  2. 添加用户到 docker 组: sudo usermod -aG docker $ACTUAL_USER"
    echo "  3. 重新登录以使权限生效"
    exit 1
fi

# 检查 Docker Compose
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    echo -e "${GREEN}✓ Docker Compose: $COMPOSE_VERSION${NC}"
else
    echo -e "${YELLOW}警告: Docker Compose 插件未安装${NC}"
    echo "安装: sudo apt-get install docker-compose-plugin"
fi

echo ""

# ==========================================
# 6. 部署 Redis 容器
# ==========================================
echo -e "${BLUE}[6/7] 部署 Redis 容器...${NC}"

# 检查 Redis 容器是否已运行
if docker ps | grep -q qyd-redis; then
    echo -e "${GREEN}✓ Redis 容器已运行${NC}"
else
    echo "启动 Redis 容器..."
    
    # 设置 Redis 密码
    read -p "请输入 Redis 密码（默认: redis_fNmAxZ）: " REDIS_PASSWORD
    REDIS_PASSWORD=${REDIS_PASSWORD:-redis_fNmAxZ}
    
    # 启动 Redis 容器
    docker run -d \
        --name qyd-redis \
        --restart unless-stopped \
        -p 6379:6379 \
        -v qyd-redis-data:/data \
        redis:7-alpine \
        redis-server \
        --requirepass "$REDIS_PASSWORD" \
        --maxmemory 2gb \
        --maxmemory-policy allkeys-lru \
        --appendonly yes \
        --appendfsync everysec
    
    # 等待 Redis 启动
    sleep 3
    
    # 测试连接
    if docker exec qyd-redis redis-cli -a "$REDIS_PASSWORD" ping | grep -q PONG; then
        echo -e "${GREEN}✓ Redis 容器启动成功${NC}"
        echo -e "${GREEN}✓ Redis 密码: $REDIS_PASSWORD${NC}"
        
        # 保存密码到文件
        echo "REDIS_PASSWORD=$REDIS_PASSWORD" > /tmp/redis_password.txt
        echo -e "${YELLOW}Redis 密码已保存到: /tmp/redis_password.txt${NC}"
    else
        echo -e "${RED}✗ Redis 启动失败${NC}"
        exit 1
    fi
fi
echo ""

# ==========================================
# 7. 安装 Nginx
# ==========================================
echo -e "${BLUE}[7/7] 安装 Nginx...${NC}"

if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1 | awk '{print $3}')
    echo -e "${GREEN}✓ Nginx 已安装: $NGINX_VERSION${NC}"
else
    echo "安装 Nginx..."
    apt-get install -y -qq nginx
    
    # 启动 Nginx
    systemctl start nginx
    systemctl enable nginx
    
    NGINX_VERSION=$(nginx -v 2>&1 | awk '{print $3}')
    echo -e "${GREEN}✓ Nginx 安装完成: $NGINX_VERSION${NC}"
fi
echo ""

# ==========================================
# 环境检查总结
# ==========================================
echo "=========================================="
echo -e "${GREEN}环境安装完成！${NC}"
echo "=========================================="
echo ""
echo "已安装的软件："
echo "  • Python: $(python3 --version | awk '{print $2}')"
echo "  • pip: $(pip3 --version | awk '{print $2}')"
echo "  • Node.js: $(node --version)"
echo "  • npm: $(npm --version)"
echo "  • Docker: $(docker --version | awk '{print $3}' | tr -d ',')"
echo "  • Docker Compose: $(docker compose version | awk '{print $4}')"
echo "  • Redis: 容器运行中 (端口 6379)"
echo "  • Nginx: $(nginx -v 2>&1 | awk '{print $3}')"
echo ""

# ==========================================
# 后续步骤
# ==========================================
echo "后续步骤："
echo ""
echo "1. 重新登录以使 Docker 权限生效："
echo "   exit"
echo "   ssh user@server"
echo ""
echo "2. 运行部署脚本："
echo "   cd /opt/zy/qyd_api"
echo "   bash deploy_native.sh"
echo ""
echo "3. Redis 连接信息："
echo "   主机: 127.0.0.1"
echo "   端口: 6379"
echo "   密码: 见 /tmp/redis_password.txt"
echo ""
echo "4. 查看 Redis 状态："
echo "   docker ps | grep redis"
echo "   docker logs qyd-redis"
echo ""
echo "5. 测试 Redis 连接："
echo "   docker exec qyd-redis redis-cli -a \$(cat /tmp/redis_password.txt) ping"
echo ""

# 保存环境信息
cat > /tmp/qyd_environment.txt << EOF
QYD 项目环境信息
安装时间: $(date)
操作系统: $(lsb_release -d | cut -f2)

已安装软件:
- Python: $(python3 --version)
- Node.js: $(node --version)
- npm: $(npm --version)
- Docker: $(docker --version)
- Redis: Docker 容器 (端口 6379)
- Nginx: $(nginx -v 2>&1)

Redis 信息:
- 容器名: qyd-redis
- 端口: 6379
- 密码: $(cat /tmp/redis_password.txt 2>/dev/null || echo "未设置")
- 数据卷: qyd-redis-data

下一步:
1. 重新登录以使 Docker 权限生效
2. 运行: bash deploy_native.sh
EOF

echo -e "${GREEN}环境信息已保存到: /tmp/qyd_environment.txt${NC}"
echo ""
