# Docker 快速部署指南

使用国内镜像加速，快速部署 QYD 项目。

## 🚀 一键部署

```bash
# 1. 进入项目目录
cd /opt/zy/qyd_api

# 2. 赋予执行权限
chmod +x docker-deploy-fast.sh

# 3. 运行部署脚本
bash docker-deploy-fast.sh
```

脚本会自动：
- ✅ 检查 Docker 环境
- ✅ 配置 Docker 国内镜像加速
- ✅ 配置环境变量
- ✅ 构建镜像（使用国内源）
- ✅ 初始化数据库
- ✅ 启动所有服务

## 📋 详细步骤

### 步骤 1: 配置 Docker 镜像加速

如果脚本没有自动配置，可以手动配置：

```bash
sudo vim /etc/docker/daemon.json
```

添加以下内容：

```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

重启 Docker：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 步骤 2: 配置环境变量

```bash
cp .env.docker .env
vim .env
```

必须配置的参数：

```env
# MySQL 主库
DB_HOST=192.168.1.100
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_mysql_password
DB_NAME=qyd

# MySQL 从库（可选）
DB_READ_WRITE_SPLIT=1
DB_SLAVE1_HOST=192.168.1.101
DB_SLAVE1_PORT=3306
DB_SLAVE1_USER=qyd
DB_SLAVE1_PASSWORD=slave_password

# Redis 密码
REDIS_PASSWORD=redis_fNmAxZ

# JWT 密钥（至少32字符）
JWT_SECRET_KEY=your-secret-key-min-32-chars-here
```

### 步骤 3: 构建并启动

```bash
# 构建镜像
docker compose build

# 初始化数据库（首次部署）
docker compose run --rm backend-api python deploy_init.py

# 启动所有服务
docker compose up -d

# 查看状态
docker compose ps
```

## 🔧 服务管理

### 查看服务状态

```bash
# 查看所有服务
docker compose ps

# 查看详细信息
docker ps
```

### 查看日志

```bash
# 查看所有日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend-api
docker compose logs -f frontend
docker compose logs -f redis
docker compose logs -f queue-worker

# 查看最近 100 行
docker compose logs --tail=100 backend-api
```

### 重启服务

```bash
# 重启所有服务
docker compose restart

# 重启特定服务
docker compose restart backend-api
docker compose restart frontend
```

### 停止服务

```bash
# 停止所有服务
docker compose stop

# 停止特定服务
docker compose stop backend-api
```

### 删除服务

```bash
# 删除所有服务（保留数据）
docker compose down

# 删除所有服务和数据
docker compose down -v
```

## 🔄 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker compose build

# 3. 重启服务
docker compose up -d

# 4. 查看日志
docker compose logs -f
```

## 🐛 故障排查

### 1. 构建速度慢

**问题**：下载镜像或安装依赖很慢

**解决**：

```bash
# 检查 Docker 镜像配置
cat /etc/docker/daemon.json

# 如果没有配置，添加镜像加速
sudo vim /etc/docker/daemon.json

# 重启 Docker
sudo systemctl restart docker

# 清理缓存重新构建
docker compose build --no-cache
```

### 2. 容器无法启动

**问题**：容器启动后立即退出

**解决**：

```bash
# 查看容器日志
docker compose logs backend-api

# 查看容器状态
docker compose ps

# 检查配置
docker compose config

# 进入容器调试
docker compose run --rm backend-api bash
```

### 3. 无法连接数据库

**问题**：后端报错 "Can't connect to MySQL server"

**解决**：

```bash
# 检查 MySQL 是否可访问
mysql -h 192.168.1.100 -u qyd -p

# 检查防火墙
sudo ufw allow from 172.0.0.0/8 to any port 3306

# 检查 MySQL 绑定地址
# 编辑 /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0

# 重启 MySQL
sudo systemctl restart mysql

# 测试容器内连接
docker compose exec backend-api python -c "
import pymysql
conn = pymysql.connect(
    host='192.168.1.100',
    port=3306,
    user='qyd',
    password='your_password',
    database='qyd'
)
print('连接成功')
"
```

### 4. Redis 连接失败

**问题**：后端报错 "Error connecting to Redis"

**解决**：

```bash
# 检查 Redis 容器
docker compose ps redis

# 查看 Redis 日志
docker compose logs redis

# 测试 Redis 连接
docker compose exec redis redis-cli -a redis_fNmAxZ ping

# 重启 Redis
docker compose restart redis
```

### 5. 前端无法访问

**问题**：访问 http://localhost 无响应

**解决**：

```bash
# 检查前端容器
docker compose ps frontend

# 查看前端日志
docker compose logs frontend

# 检查端口映射
docker port qyd-frontend

# 测试容器内部
docker compose exec frontend wget -O- http://localhost
```

## 📊 性能优化

### 1. 调整资源限制

编辑 `docker-compose.yml`：

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

### 2. 调整队列配置

编辑 `.env`：

```env
# 高性能配置
REDIS_QUEUE_BATCH_SIZE=500
REDIS_QUEUE_NUM_WORKERS=12
```

重启服务：

```bash
docker compose restart queue-worker
```

### 3. 扩展队列 Worker

```bash
# 启动 3 个队列 Worker 实例
docker compose up -d --scale queue-worker=3

# 查看状态
docker compose ps
```

## 🔒 安全建议

1. ✅ 修改默认管理员密码
2. ✅ 使用强密码作为 JWT_SECRET_KEY
3. ✅ 不要暴露 Redis 端口到公网
4. ✅ 配置防火墙规则
5. ✅ 使用 HTTPS（配置 SSL 证书）
6. ✅ 定期更新镜像
7. ✅ 定期备份数据
8. ✅ 限制容器资源使用
9. ✅ 监控容器日志
10. ✅ 使用 Docker secrets 管理敏感信息

## 📚 相关文档

- [完整 Docker 部署指南](DOCKER_DEPLOY_WITH_REDIS.md)
- [部署架构说明](docs/deployment/DEPLOYMENT_ARCHITECTURE.md)
- [前端部署详解](docs/deployment/FRONTEND_DEPLOYMENT.md)

---

**最后更新**: 2026-01-26  
**版本**: v1.3.1
