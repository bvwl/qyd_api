# Redis Docker 部署说明

## 📋 概述

后端部署现在包含 Redis 容器，无需单独安装 Redis 服务。

## 🏗️ 架构

```
后端服务器
┌─────────────────────────────────────┐
│  Docker Compose                     │
├─────────────────────────────────────┤
│                                     │
│  ┌───────────────┐                 │
│  │  Backend API  │                 │
│  │  Port: 6080   │                 │
│  └───────┬───────┘                 │
│          │                         │
│  ┌───────▼───────┐                 │
│  │ Queue Worker  │                 │
│  └───────┬───────┘                 │
│          │                         │
│  ┌───────▼───────┐                 │
│  │     Redis     │                 │
│  │  Port: 6379   │                 │
│  │  (容器内部)    │                 │
│  └───────────────┘                 │
│                                     │
└──────────────┬──────────────────────┘
               │
        ┌──────▼──────┐
        │    MySQL    │
        │  (外部服务)  │
        └─────────────┘
```

## 🚀 部署方式

### 方式一：使用部署脚本（推荐）

```bash
# 1. 配置环境变量
cp .env.backend .env
vim .env  # 修改配置

# 2. 一键部署
bash deploy-backend.sh
```

### 方式二：手动部署

```bash
# 1. 配置环境变量
cp .env.backend .env
vim .env

# 2. 构建镜像
docker compose -f docker-compose.backend.yml build

# 3. 启动服务（Redis 会自动启动）
docker compose -f docker-compose.backend.yml up -d

# 4. 查看状态
docker compose -f docker-compose.backend.yml ps
```

## ⚙️ Redis 配置

### 环境变量配置

编辑 `.env` 文件：

```env
# Redis 配置
REDIS_ENABLED=1
REDIS_PASSWORD=redis_fNmAxZ  # 建议修改为强密码
REDIS_PORT=6379               # 如果宿主机端口被占用可修改
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
```

### Redis 容器配置

在 `docker-compose.backend.yml` 中的配置：

```yaml
redis:
  image: redis:7-alpine
  container_name: qyd-redis
  restart: unless-stopped
  ports:
    - "${REDIS_PORT:-6379}:6379"
  command: >
    redis-server
    --requirepass ${REDIS_PASSWORD:-redis_password}
    --maxmemory 2gb
    --maxmemory-policy allkeys-lru
    --appendonly yes
    --appendfsync everysec
  volumes:
    - redis-data:/data
```

### 配置说明

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `requirepass` | Redis 密码 | 从 .env 读取 |
| `maxmemory` | 最大内存 | 2GB |
| `maxmemory-policy` | 内存淘汰策略 | allkeys-lru |
| `appendonly` | 启用 AOF 持久化 | yes |
| `appendfsync` | AOF 同步策略 | everysec |

## 🔧 常用命令

### 查看 Redis 状态

```bash
# 查看容器状态
docker compose -f docker-compose.backend.yml ps redis

# 查看 Redis 日志
docker compose -f docker-compose.backend.yml logs -f redis

# 进入 Redis 容器
docker compose -f docker-compose.backend.yml exec redis sh
```

### 连接 Redis

```bash
# 从宿主机连接
redis-cli -h localhost -p 6379 -a redis_fNmAxZ

# 从容器内连接
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ

# 测试连接
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ ping
# 应该返回: PONG
```

### Redis 管理命令

```bash
# 查看 Redis 信息
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ info

# 查看键数量
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ dbsize

# 查看内存使用
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ info memory

# 清空数据库（慎用！）
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ flushdb
```

## 📊 数据持久化

### 持久化方式

Redis 使用两种持久化方式：

1. **AOF (Append Only File)**
   - 记录每个写操作
   - 每秒同步一次（`appendfsync everysec`）
   - 数据更安全，但文件较大

2. **RDB (Redis Database)**
   - 定期快照
   - 文件较小，恢复快
   - 可能丢失最后一次快照后的数据

### 数据存储位置

数据存储在 Docker 卷中：

```bash
# 查看卷信息
docker volume ls | grep redis

# 查看卷详情
docker volume inspect qyd_api_redis-data

# 备份数据
docker run --rm -v qyd_api_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup-$(date +%Y%m%d).tar.gz /data
```

### 数据恢复

```bash
# 停止服务
docker compose -f docker-compose.backend.yml stop redis

# 恢复数据
docker run --rm -v qyd_api_redis-data:/data -v $(pwd):/backup alpine tar xzf /backup/redis-backup-20260127.tar.gz -C /

# 启动服务
docker compose -f docker-compose.backend.yml start redis
```

## 🔒 安全配置

### 1. 修改默认密码

```env
# .env 文件
REDIS_PASSWORD=your_strong_password_here
```

### 2. 限制访问

默认配置只允许容器内部访问。如果需要外部访问：

```yaml
# docker-compose.backend.yml
redis:
  ports:
    - "127.0.0.1:6379:6379"  # 只允许本地访问
    # - "6379:6379"          # 允许所有访问（不推荐）
```

### 3. 禁用危险命令

修改 `docker-compose.backend.yml`：

```yaml
redis:
  command: >
    redis-server
    --requirepass ${REDIS_PASSWORD}
    --rename-command FLUSHDB ""
    --rename-command FLUSHALL ""
    --rename-command CONFIG ""
```

## 📈 性能优化

### 1. 调整最大内存

```yaml
# docker-compose.backend.yml
redis:
  command: >
    redis-server
    --maxmemory 4gb  # 根据服务器内存调整
```

### 2. 调整连接数

```env
# .env 文件
REDIS_MAX_CONNECTIONS=100  # 根据并发量调整
```

### 3. 监控性能

```bash
# 实时监控
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ --stat

# 查看慢查询
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ slowlog get 10
```

## 🐛 故障排查

### 问题1：Redis 容器无法启动

**排查步骤**：

```bash
# 查看日志
docker compose -f docker-compose.backend.yml logs redis

# 检查端口占用
sudo lsof -i :6379

# 检查配置
docker compose -f docker-compose.backend.yml config
```

**解决方案**：

1. 如果端口被占用，修改 `.env` 中的 `REDIS_PORT`
2. 检查 Redis 密码配置是否正确

### 问题2：后端无法连接 Redis

**排查步骤**：

```bash
# 检查 Redis 是否运行
docker compose -f docker-compose.backend.yml ps redis

# 测试连接
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ ping

# 查看后端日志
docker compose -f docker-compose.backend.yml logs backend-api | grep -i redis
```

**解决方案**：

1. 确保 Redis 容器正常运行
2. 检查 `.env` 中的 `REDIS_PASSWORD` 是否正确
3. 重启后端服务

### 问题3：Redis 内存不足

**错误信息**: "OOM command not allowed"

**解决方案**：

```yaml
# 增加最大内存
redis:
  command: >
    redis-server
    --maxmemory 4gb
```

### 问题4：数据丢失

**原因**: AOF 文件损坏或未正确持久化

**解决方案**：

```bash
# 检查 AOF 文件
docker compose -f docker-compose.backend.yml exec redis redis-check-aof /data/appendonly.aof

# 修复 AOF 文件
docker compose -f docker-compose.backend.yml exec redis redis-check-aof --fix /data/appendonly.aof

# 重启 Redis
docker compose -f docker-compose.backend.yml restart redis
```

## 🔄 升级和维护

### 升级 Redis 版本

```bash
# 1. 备份数据
docker run --rm -v qyd_api_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz /data

# 2. 修改镜像版本
# 编辑 docker-compose.backend.yml
# image: redis:7-alpine -> redis:7.2-alpine

# 3. 重新构建
docker compose -f docker-compose.backend.yml pull redis
docker compose -f docker-compose.backend.yml up -d redis
```

### 定期维护

```bash
# 1. 查看内存使用
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ info memory

# 2. 清理过期键
docker compose -f docker-compose.backend.yml exec redis redis-cli -a redis_fNmAxZ --scan --pattern "*" | wc -l

# 3. 备份数据（建议每天）
docker run --rm -v qyd_api_redis-data:/data -v /backup:/backup alpine tar czf /backup/redis-$(date +%Y%m%d).tar.gz /data
```

## 📚 相关文档

- [后端部署指南](SEPARATE_DEPLOYMENT_GUIDE.md)
- [外部 Redis 使用指南](EXTERNAL_REDIS_GUIDE.md)（如果需要使用外部 Redis）
- [部署文档索引](DEPLOYMENT_README.md)

## 💡 提示

1. ✅ Redis 数据会持久化到 Docker 卷中
2. ✅ 容器重启不会丢失数据
3. ✅ 建议定期备份 Redis 数据
4. ✅ 生产环境建议修改默认密码
5. ✅ 监控 Redis 内存使用情况

---

**最后更新**: 2026-01-27  
**版本**: v2.0.0
