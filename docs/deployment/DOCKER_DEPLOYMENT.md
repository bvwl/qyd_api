# Docker 部署指南

本指南说明如何使用 Docker 部署 QYD 项目（前后端分离），连接到已有的 MySQL 和 Redis 服务。

## 📋 目录

- [架构说明](#架构说明)
- [前置要求](#前置要求)
- [快速部署](#快速部署)
- [详细步骤](#详细步骤)
- [配置说明](#配置说明)
- [常用命令](#常用命令)
- [故障排查](#故障排查)

## 🏗️ 架构说明

### 服务组成

```
┌─────────────────────────────────────────────────────────┐
│                      Docker 容器                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Frontend   │  │ Backend API  │  │Queue Worker  │ │
│  │   (Nginx)    │  │  (FastAPI)   │  │  (Python)    │ │
│  │   Port: 80   │  │  Port: 6080  │  │              │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                  │                  │          │
│         └──────────────────┴──────────────────┘          │
│                            │                             │
└────────────────────────────┼─────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
         ┌──────▼──────┐          ┌──────▼──────┐
         │    MySQL    │          │    Redis    │
         │  (外部服务)  │          │  (外部服务)  │
         └─────────────┘          └─────────────┘
```

### 容器说明

1. **frontend**: Nginx 服务器，提供前端静态文件和 API 代理
2. **backend-api**: FastAPI 应用，处理 HTTP 请求
3. **queue-worker**: Python 进程，处理 Redis 队列任务

## 🔧 前置要求

### 必需软件

- **Docker**: 20.10 或更高版本
- **Docker Compose**: 2.0 或更高版本

### 外部服务

- **MySQL**: 8.0 或更高版本（已部署并运行）
- **Redis**: 7.0 或更高版本（已部署并运行）

### 检查 Docker 安装

```bash
docker --version
docker-compose --version
```

## 🚀 快速部署

### 一键部署

```bash
bash docker-deploy.sh
```

脚本会自动完成：
1. ✅ 检查 Docker 环境
2. ✅ 配置环境变量
3. ✅ 构建 Docker 镜像
4. ✅ 初始化数据库
5. ✅ 启动所有服务

### 手动部署

```bash
# 1. 配置环境变量
cp .env.docker .env
vim .env  # 编辑配置

# 2. 构建镜像
docker-compose build

# 3. 初始化数据库
docker-compose run --rm backend-api python deploy_init.py

# 4. 启动服务
docker-compose up -d

# 5. 查看状态
docker-compose ps
```

## 📝 详细步骤

### 步骤 1: 准备环境变量

复制环境变量模板：

```bash
cp .env.docker .env
```

编辑 `.env` 文件，配置以下关键参数：

```env
# MySQL 配置
DB_HOST=host.docker.internal  # 如果 MySQL 在宿主机
# DB_HOST=192.168.1.100       # 如果 MySQL 在其他服务器
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_mysql_password
DB_NAME=qyd

# Redis 配置
REDIS_HOST=host.docker.internal  # 如果 Redis 在宿主机
# REDIS_HOST=192.168.1.100       # 如果 Redis 在其他服务器
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# JWT 密钥（至少32字符）
JWT_SECRET_KEY=your-secret-key-change-in-production-min-32-chars

# CORS 配置
CORS_ORIGINS=http://localhost,http://your-domain.com
```

**重要说明**:
- `host.docker.internal`: Docker 容器访问宿主机的特殊域名
- 如果 MySQL/Redis 在其他服务器，使用实际 IP 地址
- 确保防火墙允许 Docker 容器访问 MySQL/Redis

### 步骤 2: 构建 Docker 镜像

```bash
# 构建所有镜像
docker-compose build

# 或分别构建
docker-compose build backend-api
docker-compose build queue-worker
docker-compose build frontend
```

构建过程说明：
- **后端镜像**: 基于 Python 3.11，安装所有依赖
- **前端镜像**: 使用 Node.js 构建，然后用 Nginx 提供服务
- **多阶段构建**: 优化镜像大小

### 步骤 3: 初始化数据库

**首次部署时必须执行**：

```bash
docker-compose run --rm backend-api python deploy_init.py
```

这会自动完成：
- ✅ 创建数据库表结构
- ✅ 导入角色数据（ADMIN, GM, IT, MANUAL）
- ✅ 导入路由数据（菜单和权限）
- ✅ 创建管理员用户（zhiyu）
- ✅ 绑定权限

**如果数据库已初始化，可以跳过此步骤。**

### 步骤 4: 启动服务

```bash
# 启动所有服务（后台运行）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 步骤 5: 验证部署

访问以下地址验证服务：

- **前端应用**: http://localhost
- **后端 API**: http://localhost:6080
- **API 文档**: http://localhost:6080/docs

使用默认管理员账号登录：
- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com

⚠️ **首次登录后请立即修改密码！**

## ⚙️ 配置说明

### 环境变量详解

#### 数据库配置

```env
# 主库配置
DB_HOST=host.docker.internal  # MySQL 主机地址
DB_PORT=3306                   # MySQL 端口
DB_USER=qyd                    # 数据库用户
DB_PASSWORD=password           # 数据库密码
DB_NAME=qyd                    # 数据库名称
DB_MINSIZE=5                   # 连接池最小连接数
DB_MAXSIZE=20                  # 连接池最大连接数
```

#### Redis 配置

```env
REDIS_ENABLED=1                # 是否启用 Redis (1=启用, 0=禁用)
REDIS_HOST=host.docker.internal  # Redis 主机地址
REDIS_PORT=6379                # Redis 端口
REDIS_PASSWORD=password        # Redis 密码
REDIS_DB=0                     # Redis 数据库编号
REDIS_MAX_CONNECTIONS=50       # 最大连接数
```

#### 队列配置

```env
# 标准性能（2000条/秒）
REDIS_QUEUE_BATCH_SIZE=200
REDIS_QUEUE_NUM_WORKERS=4

# 高性能（6000条/秒）
REDIS_QUEUE_BATCH_SIZE=300
REDIS_QUEUE_NUM_WORKERS=8

# 超高性能（12000条/秒）
REDIS_QUEUE_BATCH_SIZE=500
REDIS_QUEUE_NUM_WORKERS=12
```

#### 服务配置

```env
DEBUG=0                        # 调试模式 (0=关闭, 1=开启)
WORKERS=1                      # Uvicorn workers 数量
LOG_LEVEL=INFO                 # 日志级别
LOG_RETENTION_DAYS=90          # 日志保留天数
```

#### CORS 配置

```env
# 允许的前端地址（逗号分隔）
CORS_ORIGINS=http://localhost,http://localhost:80,http://your-domain.com
```

### 端口映射

| 服务 | 容器端口 | 宿主机端口 | 说明 |
|------|---------|-----------|------|
| frontend | 80 | 80 | 前端应用 |
| backend-api | 6080 | 6080 | 后端 API |
| queue-worker | - | - | 无需暴露端口 |

**修改端口映射**：

编辑 `docker-compose.yml`：

```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 修改为 8080
  
  backend-api:
    ports:
      - "8000:6080"  # 修改为 8000
```

### 数据持久化

日志和状态文件会持久化到宿主机：

```yaml
volumes:
  - ./backend/logs:/app/logs      # 日志目录
  - ./backend/status:/app/status  # 状态文件
```

## 🔨 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose stop

# 重启所有服务
docker-compose restart

# 删除所有服务（保留数据）
docker-compose down

# 删除所有服务和数据
docker-compose down -v

# 查看服务状态
docker-compose ps

# 查看服务资源使用
docker stats
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend-api
docker-compose logs -f queue-worker
docker-compose logs -f frontend

# 查看最近 100 行日志
docker-compose logs --tail=100 backend-api

# 查看实时日志（不包含历史）
docker-compose logs -f --tail=0 backend-api
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend-api bash

# 进入前端容器
docker-compose exec frontend sh

# 进入队列 Worker 容器
docker-compose exec queue-worker bash
```

### 执行命令

```bash
# 在后端容器中执行 Python 脚本
docker-compose exec backend-api python check_deployment.py

# 运行数据库迁移
docker-compose exec backend-api aerich upgrade

# 重新初始化数据库
docker-compose run --rm backend-api python deploy_init.py
```

### 镜像管理

```bash
# 重新构建镜像
docker-compose build --no-cache

# 拉取最新镜像
docker-compose pull

# 查看镜像
docker images | grep qyd

# 删除未使用的镜像
docker image prune -a
```

### 扩展服务

```bash
# 启动多个队列 Worker 实例
docker-compose up -d --scale queue-worker=3

# 查看扩展后的服务
docker-compose ps
```

## 🐛 故障排查

### 1. 容器无法启动

**问题**: 容器启动后立即退出

**排查步骤**:

```bash
# 查看容器日志
docker-compose logs backend-api

# 查看容器状态
docker-compose ps

# 检查配置
docker-compose config
```

**常见原因**:
- 环境变量配置错误
- 数据库连接失败
- Redis 连接失败
- 端口被占用

### 2. 无法连接数据库

**问题**: `Can't connect to MySQL server`

**解决方案**:

```bash
# 1. 检查 MySQL 是否运行
mysql -h localhost -u qyd -p

# 2. 检查防火墙
sudo ufw status
sudo ufw allow 3306

# 3. 检查 MySQL 绑定地址
# 编辑 /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0

# 4. 重启 MySQL
sudo systemctl restart mysql

# 5. 测试容器内连接
docker-compose exec backend-api python -c "
import pymysql
conn = pymysql.connect(
    host='host.docker.internal',
    port=3306,
    user='qyd',
    password='password',
    database='qyd'
)
print('连接成功')
"
```

### 3. 无法连接 Redis

**问题**: `Error connecting to Redis`

**解决方案**:

```bash
# 1. 检查 Redis 是否运行
redis-cli ping

# 2. 检查 Redis 配置
# 编辑 /etc/redis/redis.conf
bind 0.0.0.0
protected-mode no

# 3. 重启 Redis
sudo systemctl restart redis

# 4. 测试容器内连接
docker-compose exec backend-api python -c "
import redis
r = redis.Redis(
    host='host.docker.internal',
    port=6379,
    password='password'
)
print(r.ping())
"
```

### 4. 前端无法访问后端

**问题**: 前端显示网络错误

**解决方案**:

1. 检查 CORS 配置：

```env
# .env 文件
CORS_ORIGINS=http://localhost,http://localhost:80
```

2. 检查前端 API 地址：

```env
# .env 文件
VITE_API_BASE_URL=http://localhost:6080
```

3. 使用 Nginx 代理（推荐）：

前端通过 `/api/` 路径访问后端，Nginx 自动代理到 `backend-api:6080`

### 5. 端口被占用

**问题**: `Bind for 0.0.0.0:80 failed: port is already allocated`

**解决方案**:

```bash
# 查找占用端口的进程
sudo lsof -i :80
sudo lsof -i :6080

# 停止占用端口的服务
sudo systemctl stop nginx
sudo systemctl stop apache2

# 或修改 docker-compose.yml 中的端口映射
```

### 6. 镜像构建失败

**问题**: 构建过程中出错

**解决方案**:

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建（不使用缓存）
docker-compose build --no-cache

# 检查 Dockerfile 语法
docker-compose config
```

### 7. 容器内存不足

**问题**: 容器被 OOM Killer 杀死

**解决方案**:

```bash
# 查看容器资源使用
docker stats

# 限制容器内存（编辑 docker-compose.yml）
services:
  backend-api:
    mem_limit: 1g
    mem_reservation: 512m
```

### 8. 日志文件过大

**问题**: 日志占用大量磁盘空间

**解决方案**:

```bash
# 配置日志轮转（编辑 docker-compose.yml）
services:
  backend-api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

# 手动清理日志
docker-compose logs --no-log-prefix > /dev/null
```

## 📊 监控和维护

### 健康检查

所有服务都配置了健康检查：

```bash
# 查看健康状态
docker-compose ps

# 查看详细健康信息
docker inspect qyd-backend-api | grep -A 10 Health
```

### 性能监控

```bash
# 实时监控资源使用
docker stats

# 查看容器进程
docker-compose top

# 查看网络连接
docker network inspect qyd_qyd-network
```

### 备份和恢复

```bash
# 备份日志
tar -czf logs-backup-$(date +%Y%m%d).tar.gz backend/logs/

# 备份数据库（在 MySQL 服务器上）
mysqldump -u qyd -p qyd > backup-$(date +%Y%m%d).sql

# 恢复数据库
mysql -u qyd -p qyd < backup-20260126.sql
```

## 🔒 安全建议

1. ✅ 使用强密码作为 `JWT_SECRET_KEY`（至少32字符）
2. ✅ 限制 `CORS_ORIGINS` 为特定域名
3. ✅ 使用 HTTPS（配置 SSL 证书）
4. ✅ 定期更新 Docker 镜像
5. ✅ 限制容器资源使用
6. ✅ 使用 Docker secrets 管理敏感信息
7. ✅ 配置防火墙规则
8. ✅ 定期备份数据
9. ✅ 监控容器日志
10. ✅ 使用非 root 用户运行容器

## 📚 相关文档

- [完整部署指南](backend/DEPLOYMENT_GUIDE.md)
- [快速参考](backend/QUICK_DEPLOY_REFERENCE.md)
- [性能优化](docs/performance/SCALE_TO_10K_GUIDE.md)
- [项目结构](.kiro/steering/structure.md)

## 🆘 获取帮助

如遇到问题：

1. 查看容器日志：`docker-compose logs -f`
2. 检查服务状态：`docker-compose ps`
3. 查看本文档的[故障排查](#故障排查)部分
4. 提交 Issue 到项目仓库

---

**最后更新**: 2026-01-26  
**版本**: v1.2.0
