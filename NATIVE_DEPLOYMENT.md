# 本地部署指南（非 Docker）

本指南说明如何在服务器上直接部署 QYD 项目，并配置开机自启动。

## 📋 目录

- [环境要求](#环境要求)
- [快速部署](#快速部署)
- [手动部署](#手动部署)
- [配置开机自启动](#配置开机自启动)
- [服务管理](#服务管理)
- [故障排查](#故障排查)

## 🔧 环境要求

### 必需软件

- **Python**: 3.11+
- **Node.js**: 18+
- **MySQL**: 8.0+ (已部署并运行)
- **Redis**: 7.0+ (已部署并运行)
- **Nginx**: 1.18+ (用于前端静态文件服务)

### 检查环境

```bash
# 检查 Python
python3 --version

# 检查 Node.js
node --version
npm --version

# 检查 MySQL
mysql --version

# 检查 Redis
redis-cli --version

# 检查 Nginx
nginx -v
```

## 🚀 快速部署

### 使用自动部署脚本

```bash
# 1. 进入项目目录
cd /opt/zy/qyd_api

# 2. 赋予执行权限
chmod +x deploy_native.sh

# 3. 运行部署脚本
./deploy_native.sh
```

脚本会自动完成：
- ✅ 检查环境
- ✅ 部署后端（创建虚拟环境、安装依赖）
- ✅ 部署前端（安装依赖、构建）
- ✅ 生成 Nginx 配置
- ✅ 生成 Systemd 服务配置
- ✅ 初始化数据库（可选）

## 📝 手动部署

### 1. 部署后端

```bash
cd /opt/zy/qyd_api/backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env

# 必须配置的参数：
# - DB_HOST（MySQL 主库地址）
# - DB_PASSWORD（MySQL 密码）
# - REDIS_HOST（Redis 地址）
# - REDIS_PASSWORD（Redis 密码）
# - JWT_SECRET_KEY（JWT 密钥，至少32字符）

# 初始化数据库（首次部署）
python deploy_init.py

# 测试启动
python start.py
# 按 Ctrl+C 停止
```

### 2. 部署前端

```bash
cd /opt/zy/qyd_api/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 构建产物在 dist/ 目录
ls -la dist/
```

### 3. 配置 Nginx

创建 Nginx 配置文件：

```bash
sudo vim /etc/nginx/sites-available/qyd
```

添加以下内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 修改为你的域名或 IP
    
    # 前端静态文件
    location / {
        root /opt/zy/qyd_api/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /v1/ {
        proxy_pass http://127.0.0.1:6080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /opt/zy/qyd_api/frontend/dist;
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
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/qyd /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

## 🔄 配置开机自启动

使用 Systemd 管理服务，实现开机自启动。

### 1. 创建后端 API 服务

```bash
sudo vim /etc/systemd/system/qyd-backend.service
```

添加以下内容：

```ini
[Unit]
Description=QYD Backend API Service
After=network.target mysql.service redis.service
Wants=mysql.service redis.service

[Service]
Type=simple
User=root  # 修改为你的用户名
WorkingDirectory=/opt/zy/qyd_api/backend
Environment="PATH=/opt/zy/qyd_api/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/zy/qyd_api/backend/venv/bin/python /opt/zy/qyd_api/backend/start.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/zy/qyd_api/backend/logs/systemd.log
StandardError=append:/opt/zy/qyd_api/backend/logs/systemd-error.log

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

### 2. 创建队列 Worker 服务

```bash
sudo vim /etc/systemd/system/qyd-queue-worker.service
```

添加以下内容：

```ini
[Unit]
Description=QYD Queue Worker Service
After=network.target mysql.service redis.service qyd-backend.service
Wants=mysql.service redis.service
Requires=qyd-backend.service

[Service]
Type=simple
User=root  # 修改为你的用户名
WorkingDirectory=/opt/zy/qyd_api/backend
Environment="PATH=/opt/zy/qyd_api/backend/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/zy/qyd_api/backend/venv/bin/python /opt/zy/qyd_api/backend/start_queue_worker.py
Restart=always
RestartSec=10
StandardOutput=append:/opt/zy/qyd_api/backend/logs/queue-worker.log
StandardError=append:/opt/zy/qyd_api/backend/logs/queue-worker-error.log

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
```

### 3. 启用并启动服务

```bash
# 重新加载 Systemd 配置
sudo systemctl daemon-reload

# 启用开机自启动
sudo systemctl enable qyd-backend
sudo systemctl enable qyd-queue-worker

# 启动服务
sudo systemctl start qyd-backend
sudo systemctl start qyd-queue-worker

# 查看状态
sudo systemctl status qyd-backend
sudo systemctl status qyd-queue-worker
```

## 🔧 服务管理

### 常用命令

```bash
# 启动服务
sudo systemctl start qyd-backend
sudo systemctl start qyd-queue-worker

# 停止服务
sudo systemctl stop qyd-backend
sudo systemctl stop qyd-queue-worker

# 重启服务
sudo systemctl restart qyd-backend
sudo systemctl restart qyd-queue-worker

# 查看状态
sudo systemctl status qyd-backend
sudo systemctl status qyd-queue-worker

# 查看日志
sudo journalctl -u qyd-backend -f
sudo journalctl -u qyd-queue-worker -f

# 查看最近 100 行日志
sudo journalctl -u qyd-backend -n 100

# 禁用开机自启动
sudo systemctl disable qyd-backend
sudo systemctl disable qyd-queue-worker
```

### 查看应用日志

```bash
# 后端日志
tail -f /opt/zy/qyd_api/backend/logs/api.log
tail -f /opt/zy/qyd_api/backend/logs/app.log
tail -f /opt/zy/qyd_api/backend/logs/database.log

# Systemd 日志
tail -f /opt/zy/qyd_api/backend/logs/systemd.log
tail -f /opt/zy/qyd_api/backend/logs/queue-worker.log
```

### 更新代码

```bash
# 1. 拉取最新代码
cd /opt/zy/qyd_api
git pull

# 2. 更新后端依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 3. 更新前端
cd ../frontend
npm install
npm run build

# 4. 重启服务
sudo systemctl restart qyd-backend qyd-queue-worker

# 5. 重启 Nginx（如果前端有更新）
sudo systemctl restart nginx
```

## 🐛 故障排查

### 1. 服务无法启动

**查看详细错误**：

```bash
# 查看服务状态
sudo systemctl status qyd-backend

# 查看完整日志
sudo journalctl -u qyd-backend -xe

# 查看应用日志
tail -f /opt/zy/qyd_api/backend/logs/systemd-error.log
```

**常见问题**：

- **端口被占用**：
  ```bash
  # 查找占用 6080 端口的进程
  sudo lsof -i :6080
  
  # 杀死进程
  sudo kill -9 <PID>
  ```

- **权限问题**：
  ```bash
  # 检查文件权限
  ls -la /opt/zy/qyd_api/backend/
  
  # 修改所有者
  sudo chown -R your-user:your-user /opt/zy/qyd_api/
  ```

- **虚拟环境问题**：
  ```bash
  # 重新创建虚拟环境
  cd /opt/zy/qyd_api/backend
  rm -rf venv
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```

### 2. 数据库连接失败

**测试连接**：

```bash
# 测试 MySQL 连接
mysql -h 127.0.0.1 -u qyd -p qyd

# 测试 Redis 连接
redis-cli -h 127.0.0.1 -p 6379 -a your_password ping
```

**检查配置**：

```bash
# 查看 .env 配置
cat /opt/zy/qyd_api/backend/.env | grep -E "DB_|REDIS_"
```

### 3. Nginx 配置问题

**测试配置**：

```bash
# 测试 Nginx 配置
sudo nginx -t

# 查看 Nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# 查看 Nginx 访问日志
sudo tail -f /var/log/nginx/access.log
```

### 4. 前端无法访问

**检查文件**：

```bash
# 检查构建产物
ls -la /opt/zy/qyd_api/frontend/dist/

# 检查 Nginx 配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 5. 服务重启后自动停止

**查看日志**：

```bash
# 查看崩溃日志
sudo journalctl -u qyd-backend --since "10 minutes ago"

# 查看系统日志
sudo dmesg | tail -50
```

**增加重启延迟**：

编辑服务文件，增加 `RestartSec`：

```ini
[Service]
Restart=always
RestartSec=30  # 增加到 30 秒
```

## 📊 性能优化

### 1. 使用 Supervisor（可选）

如果不想使用 Systemd，可以使用 Supervisor：

```bash
# 安装 Supervisor
sudo apt-get install supervisor

# 创建配置
sudo vim /etc/supervisor/conf.d/qyd.conf
```

```ini
[program:qyd-backend]
command=/opt/zy/qyd_api/backend/venv/bin/python /opt/zy/qyd_api/backend/start.py
directory=/opt/zy/qyd_api/backend
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/zy/qyd_api/backend/logs/supervisor.log

[program:qyd-queue-worker]
command=/opt/zy/qyd_api/backend/venv/bin/python /opt/zy/qyd_api/backend/start_queue_worker.py
directory=/opt/zy/qyd_api/backend
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/zy/qyd_api/backend/logs/queue-worker-supervisor.log
```

```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start qyd-backend qyd-queue-worker

# 查看状态
sudo supervisorctl status
```

### 2. 配置日志轮转

```bash
sudo vim /etc/logrotate.d/qyd
```

```
/opt/zy/qyd_api/backend/logs/*.log {
    daily
    rotate 90
    compress
    delaycompress
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        systemctl reload qyd-backend qyd-queue-worker > /dev/null 2>&1 || true
    endscript
}
```

## 🔒 安全建议

1. ✅ 使用非 root 用户运行服务
2. ✅ 配置防火墙规则
3. ✅ 使用 HTTPS（配置 SSL 证书）
4. ✅ 定期更新依赖包
5. ✅ 定期备份数据库
6. ✅ 限制文件权限
7. ✅ 配置日志轮转
8. ✅ 监控服务状态
9. ✅ 使用强密码
10. ✅ 定期检查日志

## 📚 相关文档

- [Docker 部署指南](DOCKER_DEPLOY_WITH_REDIS.md)
- [性能优化指南](docs/performance/SCALE_TO_10K_GUIDE.md)
- [后端 README](backend/README.md)
- [前端 README](frontend/README.md)

---

**最后更新**: 2026-01-26  
**版本**: v1.2.5
