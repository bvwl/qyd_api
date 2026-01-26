#!/bin/bash

# ==========================================
# 前端服务器原生部署脚本
# 服务器: 192.168.1.10
# 服务: Frontend (Nginx)
# ==========================================

set -e

echo "=========================================="
echo "QYD 前端服务器原生部署脚本"
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

# 检查 Node.js
echo -e "\n${YELLOW}[1/6] 检查 Node.js 环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: Node.js 未安装${NC}"
    echo "请先安装 Node.js 18:"
    echo "curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "sudo apt install nodejs -y"
    exit 1
fi
echo -e "${GREEN}✓ Node.js 版本: $(node --version)${NC}"

# 检查 Nginx
echo -e "\n${YELLOW}[2/6] 检查 Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}Nginx 未安装，正在安装...${NC}"
    sudo apt update
    sudo apt install nginx -y
fi
echo -e "${GREEN}✓ Nginx 版本: $(nginx -v 2>&1 | cut -d'/' -f2)${NC}"

# 创建部署目录
echo -e "\n${YELLOW}[3/6] 创建部署目录...${NC}"
DEPLOY_DIR="/opt/qyd"
if [ ! -d "$DEPLOY_DIR" ]; then
    sudo mkdir -p "$DEPLOY_DIR"
    sudo chown $USER:$USER "$DEPLOY_DIR"
fi
cd "$DEPLOY_DIR"
echo -e "${GREEN}✓ 部署目录: $DEPLOY_DIR${NC}"

# 克隆或更新代码
echo -e "\n${YELLOW}[4/6] 获取代码...${NC}"
if [ -d ".git" ]; then
    echo -e "${YELLOW}更新代码...${NC}"
    git pull
else
    echo -e "${YELLOW}请手动克隆代码到 $DEPLOY_DIR${NC}"
    echo "git clone <repo-url> $DEPLOY_DIR"
    exit 1
fi

# 进入前端目录
cd frontend

# 配置环境变量
echo -e "\n${YELLOW}[5/6] 配置环境变量...${NC}"
if [ ! -f .env.production ]; then
    cat > .env.production <<EOF
VITE_API_BASE_URL=http://192.168.1.20:6080
VITE_APP_TITLE=QYD项目管理系统
EOF
    echo -e "${GREEN}✓ 已创建 .env.production${NC}"
fi

echo -e "${YELLOW}请检查 .env.production 中的后端地址${NC}"
read -p "是否现在编辑 .env.production 文件？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    vim .env.production
fi

# 安装依赖并构建
echo -e "\n${YELLOW}[6/6] 构建前端...${NC}"
npm install
npm run build
echo -e "${GREEN}✓ 前端构建完成${NC}"

# 配置 Nginx
echo -e "\n${YELLOW}配置 Nginx...${NC}"
sudo tee /etc/nginx/sites-available/qyd > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;
    
    # 前端静态文件目录
    root /opt/qyd/frontend/dist;
    index index.html;
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json application/javascript;
    
    # 前端路由支持
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache";
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# 启用配置
sudo ln -sf /etc/nginx/sites-available/qyd /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
echo -e "\n${YELLOW}测试 Nginx 配置...${NC}"
sudo nginx -t

# 重启 Nginx
echo -e "\n${YELLOW}重启 Nginx...${NC}"
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${GREEN}✓ Nginx 配置完成${NC}"

# 检查服务状态
echo -e "\n${YELLOW}检查服务状态...${NC}"
sudo systemctl status nginx --no-pager

echo -e "\n${GREEN}=========================================="
echo "前端部署完成！"
echo "==========================================${NC}"
echo ""
echo "访问地址："
echo "  - 前端应用: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "常用命令："
echo "  - 查看 Nginx 状态: sudo systemctl status nginx"
echo "  - 查看 Nginx 日志: sudo tail -f /var/log/nginx/error.log"
echo "  - 重启 Nginx: sudo systemctl restart nginx"
echo "  - 测试配置: sudo nginx -t"
echo ""
echo "更新前端："
echo "  cd $DEPLOY_DIR/frontend"
echo "  git pull"
echo "  npm install"
echo "  npm run build"
echo "  sudo systemctl restart nginx"
echo ""
