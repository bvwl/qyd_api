# 部署架构说明

本文档详细说明 QYD 项目的部署架构和容器化方案。

## 📋 目录

- [架构概览](#架构概览)
- [容器化方案](#容器化方案)
- [前端部署](#前端部署)
- [后端部署](#后端部署)
- [网络架构](#网络架构)
- [数据持久化](#数据持久化)
- [性能优化](#性能优化)

## 🏗️ 架构概览

### 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户访问层                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  浏览器 → http://localhost (Port 80)                            │
│           http://localhost:6080 (API)                           │
│                                                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                      Docker 容器层                               │
├────────────────────────────┼────────────────────────────────────┤
│                            │                                     │
│  ┌─────────────────────────▼──────────────────────────────┐    │
│  │              Frontend Container (Nginx)                 │    │
│  │  - 提供静态文件服务                                      │    │
│  │  - 反向代理 API 请求                                     │    │
│  │  - 镜像大小: ~30MB                                       │    │
│  │  - 端口: 80                                              │    │
│  └─────────────────────────┬──────────────────────────────┘    │
│                            │                                     │
│  ┌─────────────────────────▼──────────────────────────────┐    │
│  │           Backend API Container (FastAPI)               │    │
│  │  - 处理 HTTP 请求                                        │    │
│  │  - JWT 认证                                              │    │
│  │  - 业务逻辑处理                                          │    │
│  │  - 镜像大小: ~500MB                                      │    │
│  │  - 端口: 6080                                            │    │
│  └─────────────────────────┬──────────────────────────────┘    │
│                            │                                     │
│  ┌─────────────────────────▼──────────────────────────────┐    │
│  │         Queue Worker Container (Python)                 │    │
│  │  - 处理 Redis 队列任务                                   │    │
│  │  - 批量数据处理                                          │    │
│  │  - 异步任务执行                                          │    │
│  │  - 镜像大小: ~500MB                                      │    │
│  │  - 无需暴露端口                                          │    │
│  └─────────────────────────┬──────────────────────────────┘    │
│                            │                                     │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                      外部服务层                                  │
├────────────────────────────┼────────────────────────────────────┤
│                            │                                     │
│  ┌──────────────┐    ┌─────▼──────┐    ┌──────────────┐       │
│  │    MySQL     │    │   Redis    │    │  Log Files   │       │
│  │   (外部)     │    │   (外部)   │    │   (挂载)     │       │
│  │  Port: 3306  │    │ Port: 6379 │    │              │       │
│  └──────────────┘    └────────────┘    └──────────────┘       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 服务职责

| 服务 | 职责 | 技术栈 | 端口 |
|------|------|--------|------|
| **Frontend** | 静态文件服务、API 代理 | Nginx Alpine | 80 |
| **Backend API** | HTTP 请求处理、业务逻辑 | FastAPI + Python 3.11 | 6080 |
| **Queue Worker** | 异步任务处理、批量操作 | Python 3.11 + Redis | - |
| **MySQL** | 数据持久化 | MySQL 8.0 | 3306 |
| **Redis** | 缓存、队列 | Redis 7.0 | 6379 |

## 🐳 容器化方案

### 为什么使用容器化？

1. **环境一致性**: 开发、测试、生产环境完全一致
2. **快速部署**: 一键启动所有服务
3. **资源隔离**: 每个服务独立运行，互不影响
4. **易于扩展**: 可以轻松增加容器实例
5. **版本管理**: 镜像版本化，方便回滚

### Docker Compose 配置

```yaml
version: '3.8'

services:
  # 前端服务
  frontend:
    build:
      context: ./frontend
    container_name: qyd-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    networks:
      - qyd-network
    depends_on:
      - backend-api

  # 后端 API 服务
  backend-api:
    build:
      context: ./backend
      target: backend-api
    container_name: qyd-backend-api
    restart: unless-stopped
    ports:
      - "6080:6080"
    environment:
      - DB_HOST=host.docker.internal
      - REDIS_HOST=host.docker.internal
    volumes:
      - ./backend/logs:/app/logs
    networks:
      - qyd-network
    depends_on:
      - queue-worker

  # 队列 Worker 服务
  queue-worker:
    build:
      context: ./backend
      target: queue-worker
    container_name: qyd-queue-worker
    restart: unless-stopped
    environment:
      - DB_HOST=host.docker.internal
      - REDIS_HOST=host.docker.internal
    volumes:
      - ./backend/logs:/app/logs
    networks:
      - qyd-network

networks:
  qyd-network:
    driver: bridge
```

## 🎨 前端部署

### 多阶段构建

前端使用 Docker 多阶段构建，分为构建阶段和生产阶段。

#### 第一阶段：构建（Builder）

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用（生成 dist 目录）
RUN npm run build
```

**说明**：
- 使用 Node.js 18 Alpine 镜像（体积小）
- `npm ci` 比 `npm install` 更快、更可靠
- 执行 `npm run build` 生成生产版本

#### 第二阶段：生产（Nginx）

```dockerfile
FROM nginx:alpine

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
```

**说明**：
- 使用 Nginx Alpine 镜像（体积小）
- 只复制构建产物（dist 目录）
- 不包含 Node.js、源码、node_modules

### 为什么使用多阶段构建？

| 对比项 | 单阶段构建 | 多阶段构建 |
|--------|-----------|-----------|
| **镜像大小** | ~800MB | ~30MB |
| **包含内容** | Node.js + 源码 + 依赖 + 构建产物 | 只有 Nginx + 静态文件 |
| **安全性** | 暴露源码和依赖 | 不暴露源码 |
| **启动速度** | 慢 | 快 |
| **性能** | 一般 | 优秀（Nginx 优化） |

### Nginx 配置

```nginx
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # 前端路由（SPA）
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /v1/ {
        proxy_pass http://backend-api:6080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**功能**：
- 提供静态文件服务
- 支持 React Router（SPA 路由）
- 反向代理 API 请求到后端
- 静态资源缓存优化

### 构建流程

```bash
# 1. 构建镜像
docker-compose build frontend

# 构建过程：
# Step 1: 使用 Node.js 镜像
# Step 2: 安装依赖 (npm ci)
# Step 3: 构建应用 (npm run build)
# Step 4: 切换到 Nginx 镜像
# Step 5: 复制构建产物
# Step 6: 配置 Nginx

# 2. 启动容器
docker-compose up -d frontend

# 3. 访问应用
# http://localhost
```

### 优势总结

✅ **体积小**: 最终镜像只有 ~30MB  
✅ **性能好**: Nginx 专门优化静态文件服务  
✅ **安全性高**: 不暴露源码和依赖  
✅ **启动快**: 无需运行时编译  
✅ **易维护**: 配置简单，易于更新  

## 🔧 后端部署

### 后端 Dockerfile

```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 6080

# 启动命令
CMD ["python", "start.py"]
```

### 多目标构建

后端使用多目标构建，支持不同的启动命令：

```dockerfile
# 基础镜像
FROM python:3.11-slim as base
# ... 安装依赖 ...

# API 服务
FROM base as backend-api
CMD ["python", "start.py"]

# 队列 Worker
FROM base as queue-worker
CMD ["python", "start_queue_worker.py"]
```

### 环境变量配置

```env
# 数据库配置
DB_HOST=host.docker.internal  # Docker 访问宿主机
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_password
DB_NAME=qyd

# Redis 配置
REDIS_HOST=host.docker.internal
REDIS_PORT=6379
REDIS_PASSWORD=your_password

# 队列配置
REDIS_QUEUE_BATCH_SIZE=200
REDIS_QUEUE_NUM_WORKERS=4

# 服务配置
HOST=0.0.0.0
PORT=6080
DEBUG=0
WORKERS=1
```

## 🌐 网络架构

### Docker 网络

```yaml
networks:
  qyd-network:
    driver: bridge
```

**特点**：
- 所有容器在同一网络中
- 容器间可以通过服务名通信
- 自动 DNS 解析

### 容器间通信

```
frontend → backend-api:6080
backend-api → queue-worker (通过 Redis)
backend-api → MySQL (host.docker.internal:3306)
queue-worker → MySQL (host.docker.internal:3306)
backend-api → Redis (host.docker.internal:6379)
queue-worker → Redis (host.docker.internal:6379)
```

### 访问外部服务

使用 `host.docker.internal` 访问宿主机服务：

```python
# 容器内访问宿主机的 MySQL
DB_HOST = "host.docker.internal"
DB_PORT = 3306

# 容器内访问宿主机的 Redis
REDIS_HOST = "host.docker.internal"
REDIS_PORT = 6379
```

## 💾 数据持久化

### 日志持久化

```yaml
volumes:
  - ./backend/logs:/app/logs
```

**说明**：
- 容器内的日志写入 `/app/logs`
- 自动同步到宿主机 `./backend/logs`
- 容器删除后日志不丢失

### 日志结构

```
backend/logs/
├── api/2026/01/26/
│   ├── api.log
│   └── api.log.2026-01-26_10.gz
├── app/2026/01/26/
│   ├── app.log
│   └── app.log.2026-01-26_10.gz
├── database/2026/01/26/
│   └── database.log
└── scheduler/2026/01/26/
    └── scheduler.log
```

### 数据库备份

```bash
# 备份（在宿主机执行）
mysqldump -u qyd -p qyd > backup-$(date +%Y%m%d).sql

# 恢复
mysql -u qyd -p qyd < backup-20260126.sql
```

## ⚡ 性能优化

### 容器资源限制

```yaml
services:
  backend-api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 健康检查

```yaml
services:
  backend-api:
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:6080/docs', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 日志轮转

```yaml
services:
  backend-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 扩展队列 Worker

```bash
# 启动 3 个队列 Worker 实例
docker-compose up -d --scale queue-worker=3

# 查看运行状态
docker-compose ps
```

## 📊 监控和维护

### 查看容器状态

```bash
# 查看所有容器
docker-compose ps

# 查看资源使用
docker stats

# 查看容器详情
docker inspect qyd-backend-api
```

### 查看日志

```bash
# 实时查看所有日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend-api

# 查看最近 100 行
docker-compose logs --tail=100 backend-api
```

### 进入容器调试

```bash
# 进入后端容器
docker-compose exec backend-api bash

# 执行 Python 脚本
docker-compose exec backend-api python check_deployment.py

# 查看环境变量
docker-compose exec backend-api env
```

## 🔒 安全建议

1. ✅ 使用非 root 用户运行容器
2. ✅ 限制容器资源使用
3. ✅ 使用 Docker secrets 管理敏感信息
4. ✅ 定期更新基础镜像
5. ✅ 扫描镜像漏洞
6. ✅ 配置防火墙规则
7. ✅ 使用 HTTPS（配置 SSL 证书）
8. ✅ 限制容器网络访问
9. ✅ 定期备份数据
10. ✅ 监控容器日志

## 📚 相关文档

- [Docker 完整部署指南](DOCKER_DEPLOYMENT.md)
- [Docker 快速参考](DOCKER_QUICK_REFERENCE.md)
- [性能优化指南](../performance/SCALE_TO_10K_GUIDE.md)
- [项目结构说明](../../.kiro/steering/structure.md)

---

**最后更新**: 2026-01-26  
**版本**: v1.2.0
