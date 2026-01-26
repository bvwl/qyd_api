#!/bin/bash

# ==========================================
# QYD 项目本地部署脚本
# 前后端直接运行，Redis 使用 Docker 容器
# ==========================================

set -e

echo "=========================================="
echo "QYD 项目本地部署"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ==========================================
# 1. 检查环境
# ==========================================
echo -e "${YELLOW}[1/7] 检查环境...${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python3${NC}"
    echo "请先运行: sudo bash setup_environment.sh"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python: $PYTHON_VERSION${NC}"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到 Node.js${NC}"
    echo "请先运行: sudo bash setup_environment.sh"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js: $NODE_VERSION${NC}"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: 未找到 npm${NC}"
    echo "请先运行: sudo bash setup_environment.sh"
    exit 1
fi
NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓ npm: $NPM_VERSION${NC}"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未找到 Docker${NC}"
    echo "请先运行: sudo bash setup_environment.sh"
    exit 1
fi
DOCKER_VERSION=$(docker --version | awk '{print $3}' | tr -d ',')
echo -e "${GREEN}✓ Docker: $DOCKER_VERSION${NC}"

# 检查 Redis 容器
if ! docker ps | grep -q qyd-redis; then
    echo -e "${RED}错误: Redis 容器未运行${NC}"
    echo "请先运行: sudo bash setup_environment.sh"
    exit 1
fi
echo -e "${GREEN}✓ Redis: 容器运行中${NC}"

# 检查 Nginx
if ! command -v nginx &> /dev/null; then
    echo -e "${YELLOW}警告: 未找到 Nginx${NC}"
    echo "Nginx 用于提供前端静态文件服务"
    echo "安装: sudo apt-get install nginx"
else
    NGINX_VERSION=$(nginx -v 2>&1 | awk '{print $3}')
    echo -e "${GREEN}✓ Nginx: $NGINX_VERSION${NC}"
fi

echo ""

# ==========================================
# 2. 部署后端
# ==========================================
echo -e "${YELLOW}[2/7] 部署后端...${NC}"

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt -q

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}警告: 未找到 .env 文件，从 .env.example 复制${NC}"
    cp .env.example .env
    
    # 自动配置 Redis
    if [ -f "/tmp/redis_password.txt" ]; then
        REDIS_PASSWORD=$(cat /tmp/redis_password.txt | cut -d'=' -f2)
        sed -i "s/REDIS_HOST=.*/REDIS_HOST=127.0.0.1/" .env
        sed -i "s/REDIS_PORT=.*/REDIS_PORT=6379/" .env
        sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" .env
        echo -e "${GREEN}✓ Redis 配置已自动填写${NC}"
    fi
    
    echo -e "${RED}请编辑 backend/.env 配置数据库连接信息${NC}"
    echo "必须配置："
    echo "  - DB_HOST（MySQL 主库地址）"
    echo "  - DB_PASSWORD（MySQL 密码）"
    echo "  - JWT_SECRET_KEY（JWT 密钥，至少32字符）"
    echo ""
    read -p "按回车键继续编辑 .env 文件..." 
    ${EDITOR:-vim} .env
fi

echo -e "${GREEN}✓ 后端部署完成${NC}"

cd ..
echo ""

# ==========================================
# 3. 部署前端
# ==========================================
echo -e "${YELLOW}[3/7] 部署前端...${NC}"

cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装 Node.js 依赖..."
    npm install
else
    echo "Node.js 依赖已存在，跳过安装"
fi

# 构建前端
echo "构建前端应用（跳过类型检查）..."
npx vite build

echo -e "${GREEN}✓ 前端构建完成${NC}"

cd ..
echo ""

# ==========================================
# 4. 配置 Nginx
# ==========================================
echo -e "${YELLOW}[4/7] 配置 Nginx...${NC}"

if command -v nginx &> /dev/null; then
    # 创建 Nginx 配置
    cat > /tmp/qyd_nginx.conf << EOF
server {
    listen 80;
    server_name _;
    
    # 前端静态文件
    location / {
        root $SCRIPT_DIR/frontend/dist;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    # API 代理
    location /v1/ {
        proxy_pass http://127.0.0.1:6080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root $SCRIPT_DIR/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss;
}
EOF
    
    echo -e "${GREEN}✓ Nginx 配置已生成: /tmp/qyd_nginx.conf${NC}"
    echo ""
    echo "请手动安装 Nginx 配置："
    echo "  sudo cp /tmp/qyd_nginx.conf /etc/nginx/sites-available/qyd"
    echo "  sudo ln -sf /etc/nginx/sites-available/qyd /etc/nginx/sites-enabled/"
    echo "  sudo rm -f /etc/nginx/sites-enabled/default  # 删除默认配置"
    echo "  sudo nginx -t"
    echo "  sudo systemctl reload nginx"
    echo ""
else
    echo -e "${YELLOW}跳过 Nginx 配置（未安装）${NC}"
fi
echo ""

# ==========================================
# 5. 配置 Systemd 服务
# ==========================================
echo -e "${YELLOW}[5/7] 配置 Systemd 服务...${NC}"

# 后端 API 服务
cat > /tmp/qyd-backend.service << EOF
[Unit]
Description=QYD Backend API Service
After=network.target mysql.service docker.service
Wants=mysql.service docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR/backend
Environment="PATH=$SCRIPT_DIR/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$SCRIPT_DIR/backend/venv/bin/python $SCRIPT_DIR/backend/start.py
Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/backend/logs/systemd.log
StandardError=append:$SCRIPT_DIR/backend/logs/systemd-error.log

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# 队列 Worker 服务
cat > /tmp/qyd-queue-worker.service << EOF
[Unit]
Description=QYD Queue Worker Service
After=network.target mysql.service docker.service qyd-backend.service
Wants=mysql.service docker.service
Requires=qyd-backend.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR/backend
Environment="PATH=$SCRIPT_DIR/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$SCRIPT_DIR/backend/venv/bin/python $SCRIPT_DIR/backend/start_queue_worker.py
Restart=always
RestartSec=10
StandardOutput=append:$SCRIPT_DIR/backend/logs/queue-worker.log
StandardError=append:$SCRIPT_DIR/backend/logs/queue-worker-error.log

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Systemd 服务配置已生成${NC}"
echo "  /tmp/qyd-backend.service"
echo "  /tmp/qyd-queue-worker.service"
echo ""
echo "请手动安装服务："
echo "  sudo cp /tmp/qyd-backend.service /etc/systemd/system/"
echo "  sudo cp /tmp/qyd-queue-worker.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable qyd-backend qyd-queue-worker"
echo "  sudo systemctl start qyd-backend qyd-queue-worker"
echo ""

# ==========================================
# 6. 初始化数据库
# ==========================================
echo -e "${YELLOW}[6/7] 初始化数据库...${NC}"

cd backend
source venv/bin/activate

read -p "是否需要初始化数据库？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "初始化数据库..."
    python deploy_init.py
    echo -e "${GREEN}✓ 数据库初始化完成${NC}"
else
    echo "跳过数据库初始化"
fi

cd ..
echo ""

# ==========================================
# 7. 生成快速启动脚本
# ==========================================
echo -e "${YELLOW}[7/7] 生成快速启动脚本...${NC}"

# 创建快速启动脚本
cat > start_services.sh << 'EOF'
#!/bin/bash

# 快速启动 QYD 服务

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "启动 QYD 服务..."

# 检查 Redis 容器
if ! docker ps | grep -q qyd-redis; then
    echo "启动 Redis 容器..."
    docker start qyd-redis
    sleep 2
fi

# 启动后端
cd "$SCRIPT_DIR/backend"
source venv/bin/activate
nohup python start.py > logs/nohup-api.log 2>&1 &
echo "后端 API 已启动 (PID: $!)"

# 启动队列 Worker
nohup python start_queue_worker.py > logs/nohup-worker.log 2>&1 &
echo "队列 Worker 已启动 (PID: $!)"

echo "服务启动完成！"
echo "访问: http://localhost"
EOF

chmod +x start_services.sh

# 创建快速停止脚本
cat > stop_services.sh << 'EOF'
#!/bin/bash

# 快速停止 QYD 服务

echo "停止 QYD 服务..."

# 停止 Python 进程
pkill -f "python.*start.py"
pkill -f "python.*start_queue_worker.py"

echo "服务已停止"
EOF

chmod +x stop_services.sh

echo -e "${GREEN}✓ 快速启动脚本已生成${NC}"
echo "  ./start_services.sh  # 启动服务"
echo "  ./stop_services.sh   # 停止服务"
echo ""

# ==========================================
# 完成
# ==========================================
echo ""
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "后续步骤："
echo ""
echo "1. 配置 Nginx（见上面的命令）"
echo ""
echo "2. 安装 Systemd 服务（推荐，开机自启动）："
echo "   sudo cp /tmp/qyd-backend.service /etc/systemd/system/"
echo "   sudo cp /tmp/qyd-queue-worker.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable qyd-backend qyd-queue-worker"
echo "   sudo systemctl start qyd-backend qyd-queue-worker"
echo ""
echo "3. 或使用快速启动脚本（临时启动）："
echo "   ./start_services.sh"
echo ""
echo "4. 查看服务状态："
echo "   sudo systemctl status qyd-backend qyd-queue-worker"
echo ""
echo "5. 查看日志："
echo "   sudo journalctl -u qyd-backend -f"
echo "   tail -f backend/logs/api.log"
echo ""
echo "访问地址："
echo "  前端: http://your-server-ip"
echo "  后端: http://your-server-ip:6080"
echo "  API 文档: http://your-server-ip:6080/docs"
echo ""
echo "Redis 信息："
echo "  容器: qyd-redis"
echo "  端口: 6379"
echo "  密码: 见 /tmp/redis_password.txt"
echo ""

