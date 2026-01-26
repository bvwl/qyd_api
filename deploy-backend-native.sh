#!/bin/bash

# ==========================================
# 后端服务器原生部署脚本
# 服务器: 192.168.1.20
# 服务: Backend API + Queue Worker + Redis
# ==========================================

set -e

echo "=========================================="
echo "QYD 后端服务器原生部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否为 root 用户
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}错误: 请不要使用 root 用户运行此脚本${NC}"
    exit 1
fi

# 检查 Python 3.11
echo -e "\n${YELLOW}[1/8] 检查 Python 环境...${NC}"
if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}错误: Python 3.11 未安装${NC}"
    echo "请先安装: sudo apt install python3.11 python3.11-venv python3-pip -y"
    exit 1
fi
echo -e "${GREEN}✓ Python 环境检查通过${NC}"

# 创建部署目录
echo -e "\n${YELLOW}[2/7] 创建部署目录...${NC}"
DEPLOY_DIR="/opt/qyd"
if [ ! -d "$DEPLOY_DIR" ]; then
    sudo mkdir -p "$DEPLOY_DIR"
    sudo chown $USER:$USER "$DEPLOY_DIR"
fi
cd "$DEPLOY_DIR"
echo -e "${GREEN}✓ 部署目录: $DEPLOY_DIR${NC}"

# 克隆或更新代码
echo -e "\n${YELLOW}[3/7] 获取代码...${NC}"
if [ -d ".git" ]; then
    echo -e "${YELLOW}更新代码...${NC}"
    git pull
else
    echo -e "${YELLOW}请手动克隆代码到 $DEPLOY_DIR${NC}"
    echo "git clone <repo-url> $DEPLOY_DIR"
    exit 1
fi

# 进入后端目录
cd backend

# 创建虚拟环境
echo -e "\n${YELLOW}[4/7] 创建虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi
source venv/bin/activate

# 安装依赖
echo -e "\n${YELLOW}[5/7] 安装依赖...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 配置环境变量
echo -e "\n${YELLOW}[6/7] 配置环境变量...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ 已复制 .env.example 到 .env${NC}"
    fi
fi

echo -e "${YELLOW}请编辑 .env 文件配置以下参数：${NC}"
echo "  - DB_HOST: MySQL 服务器地址"
echo "  - DB_PASSWORD: MySQL 密码"
echo "  - REDIS_HOST: Redis 服务器地址"
echo "  - REDIS_PASSWORD: Redis 密码"
echo "  - JWT_SECRET_KEY: JWT 密钥"
echo "  - CORS_ORIGINS: 前端服务器地址"
echo ""
read -p "是否现在编辑 .env 文件？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    vim .env
fi

# 初始化数据库
echo -e "\n${YELLOW}[7/7] 初始化数据库...${NC}"
read -p "是否需要初始化数据库？(首次部署选 y) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python deploy_init.py
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
fi

# 创建 Systemd 服务
echo -e "\n${YELLOW}创建 Systemd 服务...${NC}"

# API 服务
sudo tee /etc/systemd/system/qyd-api.service > /dev/null <<EOF
[Unit]
Description=QYD Backend API Service
After=network.target mysql.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$DEPLOY_DIR/backend
Environment="PATH=$DEPLOY_DIR/backend/venv/bin"
ExecStart=$DEPLOY_DIR/backend/venv/bin/python $DEPLOY_DIR/backend/start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Queue Worker 服务
sudo tee /etc/systemd/system/qyd-worker.service > /dev/null <<EOF
[Unit]
Description=QYD Queue Worker Service
After=network.target mysql.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$DEPLOY_DIR/backend
Environment="PATH=$DEPLOY_DIR/backend/venv/bin"
ExecStart=$DEPLOY_DIR/backend/venv/bin/python $DEPLOY_DIR/backend/start_queue_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
echo -e "\n${YELLOW}启动服务...${NC}"
sudo systemctl start qyd-api
sudo systemctl start qyd-worker

# 设置开机自启
sudo systemctl enable qyd-api
sudo systemctl enable qyd-worker

echo -e "${GREEN}✓ 服务启动完成${NC}"

# 检查服务状态
echo -e "\n${YELLOW}检查服务状态...${NC}"
sleep 3
sudo systemctl status qyd-api --no-pager
sudo systemctl status qyd-worker --no-pager

echo -e "\n${GREEN}=========================================="
echo "后端部署完成！"
echo "==========================================${NC}"
echo ""
echo "服务地址："
echo "  - API 文档: http://$(hostname -I | awk '{print $1}'):6080/docs"
echo "  - API 地址: http://$(hostname -I | awk '{print $1}'):6080"
echo ""
echo "常用命令："
echo "  - 查看 API 状态: sudo systemctl status qyd-api"
echo "  - 查看 Worker 状态: sudo systemctl status qyd-worker"
echo "  - 查看 API 日志: sudo journalctl -u qyd-api -f"
echo "  - 查看 Worker 日志: sudo journalctl -u qyd-worker -f"
echo "  - 重启 API: sudo systemctl restart qyd-api"
echo "  - 重启 Worker: sudo systemctl restart qyd-worker"
echo ""
