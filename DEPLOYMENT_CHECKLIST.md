# 🚀 高并发部署快速检查清单

## 📋 部署前检查（5分钟）

### ✅ 1. 服务器资源
```bash
# 检查 CPU 核心数（建议 ≥ 8）
nproc

# 检查内存（建议 ≥ 16GB）
free -h

# 检查磁盘空间（建议 ≥ 100GB）
df -h

# 检查网络
ping -c 4 8.8.8.8
```

**最低要求**：
- [ ] CPU: 8 核心
- [ ] 内存: 16GB
- [ ] 磁盘: 100GB SSD
- [ ] 网络: 100Mbps

---

### ✅ 2. MySQL 主从集群
```bash
# 检查主库
mysql -h 192.168.13.6 -u root -p -e "SELECT VERSION();"

# 检查从库1
mysql -h 192.168.13.7 -u root -p -e "SHOW SLAVE STATUS\G" | grep Running

# 检查从库2
mysql -h 192.168.13.8 -u root -p -e "SHOW SLAVE STATUS\G" | grep Running
```

**必须确认**：
- [ ] 主库可连接
- [ ] 从库1: Slave_IO_Running: Yes
- [ ] 从库1: Slave_SQL_Running: Yes
- [ ] 从库2: Slave_IO_Running: Yes
- [ ] 从库2: Slave_SQL_Running: Yes

---

### ✅ 3. Docker 环境
```bash
# 检查 Docker
docker --version
docker ps

# 检查 Docker Compose
docker compose version
```

**必须确认**：
- [ ] Docker 已安装
- [ ] Docker 正在运行
- [ ] Docker Compose 已安装
- [ ] 当前用户有 Docker 权限

---

### ✅ 4. 环境变量配置
```bash
# 复制高并发配置
cp .env.high_concurrency .env

# 编辑配置
vim .env
```

**必须配置**：
- [ ] DB_HOST（MySQL 主库地址）
- [ ] DB_PASSWORD（MySQL 密码）
- [ ] DB_SLAVE1_HOST（从库1地址）
- [ ] DB_SLAVE2_HOST（从库2地址）
- [ ] REDIS_PASSWORD（Redis 密码）
- [ ] JWT_SECRET_KEY（JWT 密钥）
- [ ] CORS_ORIGINS（前端地址）

---

## 🚀 一键部署（10分钟）

### 方式 1: 使用自动化脚本（推荐）

```bash
# 1. 赋予执行权限
chmod +x deploy-high-concurrency.sh

# 2. 运行部署脚本
bash deploy-high-concurrency.sh
```

脚本会自动：
- ✅ 检查环境
- ✅ 检查 MySQL 主从
- ✅ 优化系统参数
- ✅ 构建镜像
- ✅ 初始化数据库
- ✅ 启动服务（5个后端 + 5个队列）
- ✅ 健康检查

---

### 方式 2: 手动部署

```bash
# 1. 拉取最新代码
git pull

# 2. 配置环境变量
cp .env.high_concurrency .env
vim .env

# 3. 构建镜像
docker compose build

# 4. 初始化数据库（首次部署）
docker compose up -d redis
sleep 10
docker compose run --rm backend-api python deploy_init.py

# 5. 启动服务（高并发模式）
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 6. 查看状态
docker compose ps
docker stats
```

---

## 🔍 部署后验证（5分钟）

### ✅ 1. 检查容器状态
```bash
# 查看所有容器
docker compose ps

# 应该看到：
# - backend-api: 5 个容器（Running）
# - queue-worker: 5 个容器（Running）
# - frontend: 1 个容器（Running）
# - redis: 1 个容器（Running）
```

**必须确认**：
- [ ] 所有容器状态为 "Up" 或 "Running"
- [ ] 没有容器频繁重启
- [ ] 健康检查通过（healthy）

---

### ✅ 2. 测试服务访问
```bash
# 测试前端
curl -I http://192.168.13.6/

# 测试后端 API
curl -I http://192.168.13.6:6080/docs

# 测试 Redis
docker compose exec redis redis-cli -a redis_fNmAxZ PING
```

**必须确认**：
- [ ] 前端返回 200 OK
- [ ] 后端返回 200 OK
- [ ] Redis 返回 PONG

---

### ✅ 3. 检查数据库连接
```bash
# 查看 MySQL 连接数
mysql -h 192.168.13.6 -u root -p -e "SHOW PROCESSLIST;" | wc -l

# 应该看到约 750 个连接（5容器 × 50 × 3）
```

**必须确认**：
- [ ] 主库连接数正常（约 250 个）
- [ ] 从库1连接数正常（约 250 个）
- [ ] 从库2连接数正常（约 250 个）
- [ ] 没有大量 Sleep 状态连接

---

### ✅ 4. 检查 Redis 状态
```bash
# 进入 Redis
docker compose exec redis redis-cli -a redis_fNmAxZ

# 查看信息
INFO stats
INFO clients
INFO memory

# 查看连接数
CLIENT LIST | wc -l

# 应该看到约 1000 个连接（5容器 × 200）
```

**必须确认**：
- [ ] Redis 连接数正常（约 1000 个）
- [ ] 内存使用正常（< 8GB）
- [ ] 没有大量阻塞命令

---

### ✅ 5. 查看日志
```bash
# 查看后端日志
docker compose logs backend-api --tail=100

# 查看队列日志
docker compose logs queue-worker --tail=100

# 查看 Redis 日志
docker compose logs redis --tail=100
```

**必须确认**：
- [ ] 没有 ERROR 级别日志
- [ ] 没有数据库连接失败
- [ ] 没有 Redis 连接失败
- [ ] 没有内存不足警告

---

## 📊 性能测试（5分钟）

### ✅ 1. 基础压力测试
```bash
# 安装测试工具
sudo apt install apache2-utils -y

# 测试 API 响应（1000并发，10000请求）
ab -n 10000 -c 1000 -k http://192.168.13.6:6080/docs

# 查看结果
# - Requests per second: 应该 > 5000
# - Time per request: 应该 < 200ms
# - Failed requests: 应该 = 0
```

**性能指标**：
- [ ] QPS > 5,000
- [ ] 平均响应时间 < 200ms
- [ ] 失败率 = 0%

---

### ✅ 2. 持续压力测试
```bash
# 安装 wrk
sudo apt install wrk -y

# 持续压测 60 秒（12线程，1000并发）
wrk -t12 -c1000 -d60s http://192.168.13.6:6080/docs

# 查看结果
# - Requests/sec: 应该 > 10000
# - Latency avg: 应该 < 100ms
```

**性能指标**：
- [ ] QPS > 10,000
- [ ] 平均延迟 < 100ms
- [ ] P99 延迟 < 500ms

---

### ✅ 3. 监控资源使用
```bash
# 查看容器资源
docker stats --no-stream

# 查看系统资源
top
free -h
df -h
```

**资源使用**：
- [ ] CPU 使用率 < 80%
- [ ] 内存使用 < 16GB
- [ ] 磁盘使用 < 80%
- [ ] 网络带宽充足

---

## 🔧 常见问题处理

### ❌ 问题 1: 容器启动失败

**症状**：容器状态为 "Exited" 或频繁重启

**排查**：
```bash
# 查看容器日志
docker compose logs backend-api --tail=200

# 常见原因：
# 1. 数据库连接失败 → 检查 .env 配置
# 2. Redis 连接失败 → 检查 Redis 容器
# 3. 端口被占用 → 检查端口占用
# 4. 内存不足 → 增加服务器内存
```

**解决**：
```bash
# 重启服务
docker compose restart backend-api

# 如果还是失败，重新部署
docker compose down
docker compose up -d --scale backend-api=5 --scale queue-worker=5
```

---

### ❌ 问题 2: 数据库连接耗尽

**症状**：日志显示 "Too many connections"

**排查**：
```bash
# 查看 MySQL 连接数
mysql -h 192.168.13.6 -u root -p -e "SHOW PROCESSLIST;" | wc -l

# 查看最大连接数
mysql -h 192.168.13.6 -u root -p -e "SHOW VARIABLES LIKE 'max_connections';"
```

**解决**：
```bash
# 临时增加最大连接数
mysql -h 192.168.13.6 -u root -p -e "SET GLOBAL max_connections = 2000;"

# 永久修改：编辑 /etc/mysql/mysql.conf.d/mysqld.cnf
max_connections = 2000

# 重启 MySQL
sudo systemctl restart mysql
```

---

### ❌ 问题 3: Redis 内存不足

**症状**：日志显示 "OOM command not allowed"

**排查**：
```bash
# 查看 Redis 内存使用
docker compose exec redis redis-cli -a redis_fNmAxZ INFO memory
```

**解决**：
```bash
# 编辑 docker-compose.yml，增加 Redis 内存
--maxmemory 16gb

# 重启 Redis
docker compose restart redis
```

---

### ❌ 问题 4: 响应时间过长

**症状**：API 响应时间 > 1秒

**排查**：
```bash
# 查看慢查询
tail -f /var/log/mysql/slow.log

# 查看 Redis 慢查询
docker compose exec redis redis-cli -a redis_fNmAxZ SLOWLOG GET 10

# 查看容器资源
docker stats
```

**解决**：
```bash
# 1. 优化数据库查询（添加索引）
# 2. 增加容器数量
docker compose up -d --scale backend-api=10 --scale queue-worker=10

# 3. 增加数据库连接池
# 编辑 .env: DB_MAXSIZE=100
```

---

## 📈 性能优化建议

### 🔥 如果 QPS < 10,000

1. **增加容器数量**
   ```bash
   docker compose up -d --scale backend-api=10 --scale queue-worker=10
   ```

2. **增加数据库连接池**
   ```env
   DB_MAXSIZE=100
   DB_SLAVE1_MAXSIZE=100
   DB_SLAVE2_MAXSIZE=100
   ```

3. **增加 Redis 连接池**
   ```env
   REDIS_MAX_CONNECTIONS=500
   ```

---

### 🔥 如果 QPS < 50,000

1. **使用 Nginx 负载均衡**
   - 参考 `HIGH_CONCURRENCY_DEPLOYMENT.md` 第 6 步

2. **优化数据库**
   - 添加索引
   - 优化慢查询
   - 增加 innodb_buffer_pool_size

3. **使用 Redis 集群**
   - 部署 Redis Cluster
   - 使用 Redis Sentinel

---

## 📚 相关文档

- [高并发部署完整指南](HIGH_CONCURRENCY_DEPLOYMENT.md)
- [Docker 快速部署](DOCKER_QUICK_START.md)
- [性能优化指南](docs/performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md)

---

## 🎯 部署成功标准

- ✅ 所有容器正常运行
- ✅ 前端和后端可访问
- ✅ MySQL 主从同步正常
- ✅ Redis 连接正常
- ✅ QPS > 10,000
- ✅ 平均响应时间 < 100ms
- ✅ CPU 使用率 < 80%
- ✅ 内存使用 < 16GB
- ✅ 无错误日志

---

**最后更新**: 2026-01-26  
**适用版本**: v1.3.1
