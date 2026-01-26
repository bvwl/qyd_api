# Docker 部署指南（包含 Redis 容器）

本指南说明如何使用 Docker Compose 部署完整的应用栈，包括 Redis 容器。

## 📋 架构说明

```
┌─────────────────────────────────────────────────────────┐
│                      Docker 容器                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Frontend │  │Backend   │  │  Queue   │  │ Redis  │ │
│  │ (Nginx)  │  │   API    │  │  Worker  │  │  7.0   │ │
│  │ Port: 80 │  │Port: 6080│  │          │  │Port:   │ │
│  │          │  │          │  │          │  │ 6379   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───┬────┘ │
│       │             │              │             │       │
│       └─────────────┴──────────────┴─────────────┘       │
│                            │                             │
└────────────────────────────┼─────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  MySQL (外部)   │
                    │  主从分离架构    │
                    └─────────────────┘
```

### 服务说明

| 服务 | 说明 | 部署位置 | 端口 |
|------|------|---------|------|
| **MySQL** | 数据库（主从） | 外部服务器 | 3306 |
| **Redis** | 缓存/队列 | Docker 容器 | 6379 |
| **Frontend** | 前端应用 | Docker 容器 | 80 |
| **Backend API** | 后端 API | Docker 容器 | 6080 |
| **Queue Worker** | 队列处理 | Docker 容器 | - |

## 🚀 快速部署

### 1. 配置环境变量

```bash
# 复制配置文件
cp .env.docker .env

# 编辑配置
vim .env
```

**必须配置的参数**：

```env
# MySQL 主库（外部服务器，用于写操作）
DB_HOST=192.168.1.100        # MySQL 主库 IP
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_mysql_password
DB_NAME=qyd

# 是否启用读写分离（1=启用, 0=禁用）
DB_READ_WRITE_SPLIT=1

# MySQL 从库1（外部服务器，用于读操作）
DB_SLAVE1_HOST=192.168.1.101
DB_SLAVE1_PORT=3306
DB_SLAVE1_USER=qyd                    # 从库账号（可与主库不同）
DB_SLAVE1_PASSWORD=your_slave1_password  # 从库密码（可与主库不同）
DB_SLAVE1_NAME=qyd

# MySQL 从库2（外部服务器，用于读操作）
DB_SLAVE2_HOST=192.168.1.102
DB_SLAVE2_PORT=3306
DB_SLAVE2_USER=qyd                    # 从库账号（可与主库不同）
DB_SLAVE2_PASSWORD=your_slave2_password  # 从库密码（可与主库不同）
DB_SLAVE2_NAME=qyd

# Redis 密码（容器内 Redis）
REDIS_PASSWORD=redis_fNmAxZ

# JWT 密钥（至少32字符）
JWT_SECRET_KEY=your-secret-key-min-32-chars
```

**说明**：
- 如果从库账号密码与主库相同，可以不配置 `DB_SLAVE*_USER` 和 `DB_SLAVE*_PASSWORD`
- 如果只有一个从库，只配置 `DB_SLAVE1_*` 即可
- 如果不启用读写分离，设置 `DB_READ_WRITE_SPLIT=0`

### 2. 启动所有服务

```bash
# 构建并启动所有容器
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 3. 初始化数据库

```bash
# 首次部署需要初始化数据库
docker-compose exec backend-api python deploy_init.py
```

### 4. 验证部署

```bash
# 检查所有服务状态
docker-compose ps

# 应该看到：
# qyd-redis          running (healthy)
# qyd-queue-worker   running
# qyd-backend-api    running (healthy)
# qyd-frontend       running (healthy)

# 测试 Redis 连接
docker-compose exec redis redis-cli -a redis_fNmAxZ ping
# 应该返回：PONG

# 访问应用
# 前端：http://localhost
# 后端：http://localhost:6080
# API 文档：http://localhost:6080/docs
```

## 📝 详细配置说明

### Redis 容器配置

```yaml
redis:
  image: redis:7-alpine          # 使用 Redis 7 Alpine 版本
  ports:
    - "6379:6379"                # 暴露端口（可选）
  command: >
    redis-server
    --requirepass ${REDIS_PASSWORD}  # 密码保护
    --maxmemory 2gb                  # 最大内存 2GB
    --maxmemory-policy allkeys-lru   # 内存淘汰策略
    --appendonly yes                 # 开启 AOF 持久化
    --appendfsync everysec           # 每秒同步
  volumes:
    - redis-data:/data           # 数据持久化
```

**Redis 配置说明**：
- **密码保护**：通过 `--requirepass` 设置密码
- **内存限制**：最大使用 2GB 内存
- **淘汰策略**：内存满时使用 LRU 算法淘汰
- **持久化**：开启 AOF，每秒同步一次
- **数据卷**：数据持久化到 Docker 卷

### MySQL 主从配置

```env
# 主库（用于写操作）
DB_HOST=192.168.1.100
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=master_password
DB_NAME=qyd

# 启用读写分离
DB_READ_WRITE_SPLIT=1

# 从库1（用于读操作）
DB_SLAVE1_HOST=192.168.1.101
DB_SLAVE1_PORT=3306
DB_SLAVE1_USER=qyd_readonly        # 可以使用只读账号
DB_SLAVE1_PASSWORD=slave1_password
DB_SLAVE1_NAME=qyd

# 从库2（用于读操作）
DB_SLAVE2_HOST=192.168.1.102
DB_SLAVE2_PORT=3306
DB_SLAVE2_USER=qyd_readonly        # 可以使用只读账号
DB_SLAVE2_PASSWORD=slave2_password
DB_SLAVE2_NAME=qyd
```

**说明**：
- **主库**：用于所有写操作（INSERT, UPDATE, DELETE）
- **从库**：用于所有读操作（SELECT）
- **账号权限**：
  - 主库账号需要完整的读写权限
  - 从库账号可以只配置只读权限（推荐）
- **自动路由**：系统自动根据操作类型选择数据库
- **负载均衡**：多个从库会轮询使用

**从库只读账号创建**（推荐）：

```sql
-- 在从库上创建只读账号
CREATE USER 'qyd_readonly'@'%' IDENTIFIED BY 'slave_password';
GRANT SELECT ON qyd.* TO 'qyd_readonly'@'%';
FLUSH PRIVILEGES;
```

### 服务依赖关系

```yaml
# 启动顺序
redis → queue-worker → backend-api → frontend

# 依赖说明
queue-worker:
  depends_on:
    redis:
      condition: service_healthy  # 等待 Redis 健康检查通过

backend-api:
  depends_on:
    redis:
      condition: service_healthy
    queue-worker:
      condition: service_started
```

## 🔧 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose stop

# 重启所有服务
docker-compose restart

# 重启单个服务
docker-compose restart redis
docker-compose restart backend-api

# 删除所有服务（保留数据）
docker-compose down

# 删除所有服务和数据
docker-compose down -v
```

### Redis 管理

```bash
# 进入 Redis 容器
docker-compose exec redis sh

# 连接 Redis CLI
docker-compose exec redis redis-cli -a redis_fNmAxZ

# 查看 Redis 信息
docker-compose exec redis redis-cli -a redis_fNmAxZ INFO

# 查看内存使用
docker-compose exec redis redis-cli -a redis_fNmAxZ INFO memory

# 查看队列大小
docker-compose exec redis redis-cli -a redis_fNmAxZ ZCARD qyd:project_account_keys_zset

# 清空 Redis 数据（慎用！）
docker-compose exec redis redis-cli -a redis_fNmAxZ FLUSHALL
```

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看 Redis 日志
docker-compose logs -f redis

# 查看后端日志
docker-compose logs -f backend-api

# 查看队列 Worker 日志
docker-compose logs -f queue-worker
```

### 数据备份

```bash
# 备份 Redis 数据
docker-compose exec redis redis-cli -a redis_fNmAxZ SAVE
docker cp qyd-redis:/data/dump.rdb ./backup/redis-$(date +%Y%m%d).rdb

# 备份 MySQL 数据（在 MySQL 服务器上执行）
mysqldump -h 192.168.1.100 -u qyd -p qyd > backup-$(date +%Y%m%d).sql
```

### 数据恢复

```bash
# 恢复 Redis 数据
docker-compose stop redis
docker cp ./backup/redis-20260126.rdb qyd-redis:/data/dump.rdb
docker-compose start redis

# 恢复 MySQL 数据（在 MySQL 服务器上执行）
mysql -h 192.168.1.100 -u qyd -p qyd < backup-20260126.sql
```

## 🐛 故障排查

### 1. Redis 无法启动

**问题**：Redis 容器启动失败

**排查**：

```bash
# 查看 Redis 日志
docker-compose logs redis

# 检查端口占用
sudo lsof -i :6379

# 检查数据卷
docker volume ls | grep redis
docker volume inspect qyd_redis-data
```

**解决**：

```bash
# 如果端口被占用，停止占用进程或修改端口
# 修改 docker-compose.yml 中的端口映射
ports:
  - "6380:6379"  # 改为 6380

# 如果数据卷损坏，删除并重建
docker-compose down -v
docker-compose up -d
```

### 2. 后端无法连接 Redis

**问题**：后端报错 "Error connecting to Redis"

**排查**：

```bash
# 检查 Redis 是否运行
docker-compose ps redis

# 测试 Redis 连接
docker-compose exec backend-api python -c "
import redis
r = redis.Redis(host='redis', port=6379, password='redis_fNmAxZ')
print(r.ping())
"

# 检查网络
docker network inspect qyd_qyd-network
```

**解决**：

```bash
# 确认 .env 中的 Redis 密码正确
REDIS_PASSWORD=redis_fNmAxZ

# 重启服务
docker-compose restart backend-api queue-worker
```

### 3. 后端无法连接 MySQL

**问题**：后端报错 "Can't connect to MySQL server"

**排查**：

```bash
# 测试从容器连接 MySQL
docker-compose exec backend-api python -c "
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

# 检查 MySQL 服务器防火墙
# 在 MySQL 服务器上执行
sudo ufw status
sudo ufw allow from 172.0.0.0/8 to any port 3306
```

**解决**：

```bash
# 1. 确认 MySQL 绑定地址
# 编辑 /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0

# 2. 授权远程访问
mysql -u root -p
GRANT ALL PRIVILEGES ON qyd.* TO 'qyd'@'%' IDENTIFIED BY 'password';
FLUSH PRIVILEGES;

# 3. 重启 MySQL
sudo systemctl restart mysql
```

### 4. Redis 内存不足

**问题**：Redis 报错 "OOM command not allowed"

**排查**：

```bash
# 查看内存使用
docker-compose exec redis redis-cli -a redis_fNmAxZ INFO memory

# 查看配置
docker-compose exec redis redis-cli -a redis_fNmAxZ CONFIG GET maxmemory
```

**解决**：

```bash
# 方法1：增加内存限制（修改 docker-compose.yml）
command: >
  redis-server
  --maxmemory 4gb  # 改为 4GB

# 方法2：清理过期数据
docker-compose exec redis redis-cli -a redis_fNmAxZ FLUSHDB

# 重启 Redis
docker-compose restart redis
```

## 📊 性能优化

### Redis 性能优化

```yaml
# docker-compose.yml
redis:
  command: >
    redis-server
    --maxmemory 4gb                    # 增加内存
    --maxmemory-policy allkeys-lru     # LRU 淘汰
    --save ""                          # 禁用 RDB（如果不需要）
    --appendonly yes                   # 启用 AOF
    --appendfsync everysec             # 每秒同步
    --tcp-backlog 511                  # TCP 连接队列
    --timeout 0                        # 客户端超时
    --tcp-keepalive 300                # TCP keepalive
```

### 队列性能配置

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

### 扩展队列 Worker

```bash
# 启动多个队列 Worker 实例
docker-compose up -d --scale queue-worker=3

# 查看运行状态
docker-compose ps
```

## 🔒 安全建议

1. ✅ 修改 Redis 默认密码
2. ✅ 不要暴露 Redis 端口到公网
3. ✅ 使用强密码（至少16字符）
4. ✅ 定期备份 Redis 数据
5. ✅ 限制 Redis 内存使用
6. ✅ 配置防火墙规则
7. ✅ 使用 TLS 加密（生产环境）
8. ✅ 定期更新 Redis 镜像
9. ✅ 监控 Redis 性能
10. ✅ 设置合理的淘汰策略

## 📚 相关文档

- [Docker 完整部署指南](docs/deployment/DOCKER_DEPLOYMENT.md)
- [部署架构说明](docs/deployment/DEPLOYMENT_ARCHITECTURE.md)
- [前端部署详解](docs/deployment/FRONTEND_DEPLOYMENT.md)
- [性能优化指南](docs/performance/SCALE_TO_10K_GUIDE.md)

---

**最后更新**: 2026-01-26  
**版本**: v1.2.0
