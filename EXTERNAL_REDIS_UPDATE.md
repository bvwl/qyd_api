# 外部 Redis 配置更新说明

## 📝 更新内容

已将部署配置修改为使用外部 Redis 服务器，而不是在 Docker 中启动新的 Redis 容器。

## 🔄 修改的文件

### 1. docker-compose.backend.yml

**修改内容**:
- ✅ 移除了 Redis 服务定义
- ✅ 修改 Redis 连接配置为使用外部服务器
- ✅ 移除了 Redis 容器的依赖关系
- ✅ 移除了 Redis 数据卷

**关键变化**:

```yaml
# 之前: 使用容器内 Redis
- REDIS_HOST=redis

# 现在: 使用外部 Redis
- REDIS_HOST=${REDIS_HOST:-192.168.1.20}
- REDIS_PORT=${REDIS_PORT:-6379}
```

### 2. .env.backend

**修改内容**:
- ✅ 添加了 REDIS_HOST 配置项
- ✅ 添加了 REDIS_PORT 配置项
- ✅ 更新了注释说明

**新配置**:

```env
# Redis 配置（外部 Redis 服务器）
REDIS_HOST=192.168.1.20
REDIS_PORT=6379
REDIS_PASSWORD=redis_fNmAxZ
```

### 3. deploy-backend.sh

**修改内容**:
- ✅ 更新了配置提示信息
- ✅ 添加了 REDIS_HOST 配置提示

### 4. deploy-backend-native.sh

**修改内容**:
- ✅ 移除了 Redis 安装步骤
- ✅ 移除了 Redis 配置步骤
- ✅ 更新了步骤编号（从 8 步改为 7 步）
- ✅ 移除了 Systemd 服务中的 redis.service 依赖

### 5. 新增文档

**EXTERNAL_REDIS_GUIDE.md**:
- ✅ 详细的外部 Redis 使用指南
- ✅ Redis 服务器配置说明
- ✅ 防火墙配置指南
- ✅ 连接测试方法
- ✅ 故障排查步骤
- ✅ 性能优化建议
- ✅ 安全配置建议

## 🚀 使用方法

### 快速开始

#### 1. 确保 Redis 服务器正常运行

```bash
# 测试 Redis 连接
redis-cli -h 192.168.1.20 -p 6379 -a redis_fNmAxZ ping

# 应该返回: PONG
```

#### 2. 配置环境变量

编辑 `.env.backend` 文件:

```env
# Redis 服务器地址（修改为你的实际地址）
REDIS_HOST=192.168.1.20
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
```

#### 3. 部署后端

```bash
# 复制配置文件
cp .env.backend .env

# 编辑配置
vim .env

# 一键部署
bash deploy-backend.sh
```

## ✅ 验证部署

### 1. 检查服务状态

```bash
# Docker 部署
docker-compose -f docker-compose.backend.yml ps

# 应该看到:
# - backend-api: running
# - queue-worker: running
# 注意: 不再有 redis 容器
```

### 2. 检查 Redis 连接

```bash
# 查看后端日志
docker-compose -f docker-compose.backend.yml logs -f backend-api

# 应该看到类似的日志:
# INFO: Redis connected successfully
# INFO: Redis version: 7.0.x
```

### 3. 测试 API

```bash
# 访问 API 文档
curl http://192.168.1.20:6080/docs

# 测试健康检查
curl http://192.168.1.20:6080/health
```

## 🔧 Redis 服务器配置

### 必需配置

编辑 `/etc/redis/redis.conf`:

```conf
# 1. 绑定地址（允许后端服务器访问）
bind 0.0.0.0

# 2. 设置密码
requirepass redis_fNmAxZ

# 3. 最大内存
maxmemory 2gb
maxmemory-policy allkeys-lru

# 4. 持久化
appendonly yes
appendfsync everysec
```

重启 Redis:

```bash
sudo systemctl restart redis
sudo systemctl enable redis
```

### 防火墙配置

```bash
# 如果 Redis 和后端在同一服务器，无需配置

# 如果在不同服务器，允许后端访问
sudo ufw allow from 192.168.1.20 to any port 6379
```

## 🐛 常见问题

### 1. 无法连接 Redis

**错误信息**: "Error connecting to Redis"

**解决方案**:

```bash
# 1. 检查 Redis 是否运行
sudo systemctl status redis

# 2. 测试连接
redis-cli -h 192.168.1.20 -p 6379 -a redis_fNmAxZ ping

# 3. 检查防火墙
sudo ufw status

# 4. 检查绑定地址
grep "^bind" /etc/redis/redis.conf
```

### 2. Redis 密码错误

**错误信息**: "NOAUTH Authentication required"

**解决方案**:

```bash
# 检查 Redis 密码配置
grep "^requirepass" /etc/redis/redis.conf

# 确保 .env 文件中的密码一致
grep "REDIS_PASSWORD" .env
```

### 3. 端口被占用

**错误信息**: "Address already in use"

**解决方案**:

```bash
# 查看占用端口的进程
sudo lsof -i :6379

# 如果是旧的 Redis 容器，停止它
docker stop qyd-redis
docker rm qyd-redis
```

## 📊 性能对比

### 使用外部 Redis vs Docker Redis

| 特性 | 外部 Redis | Docker Redis |
|------|-----------|-------------|
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 资源利用 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 管理复杂度 | ⭐⭐⭐ | ⭐⭐ |
| 共享能力 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 持久化 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 优势

- ✅ **性能更好**: 无容器网络开销
- ✅ **资源共享**: 可以被多个应用使用
- ✅ **统一管理**: 集中管理 Redis 配置
- ✅ **持久化更可靠**: 直接写入宿主机磁盘
- ✅ **监控更方便**: 使用系统级监控工具

## 📚 相关文档

- [外部 Redis 使用指南](EXTERNAL_REDIS_GUIDE.md) - 详细配置和故障排查
- [前后端分离部署指南](SEPARATE_DEPLOYMENT_GUIDE.md) - 完整部署流程
- [快速参考](SEPARATE_DEPLOYMENT_QUICK_REF.md) - 快速命令参考

## 🔄 回滚到 Docker Redis

如果需要回滚到使用 Docker Redis，可以：

1. 恢复 `docker-compose.backend.yml` 中的 Redis 服务定义
2. 修改环境变量 `REDIS_HOST=redis`
3. 重新部署

或者使用原来的 `docker-compose.yml` 进行一体化部署。

---

**更新时间**: 2026-01-27  
**版本**: v2.0.0
