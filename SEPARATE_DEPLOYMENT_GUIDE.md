# 前后端分离部署指南

本指南说明如何将前端和后端部署到不同的服务器上。

## 📋 目录

- [架构说明](#架构说明)
- [部署方案](#部署方案)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [配置说明](#配置说明)
- [故障排查](#故障排查)

## 🏗️ 架构说明

### 分离部署架构

```
┌─────────────────────┐         ┌─────────────────────┐
│   前端服务器 A       │         │   后端服务器 B       │
│  (192.168.1.10)     │         │  (192.168.1.20)     │
├─────────────────────┤         ├─────────────────────┤
│                     │         │                     │
│  ┌───────────────┐ │         │  ┌───────────────┐ │
│  │   Frontend    │ │         │  │  Backend API  │ │
│  │   (Nginx)     │ │◄────────┤  │  (FastAPI)    │ │
│  │   Port: 80    │ │  CORS   │  │  Port: 6080   │ │
│  └───────────────┘ │         │  └───────────────┘ │
│                     │         │                     │
└─────────────────────┘         │  ┌───────────────┐ │
                                │  │ Queue Worker  │ │
                                │  │  (Python)     │ │
                                │  └───────────────┘ │
                                │                     │
                                │  ┌───────────────┐ │
                                │  │     Redis     │ │
                                │  │   Port: 6379  │ │
                                │  └───────────────┘ │
                                │                     │
                                └──────────┬──────────┘
                                           │
                                    ┌──────▼──────┐
                                    │    MySQL    │
                                    │ (外部服务)   │
                                    └─────────────┘
```


### 部署优势

- ✅ **独立扩展**: 前后端可以独立扩展资源
- ✅ **故障隔离**: 一方故障不影响另一方
- ✅ **灵活部署**: 可以使用不同的服务器配置
- ✅ **安全性**: 后端可以部署在内网，只暴露必要的端口
- ✅ **负载均衡**: 可以部署多个后端实例

## 🚀 部署方案

### 方案一：Docker 部署（推荐）

**前端服务器**: 使用 Docker 部署 Nginx 容器  
**后端服务器**: 使用 Docker 部署 FastAPI + Queue Worker + Redis

### 方案二：原生部署

**前端服务器**: 直接使用 Nginx 部署静态文件  
**后端服务器**: 使用 systemd 管理 Python 进程

## 📦 后端部署

### 后端服务器配置

**服务器**: 192.168.1.20  
**服务**: Backend API + Queue Worker + Redis  
**端口**: 6080 (API), 6379 (Redis)

### Docker 部署后端

#### 1. 准备后端服务器

在后端服务器 (192.168.1.20) 上执行：

```bash
# 克隆项目代码
git clone <your-repo-url> /opt/qyd
cd /opt/qyd

# 配置环境变量
cp .env.backend .env
vim .env
```

编辑 `.env` 文件，配置以下参数：

```env
# MySQL 配置
DB_HOST=192.168.1.30
DB_PASSWORD=your_mysql_password

# Redis 密码
REDIS_PASSWORD=redis_fNmAxZ

# JWT 密钥（至少32字符）
JWT_SECRET_KEY=your-secret-key-change-in-production-min-32-chars

# CORS 配置（前端服务器地址）
CORS_ORIGINS=http://192.168.1.10,http://192.168.1.10:80
```

#### 2. 一键部署后端

```bash
# 赋予执行权限
chmod +x deploy-backend.sh

# 运行部署脚本
bash deploy-backend.sh
```

脚本会自动完成：
- ✅ 检查 Docker 环境
- ✅ 配置环境变量
- ✅ 构建 Docker 镜像
- ✅ 初始化数据库（可选）
- ✅ 启动所有服务

#### 3. 手动部署后端

```bash
# 构建镜像
docker-compose -f docker-compose.backend.yml build

# 初始化数据库（首次部署）
docker-compose -f docker-compose.backend.yml run --rm backend-api python deploy_init.py

# 启动服务
docker-compose -f docker-compose.backend.yml up -d

# 查看状态
docker-compose -f docker-compose.backend.yml ps

# 查看日志
docker-compose -f docker-compose.backend.yml logs -f
```

#### 4. 验证后端部署

访问以下地址验证：

- **API 文档**: http://192.168.1.20:6080/docs
- **健康检查**: http://192.168.1.20:6080/health

## 🎨 前端部署

### 前端服务器配置

**服务器**: 192.168.1.10  
**服务**: Frontend (Nginx)  
**端口**: 80

### Docker 部署前端

#### 1. 准备前端服务器

在前端服务器 (192.168.1.10) 上执行：

```bash
# 克隆项目代码
git clone <your-repo-url> /opt/qyd
cd /opt/qyd

# 配置环境变量
cp .env.frontend .env
vim .env
```

编辑 `.env` 文件，配置后端地址：

```env
# 后端 API 地址
VITE_API_BASE_URL=http://192.168.1.20:6080
```

#### 2. 一键部署前端

```bash
# 赋予执行权限
chmod +x deploy-frontend.sh

# 运行部署脚本
bash deploy-frontend.sh
```

脚本会自动完成：
- ✅ 检查 Docker 环境
- ✅ 配置环境变量
- ✅ 构建 Docker 镜像
- ✅ 启动服务

#### 3. 手动部署前端

```bash
# 构建镜像
docker-compose -f docker-compose.frontend.yml build

# 启动服务
docker-compose -f docker-compose.frontend.yml up -d

# 查看状态
docker-compose -f docker-compose.frontend.yml ps

# 查看日志
docker-compose -f docker-compose.frontend.yml logs -f
```

#### 4. 验证前端部署

访问前端应用：

- **前端地址**: http://192.168.1.10

使用默认管理员账号登录：
- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com

## ⚙️ 配置说明

### 网络配置

#### 防火墙规则

**后端服务器** (192.168.1.20):

```bash
# 允许前端服务器访问 API
sudo ufw allow from 192.168.1.10 to any port 6080

# 或允许所有访问（不推荐）
sudo ufw allow 6080
```

**前端服务器** (192.168.1.10):

```bash
# 允许所有访问前端
sudo ufw allow 80
sudo ufw allow 443  # 如果使用 HTTPS
```

#### CORS 配置

后端 `.env` 文件中必须配置前端地址：

```env
# 允许的前端地址（多个用逗号分隔）
CORS_ORIGINS=http://192.168.1.10,http://192.168.1.10:80,http://yourdomain.com
```

### 域名配置

如果使用域名访问，需要配置 DNS 和 Nginx：

#### 前端域名配置

1. 配置 DNS 解析：
   - `www.yourdomain.com` → 192.168.1.10

2. 修改前端 Nginx 配置 (`frontend/nginx.conf`):

```nginx
server {
    listen 80;
    server_name www.yourdomain.com;
    
    # ... 其他配置
}
```

3. 更新后端 CORS 配置：

```env
CORS_ORIGINS=http://www.yourdomain.com,https://www.yourdomain.com
```

#### 后端域名配置

1. 配置 DNS 解析：
   - `api.yourdomain.com` → 192.168.1.20

2. 更新前端 API 地址：

```env
VITE_API_BASE_URL=http://api.yourdomain.com
```

### HTTPS 配置

#### 使用 Let's Encrypt 免费证书

**前端服务器**:

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d www.yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

**后端服务器**:

```bash
# 获取证书
sudo certbot --nginx -d api.yourdomain.com
```

更新配置后重新构建：

```bash
# 前端
docker-compose -f docker-compose.frontend.yml build
docker-compose -f docker-compose.frontend.yml up -d

# 后端
docker-compose -f docker-compose.backend.yml build
docker-compose -f docker-compose.backend.yml up -d
```

## 🔨 常用命令

### 后端服务器

```bash
# 查看服务状态
docker-compose -f docker-compose.backend.yml ps

# 查看日志
docker-compose -f docker-compose.backend.yml logs -f backend-api
docker-compose -f docker-compose.backend.yml logs -f queue-worker
docker-compose -f docker-compose.backend.yml logs -f redis

# 重启服务
docker-compose -f docker-compose.backend.yml restart

# 停止服务
docker-compose -f docker-compose.backend.yml stop

# 更新部署
git pull
docker-compose -f docker-compose.backend.yml build
docker-compose -f docker-compose.backend.yml up -d

# 扩展队列 Worker
docker-compose -f docker-compose.backend.yml up -d --scale queue-worker=3
```

### 前端服务器

```bash
# 查看服务状态
docker-compose -f docker-compose.frontend.yml ps

# 查看日志
docker-compose -f docker-compose.frontend.yml logs -f

# 重启服务
docker-compose -f docker-compose.frontend.yml restart

# 停止服务
docker-compose -f docker-compose.frontend.yml stop

# 更新部署
git pull
docker-compose -f docker-compose.frontend.yml build
docker-compose -f docker-compose.frontend.yml up -d
```

## 🐛 故障排查

### 1. 前端无法访问后端

**问题**: 前端显示网络错误或 CORS 错误

**排查步骤**:

```bash
# 1. 检查后端是否运行
curl http://192.168.1.20:6080/docs

# 2. 检查防火墙
sudo ufw status

# 3. 检查 CORS 配置
docker-compose -f docker-compose.backend.yml exec backend-api env | grep CORS

# 4. 查看后端日志
docker-compose -f docker-compose.backend.yml logs -f backend-api
```

**解决方案**:

1. 确保后端 CORS 配置包含前端地址：

```env
CORS_ORIGINS=http://192.168.1.10,http://192.168.1.10:80
```

2. 开放防火墙端口：

```bash
sudo ufw allow from 192.168.1.10 to any port 6080
```

3. 重启后端服务：

```bash
docker-compose -f docker-compose.backend.yml restart
```

### 2. 后端无法连接数据库

**问题**: 后端日志显示 "Can't connect to MySQL server"

**排查步骤**:

```bash
# 1. 测试数据库连接
mysql -h 192.168.1.30 -u qyd -p

# 2. 检查防火墙（在数据库服务器上）
sudo ufw allow from 192.168.1.20 to any port 3306

# 3. 检查 MySQL 绑定地址
# 编辑 /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0

# 4. 重启 MySQL
sudo systemctl restart mysql
```

### 3. 前端构建失败

**问题**: 前端镜像构建时出错

**解决方案**:

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建（不使用缓存）
docker-compose -f docker-compose.frontend.yml build --no-cache

# 检查 Node.js 版本
docker run --rm node:18-alpine node --version
```

### 4. Redis 连接失败

**问题**: 后端无法连接 Redis

**排查步骤**:

```bash
# 1. 检查 Redis 容器
docker-compose -f docker-compose.backend.yml ps redis

# 2. 测试 Redis 连接
docker-compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ ping

# 3. 查看 Redis 日志
docker-compose -f docker-compose.backend.yml logs redis

# 4. 重启 Redis
docker-compose -f docker-compose.backend.yml restart redis
```

## 📊 性能优化

### 后端优化

#### 1. 扩展 API 实例

```bash
# 启动多个 API 实例
docker-compose -f docker-compose.backend.yml up -d --scale backend-api=3

# 配置 Nginx 负载均衡
# 在前端服务器上配置反向代理
```

#### 2. 扩展队列 Worker

```bash
# 启动多个 Worker 实例
docker-compose -f docker-compose.backend.yml up -d --scale queue-worker=3
```

#### 3. 调整队列配置

编辑 `.env`:

```env
# 高性能配置
REDIS_QUEUE_BATCH_SIZE=500
REDIS_QUEUE_NUM_WORKERS=12
```

### 前端优化

#### 1. 启用 Gzip 压缩

前端 Nginx 已默认启用 Gzip 压缩。

#### 2. 配置 CDN

将静态资源上传到 CDN，修改 `frontend/nginx.conf`:

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    # 重定向到 CDN
    return 301 https://cdn.yourdomain.com$request_uri;
}
```

## 🔒 安全建议

### 后端安全

1. ✅ 使用强密码作为 JWT_SECRET_KEY（至少32字符）
2. ✅ 限制 CORS_ORIGINS 为特定域名
3. ✅ 配置防火墙，只允许前端服务器访问
4. ✅ 使用 HTTPS 加密通信
5. ✅ 定期更新 Docker 镜像
6. ✅ 限制容器资源使用
7. ✅ 定期备份数据库
8. ✅ 监控容器日志

### 前端安全

1. ✅ 使用 HTTPS
2. ✅ 配置 CSP (Content Security Policy)
3. ✅ 启用 HSTS (HTTP Strict Transport Security)
4. ✅ 定期更新依赖
5. ✅ 配置防火墙

## 📚 相关文档

- [Docker 快速部署](DOCKER_QUICK_START.md)
- [Docker 部署指南](docs/deployment/DOCKER_DEPLOYMENT.md)
- [性能优化指南](docs/performance/SCALE_TO_10K_GUIDE.md)
- [项目结构](.kiro/steering/structure.md)

---

**最后更新**: 2026-01-27  
**版本**: v1.0.0
