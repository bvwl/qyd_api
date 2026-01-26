#!/bin/bash

# QYD 项目快速更新脚本
# 用途：拉取最新代码并重新部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数定义
function print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

function print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查是否在项目根目录
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "请在项目根目录运行此脚本"
    exit 1
fi

print_info "开始更新 QYD 项目..."

# 1. 拉取最新代码
print_info "步骤 1/5: 拉取最新代码"
git pull origin main
if [ $? -ne 0 ]; then
    print_error "拉取代码失败"
    exit 1
fi

# 2. 检查部署方式
print_info "步骤 2/5: 检查部署方式"

if [ -f "docker-compose.yml" ] && command -v docker &> /dev/null; then
    DEPLOY_TYPE="docker"
    print_info "检测到 Docker 部署"
elif systemctl is-active --quiet qyd-backend; then
    DEPLOY_TYPE="systemd"
    print_info "检测到 Systemd 部署"
else
    print_warning "未检测到运行中的服务，将尝试 Docker 部署"
    DEPLOY_TYPE="docker"
fi

# 3. 根据部署方式更新
if [ "$DEPLOY_TYPE" = "docker" ]; then
    print_info "步骤 3/5: Docker 部署更新"
    
    # 停止服务
    print_info "停止服务..."
    docker compose down
    
    # 重新构建
    print_info "重新构建镜像..."
    docker compose build
    
    # 启动服务
    print_info "启动服务..."
    docker compose up -d
    
    # 等待服务启动
    sleep 5
    
    # 检查状态
    print_info "步骤 4/5: 检查服务状态"
    docker compose ps
    
elif [ "$DEPLOY_TYPE" = "systemd" ]; then
    print_info "步骤 3/5: Systemd 部署更新"
    
    # 更新后端
    print_info "更新后端依赖..."
    cd backend
    if [ -d "venv" ]; then
        source venv/bin/activate
        pip install -r requirements.txt -q
    else
        print_warning "未找到虚拟环境，跳过后端依赖更新"
    fi
    cd ..
    
    # 更新前端
    print_info "更新前端..."
    cd frontend
    if command -v npm &> /dev/null; then
        npm install --silent
        npm run build
    else
        print_warning "未找到 npm，跳过前端更新"
    fi
    cd ..
    
    # 重启服务
    print_info "重启服务..."
    sudo systemctl restart qyd-backend qyd-queue-worker
    
    # 重启 Nginx（如果存在）
    if systemctl is-active --quiet nginx; then
        sudo systemctl restart nginx
    fi
    
    # 等待服务启动
    sleep 3
    
    # 检查状态
    print_info "步骤 4/5: 检查服务状态"
    sudo systemctl status qyd-backend --no-pager -l
    sudo systemctl status qyd-queue-worker --no-pager -l
fi

# 5. 验证部署
print_info "步骤 5/5: 验证部署"

if [ "$DEPLOY_TYPE" = "docker" ]; then
    # 检查容器是否运行
    RUNNING_CONTAINERS=$(docker compose ps --services --filter "status=running" | wc -l)
    TOTAL_CONTAINERS=$(docker compose ps --services | wc -l)
    
    if [ "$RUNNING_CONTAINERS" -eq "$TOTAL_CONTAINERS" ]; then
        print_info "所有容器运行正常 ($RUNNING_CONTAINERS/$TOTAL_CONTAINERS)"
    else
        print_warning "部分容器未运行 ($RUNNING_CONTAINERS/$TOTAL_CONTAINERS)"
    fi
    
    # 显示日志
    print_info "查看最近日志（按 Ctrl+C 退出）："
    sleep 2
    docker compose logs --tail=50 -f
    
elif [ "$DEPLOY_TYPE" = "systemd" ]; then
    # 检查服务状态
    if systemctl is-active --quiet qyd-backend && systemctl is-active --quiet qyd-queue-worker; then
        print_info "所有服务运行正常"
    else
        print_warning "部分服务未运行"
    fi
    
    # 显示日志
    print_info "查看最近日志（按 Ctrl+C 退出）："
    sleep 2
    sudo journalctl -u qyd-backend -u qyd-queue-worker -f
fi

print_info "更新完成！"
