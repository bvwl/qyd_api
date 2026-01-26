# 前后端分离原生部署指南

本指南说明如何在不使用 Docker 的情况下，将前后端部署到不同服务器。

## 📋 目录

- [后端原生部署](#后端原生部署)
- [前端原生部署](#前端原生部署)
- [Systemd 服务配置](#systemd-服务配置)
- [Nginx 配置](#nginx-配置)

## 🔧 后端原生部署

### 后端服务器 (192.168.1.20)

#### 1. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# 安装 MySQL 客户端库
sudo apt install default-libmysqlclient-dev pkg-config -y

# 安装 Redis
sudo apt install redis-server -y
```

#### 2. 配置 Redis

```bash
# 编辑 Redis 配置
sudo vim /etc/redis/redis.conf
```

修改以下配置：

```conf
# 绑定地址（只允许本地访问）
bind 127.0.0.1

# 设置密码
requirepass redis_fNmAxZ

# 最大内存
maxmemory 2gb
maxmemory-policy allkeys-lru

# 持久化
appendonly yes
appendfsync everysec
```

重启 Redis：

```bash
sudo systemctl restart redis
sudo systemctl enable redis
```

#### 3. 部署后端代码

```bash
# 创建部署目录
sudo mkdir -p /opt/qyd
sudo chown $USER:$USER /opt/qyd

# 克隆代码
cd /opt/qyd
git clone <repo-url> .

# 进入后端目录
cd backend

# 创建虚拟环境
python3.11 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

配置以下参数：

```env
# 数据库配置
DB_HOST=192.168.1.30
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_mysql_password
DB_NAME=qyd

# Redis 配置
REDIS_ENABLED=1
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=redis_fNmAxZ

# JWT 配置
JWT_SECRET_KEY=your-secret-key-min-32-chars

# 服务配置
HOST=0.0.0.0
PORT=6080
DEBUG=0
WORKERS=4

# CORS 配置
CORS_ORIGINS=http://192.168.1.10
```

#### 5. 初始化数据库

```bash
# 激活虚拟环境
source venv/bin/activate

# 初始化数据库
python deploy_init.py
```

#### 6. 测试运行

```bash
# 测试 API 服务
python start.py

# 测试队列 Worker（新终端）
python start_queue_worker.py
```

访问 http://192.168.1.20:6080/docs 验证。

#### 7. 配置 Systemd 服务

创建 API 服务：

```bash
sudo vim /etc/systemd/system/qyd-api.service
```

内容：

```ini
[Unit]
Description=QYD Backend API Service
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/qyd/backend
Environment="PATH=/opt/qyd/backend/venv/bin"
ExecStart=/opt/qyd/backend/venv/bin/python /opt/qyd/backend/start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

创建 Queue Worker 服务：

```bash
sudo vim /etc/systemd/system/qyd-worker.service
```

内容：

```ini
[Unit]
Description=QYD Queue Worker Service
After=network.target mysql.service redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/qyd/backend
Environment="PATH=/opt/qyd/backend/venv/bin"
ExecStart=/opt/qyd/backend/venv/bin/python /opt/qyd/backend/start_queue_worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start qyd-api
sudo systemctl start qyd-worker

# 设置开机自启
sudo systemctl enable qyd-api
sudo systemctl enable qyd-worker

# 查看状态
sudo systemctl status qyd-api
sudo systemctl status qyd-worker

# 查看日志
sudo journalctl -u qyd-api -f
sudo journalctl -u qyd-worker -f
```

#### 8. 配置防火墙

```bash
# 允许 API 端口
sudo ufw allow from 192.168.1.10 to any port 6080

# 或允许所有访问
sudo ufw allow 6080
```

## 🎨 前端原生部署

### 前端服务器 (192.168.1.10)

#### 1. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# 安装 Nginx
sudo apt install nginx -y

# 验证安装
node --version
npm --version
nginx -v
```

#### 2. 构建前端

```bash
# 创建部署目录
sudo mkdir -p /opt/qyd
sudo chown $USER:$USER /opt/qyd

# 克隆代码
cd /opt/qyd
git clone <repo-url> .

# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量
vim .env.production
```

配置后端地址：

```env
VITE_API_BASE_URL=http://192.168.1.20:6080
VITE_APP_TITLE=QYD项目管理系统
```

构建前端：

```bash
# 构建生产版本
npm run build

# 构建产物在 dist/ 目录
ls -la dist/
```

#### 3. 配置 Nginx

```bash
# 创建 Nginx 配置
sudo vim /etc/nginx/sites-available/qyd
```

内容：

```nginx
server {
    listen 80;
    server_name 192.168.1.10;  # 或你的域名
    
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
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/qyd /etc/nginx/sites-enabled/

# 删除默认配置
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 设置开机自启
sudo systemctl enable nginx

# 查看状态
sudo systemctl status nginx
```

#### 4. 配置防火墙

```bash
# 允许 HTTP
sudo ufw allow 80

# 允许 HTTPS（如果使用）
sudo ufw allow 443
```

#### 5. 验证部署

访问 http://192.168.1.10 验证前端是否正常。

## 🔄 更新部署

### 更新后端

```bash
# 进入后端目录
cd /opt/qyd/backend

# 拉取最新代码
git pull

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl restart qyd-api
sudo systemctl restart qyd-worker

# 查看日志
sudo journalctl -u qyd-api -f
```

### 更新前端

```bash
# 进入前端目录
cd /opt/qyd/frontend

# 拉取最新代码
git pull

# 安装依赖
npm install

# 重新构建
npm run build

# 重启 Nginx
sudo systemctl restart nginx
```

## 🐛 故障排查

### 后端服务无法启动

```bash
# 查看服务状态
sudo systemctl status qyd-api

# 查看详细日志
sudo journalctl -u qyd-api -n 100 --no-pager

# 检查端口占用
sudo lsof -i :6080

# 手动测试
cd /opt/qyd/backend
source venv/bin/activate
python start.py
```

### 前端无法访问

```bash
# 检查 Nginx 状态
sudo systemctl status nginx

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# 测试 Nginx 配置
sudo nginx -t

# 检查文件权限
ls -la /opt/qyd/frontend/dist/
```

### Redis 连接失败

```bash
# 检查 Redis 状态
sudo systemctl status redis

# 测试 Redis 连接
redis-cli -a redis_fNmAxZ ping

# 查看 Redis 日志
sudo tail -f /var/log/redis/redis-server.log
```

## 📊 性能优化

### 后端优化

1. 增加 Uvicorn Workers：

```env
# .env
WORKERS=4  # 根据 CPU 核心数调整
```

2. 使用 Supervisor 管理多个进程：

```bash
sudo apt install supervisor -y
```

### 前端优化

1. 启用 HTTP/2：

```nginx
listen 443 ssl http2;
```

2. 配置浏览器缓存：

```nginx
location ~* \.(js|css)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🔒 安全建议

1. ✅ 使用非 root 用户运行服务
2. ✅ 配置防火墙规则
3. ✅ 使用 HTTPS（Let's Encrypt）
4. ✅ 定期更新系统和依赖
5. ✅ 配置日志轮转
6. ✅ 监控服务状态
7. ✅ 定期备份数据

## 📚 相关文档

- [Docker 部署指南](SEPARATE_DEPLOYMENT_GUIDE.md)
- [快速参考](SEPARATE_DEPLOYMENT_QUICK_REF.md)

---

**最后更新**: 2026-01-27  
**版本**: v1.0.0
