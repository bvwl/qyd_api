# QYD 项目启动指南

根据不同场景选择合适的启动方式。

## 📋 目录

- [场景选择](#场景选择)
- [场景 1: 开发环境](#场景-1-开发环境)
- [场景 2: Docker 快速部署](#场景-2-docker-快速部署)
- [场景 3: 生产环境（本地部署）](#场景-3-生产环境本地部署)
- [场景 4: 高并发生产环境](#场景-4-高并发生产环境)
- [场景 5: 仅启动后端](#场景-5-仅启动后端)
- [场景 6: 仅启动前端](#场景-6-仅启动前端)
- [常见问题](#常见问题)

---

## 场景选择

| 场景 | 适用情况 | 性能 | 复杂度 | 推荐指数 |
|------|---------|------|--------|---------|
| [开发环境](#场景-1-开发环境) | 本地开发、调试 | 低 | ⭐ | 开发必备 |
| [Docker 快速部署](#场景-2-docker-快速部署) | 快速体验、测试 | 中 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| [生产环境（本地）](#场景-3-生产环境本地部署) | 小型生产环境 | 中 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| [高并发生产](#场景-4-高并发生产环境) | 大型生产环境 | 高 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| [仅后端](#场景-5-仅启动后端) | 后端开发、API 测试 | 低 | ⭐ | ⭐⭐⭐ |
| [仅前端](#场景-6-仅启动前端) | 前端开发、UI 调试 | 低 | ⭐ | ⭐⭐⭐ |

---

## 场景 1: 开发环境

**适用于**: 本地开发、功能调试、代码测试

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0+ (本地或远程)
- Redis 7.0+ (可选)

### 启动步骤

#### 1. 启动后端

```bash
cd backend

# 首次运行：创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
vim .env  # 配置数据库连接等

# 初始化数据库（首次运行）
python deploy_init.py

# 启动后端服务
python start.py
```

后端将在 `http://localhost:6080` 启动

#### 2. 启动前端

```bash
cd frontend

# 首次运行：安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173` 启动

#### 3. 启动队列 Worker（可选）

如果需要测试异步任务处理：

```bash
cd backend
source venv/bin/activate
python start_queue_worker.py
```

### 开发技巧

```bash
# 后端热重载（代码修改自动重启）
# start.py 已配置 reload=True

# 前端热重载（Vite 自动支持）
# 修改代码后浏览器自动刷新

# 查看 API 文档
# 访问 http://localhost:6080/docs

# 查看日志
tail -f backend/logs/api.log
tail -f backend/logs/app.log
```

### 停止服务

```bash
# 按 Ctrl+C 停止后端和前端
# 或者关闭终端窗口
```

---

## 场景 2: Docker 快速部署

**适用于**: 快速体验、演示、测试环境

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- 外部 MySQL 8.0+
- 外部 Redis 7.0+ (可选)

### 一键部署

```bash
# 1. 配置环境变量
cp .env.docker .env
vim .env  # 配置 MySQL、Redis 连接

# 2. 运行部署脚本
bash docker-deploy-fast.sh
```

### 手动部署

```bash
# 1. 配置环境变量
cp .env.docker .env
vim .env

# 2. 构建镜像
docker compose build

# 3. 初始化数据库（首次部署）
docker compose run --rm backend-api python deploy_init.py

# 4. 启动所有服务
docker compose up -d

# 5. 查看状态
docker compose ps
```

### 访问地址

- 前端: http://localhost
- 后端: http://localhost:6080
- API 文档: http://localhost:6080/docs

### 服务管理

```bash
# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose stop

# 删除服务
docker compose down
```

### 详细文档

参考: [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)

---

## 场景 3: 生产环境（本地部署）

**适用于**: 小型生产环境、单服务器部署

### 环境要求

- Ubuntu Server 20.04+ / CentOS 7+
- Python 3.11+
- Node.js 18+
- MySQL 8.0+
- Redis 7.0+
- Nginx 1.18+

### 一键部署

```bash
# 1. 安装环境
sudo bash setup_environment.sh

# 2. 重新登录（使 Docker 权限生效）
exit
ssh user@server

# 3. 部署项目
bash deploy_native.sh

# 4. 配置 Nginx
sudo cp /tmp/qyd_nginx.conf /etc/nginx/sites-available/qyd
sudo ln -sf /etc/nginx/sites-available/qyd /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# 5. 配置开机自启动
sudo cp /tmp/qyd-backend.service /etc/systemd/system/
sudo cp /tmp/qyd-queue-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qyd-backend qyd-queue-worker
sudo systemctl start qyd-backend qyd-queue-worker
```

### 服务管理

```bash
# 启动服务
sudo systemctl start qyd-backend qyd-queue-worker

# 停止服务
sudo systemctl stop qyd-backend qyd-queue-worker

# 重启服务
sudo systemctl restart qyd-backend qyd-queue-worker

# 查看状态
sudo systemctl status qyd-backend qyd-queue-worker

# 查看日志
sudo journalctl -u qyd-backend -f
```

### 详细文档

参考: [QUICK_START.md](QUICK_START.md) | [NATIVE_DEPLOYMENT.md](NATIVE_DEPLOYMENT.md)

---

## 场景 4: 高并发生产环境

**适用于**: 大型生产环境、高并发场景（10000+ QPS）

### 环境要求

- 服务器: 16核心 / 32GB 内存 / 500GB SSD
- MySQL 主从集群（1主2从）
- Redis 集群或高性能单机
- Docker 20.10+
- Docker Compose 2.0+

### 部署步骤

#### 1. 配置高并发环境变量

```bash
cp .env.high_concurrency .env
vim .env
```

关键配置：

```env
# MySQL 主从配置
DB_HOST=192.168.13.6
DB_SLAVE1_HOST=192.168.13.7
DB_SLAVE2_HOST=192.168.13.8
DB_READ_WRITE_SPLIT=1

# 高并发连接池
DB_MAXSIZE=50
DB_SLAVE1_MAXSIZE=50
DB_SLAVE2_MAXSIZE=50

# Redis 队列配置
REDIS_QUEUE_BATCH_SIZE=1000
REDIS_QUEUE_NUM_WORKERS=16
REDIS_MAX_CONNECTIONS=200
```

#### 2. 系统优化

```bash
# 内核参数优化
sudo bash -c 'cat >> /etc/sysctl.conf << EOF
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 65535
net.ipv4.tcp_max_syn_backlog = 65535
fs.file-max = 1000000
EOF'

sudo sysctl -p
```

#### 3. 部署多实例

```bash
# 构建镜像
docker compose build

# 初始化数据库
docker compose run --rm backend-api python deploy_init.py

# 启动多个实例
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 查看状态
docker compose ps
```

#### 4. 配置 Nginx 负载均衡（可选）

```bash
# 安装 Nginx
sudo apt install nginx -y

# 配置负载均衡
sudo vim /etc/nginx/sites-available/qyd
```

添加配置：

```nginx
upstream backend_api {
    least_conn;
    server 127.0.0.1:6080;
    server 127.0.0.1:6081;
    server 127.0.0.1:6082;
    server 127.0.0.1:6083;
    server 127.0.0.1:6084;
    keepalive 100;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location /api/ {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

### 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看数据库连接数
mysql -h 192.168.13.6 -u root -p -e "SHOW PROCESSLIST;" | wc -l

# 查看 Redis 连接数
docker compose exec redis redis-cli -a redis_fNmAxZ CLIENT LIST | wc -l

# 压力测试
ab -n 100000 -c 1000 http://your-domain.com/api/v1/health
```

### 详细文档

参考: [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md)

---

## 场景 5: 仅启动后端

**适用于**: 后端开发、API 测试、接口调试

### 启动步骤

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 启动后端服务
python start.py

# 或使用 uvicorn 直接启动
uvicorn app.main:app --host 0.0.0.0 --port 6080 --reload
```

### 访问 API 文档

- Swagger UI: http://localhost:6080/docs
- ReDoc: http://localhost:6080/redoc

### 测试 API

```bash
# 使用 curl 测试
curl http://localhost:6080/docs

# 使用 httpie 测试（更友好）
pip install httpie
http GET http://localhost:6080/docs

# 使用 Postman 或 Insomnia
# 导入 OpenAPI 规范: http://localhost:6080/openapi.json
```

### 启动队列 Worker

```bash
cd backend
source venv/bin/activate
python start_queue_worker.py
```

---

## 场景 6: 仅启动前端

**适用于**: 前端开发、UI 调试、样式调整

### 前提条件

确保后端服务已启动（本地或远程）

### 启动步骤

```bash
cd frontend

# 配置后端 API 地址
vim .env.development
```

```env
VITE_API_BASE_URL=http://localhost:6080
# 或远程后端
# VITE_API_BASE_URL=http://192.168.1.100:6080
```

```bash
# 启动开发服务器
npm run dev
```

### 访问地址

http://localhost:5173

### 开发技巧

```bash
# 热重载（自动刷新）
# Vite 自动支持，修改代码后浏览器自动刷新

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint
```

---

## 常见问题

### 1. 端口被占用

**问题**: 启动时提示端口已被占用

**解决**:

```bash
# 查找占用端口的进程
# Linux/macOS
lsof -i :6080
lsof -i :5173

# Windows
netstat -ano | findstr :6080

# 杀死进程
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows
```

### 2. 数据库连接失败

**问题**: 后端启动失败，提示无法连接数据库

**解决**:

```bash
# 检查 MySQL 是否运行
sudo systemctl status mysql

# 测试连接
mysql -h 127.0.0.1 -u qyd -p qyd

# 检查 .env 配置
cat backend/.env | grep DB_

# 检查防火墙
sudo ufw allow 3306/tcp
```

### 3. Redis 连接失败

**问题**: 队列 Worker 无法启动

**解决**:

```bash
# 检查 Redis 是否运行
redis-cli ping

# 或 Docker 容器
docker ps | grep redis

# 测试连接
redis-cli -h 127.0.0.1 -p 6379 -a your_password ping

# 检查 .env 配置
cat backend/.env | grep REDIS_
```

### 4. 前端无法访问后端

**问题**: 前端页面加载失败，控制台报错 CORS

**解决**:

```bash
# 检查后端 CORS 配置
cat backend/.env | grep CORS_ORIGINS

# 添加前端地址
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# 重启后端
```

### 5. Docker 构建速度慢

**问题**: Docker 镜像构建或拉取很慢

**解决**:

```bash
# 配置 Docker 镜像加速
sudo vim /etc/docker/daemon.json

# 添加：
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}

# 重启 Docker
sudo systemctl restart docker
```

### 6. 权限问题

**问题**: 无法创建文件或目录

**解决**:

```bash
# 修改项目目录所有者
sudo chown -R $USER:$USER /opt/zy/qyd_api

# 或使用 sudo 运行
sudo python start.py
```

---

## 快速参考

### 环境变量配置

| 变量 | 说明 | 示例 |
|------|------|------|
| `DB_HOST` | MySQL 主库地址 | `127.0.0.1` |
| `DB_PORT` | MySQL 端口 | `3306` |
| `DB_USER` | MySQL 用户名 | `qyd` |
| `DB_PASSWORD` | MySQL 密码 | `your_password` |
| `REDIS_HOST` | Redis 地址 | `127.0.0.1` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `REDIS_PASSWORD` | Redis 密码 | `redis_password` |
| `JWT_SECRET_KEY` | JWT 密钥 | 至少32字符 |

### 默认端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端（开发） | 5173 | Vite 开发服务器 |
| 前端（生产） | 80 | Nginx |
| 后端 API | 6080 | FastAPI |
| MySQL | 3306 | 数据库 |
| Redis | 6379 | 缓存/队列 |

### 默认账号

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com
- **角色**: ADMIN

> ⚠️ 首次登录后请立即修改密码！

---

## 相关文档

### 快速开始
- [QUICK_START.md](QUICK_START.md) - 本地快速部署
- [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Docker 快速部署

### 详细部署
- [NATIVE_DEPLOYMENT.md](NATIVE_DEPLOYMENT.md) - 本地详细部署
- [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md) - 高并发部署

### 开发文档
- [backend/README.md](backend/README.md) - 后端开发指南
- [frontend/README.md](frontend/README.md) - 前端开发指南
- [.kiro/steering/conventions.md](.kiro/steering/conventions.md) - 开发规范

### 性能优化
- [docs/performance/SCALE_TO_10K_GUIDE.md](docs/performance/SCALE_TO_10K_GUIDE.md) - 扩展到 10000+ QPS
- [docs/performance/PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md) - 性能配置参考

---

**最后更新**: 2026-01-26  
**版本**: v1.0.0
