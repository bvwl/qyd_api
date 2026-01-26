# 高并发部署完整清单

## 📋 部署前检查清单

### 1. 服务器资源要求

**最低配置（支持 10000+ QPS）**：
- ✅ CPU: 8 核心
- ✅ 内存: 16GB
- ✅ 磁盘: 100GB SSD
- ✅ 网络: 100Mbps

**推荐配置（支持 50000+ QPS）**：
- ✅ CPU: 16 核心
- ✅ 内存: 32GB
- ✅ 磁盘: 500GB SSD
- ✅ 网络: 1Gbps

### 2. MySQL 主从集群检查

```bash
# 检查主库状态
mysql -h 192.168.13.6 -u root -p -e "SHOW MASTER STATUS;"

# 检查从库1状态
mysql -h 192.168.13.7 -u root -p -e "SHOW SLAVE STATUS\G"

# 检查从库2状态
mysql -h 192.168.13.8 -u root -p -e "SHOW SLAVE STATUS\G"

# 确认：
# ✅ Slave_IO_Running: Yes
# ✅ Slave_SQL_Running: Yes
# ✅ Seconds_Behind_Master: 0 或很小的数字
```

### 3. MySQL 性能优化

编辑 MySQL 配置文件 `/etc/mysql/mysql.conf.d/mysqld.cnf`：

```ini
[mysqld]
# 连接配置
max_connections = 1000
max_connect_errors = 100000
wait_timeout = 600
interactive_timeout = 600

# InnoDB 配置（根据内存调整）
innodb_buffer_pool_size = 8G  # 服务器内存的 50-70%
innodb_log_file_size = 512M
innodb_log_buffer_size = 64M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# 查询缓存
query_cache_type = 1
query_cache_size = 256M
query_cache_limit = 2M

# 临时表
tmp_table_size = 256M
max_heap_table_size = 256M

# 线程缓存
thread_cache_size = 100

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

重启 MySQL：
```bash
sudo systemctl restart mysql
```

### 4. Redis 容器资源限制

编辑 `docker-compose.yml`，调整 Redis 配置：

```yaml
redis:
  image: redis:7-alpine
  container_name: qyd-redis
  restart: unless-stopped
  ports:
    - "6379:6379"
  command: >
    redis-server
    --requirepass ${REDIS_PASSWORD:-redis_password}
    --maxmemory 8gb
    --maxmemory-policy allkeys-lru
    --appendonly yes
    --appendfsync everysec
    --maxclients 10000
    --tcp-backlog 511
    --timeout 300
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 10G
      reservations:
        cpus: '2'
        memory: 8G
```

### 5. 系统内核参数优化

```bash
# 编辑系统参数
sudo vim /etc/sysctl.conf

# 添加以下内容：
# 网络优化
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 10000 65000

# 文件描述符
fs.file-max = 1000000
fs.nr_open = 1000000

# 应用配置
sudo sysctl -p
```

### 6. Docker 资源限制

```bash
# 编辑 Docker 配置
sudo vim /etc/docker/daemon.json

# 添加：
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "5"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}

# 重启 Docker
sudo systemctl restart docker
```

---

## 🚀 高并发环境变量配置

创建 `.env` 文件：

```bash
# ==========================================
# 高并发部署配置
# ==========================================

# ==========================================
# 数据库配置（外部 MySQL 主从）
# ==========================================
DB_HOST=192.168.13.6
DB_PORT=3306
DB_USER=root
DB_PASSWORD=zhiyu666
DB_NAME=qyd

# 高并发连接池配置（每个容器）
DB_MINSIZE=10
DB_MAXSIZE=50

# ==========================================
# MySQL 读写分离配置
# ==========================================
DB_READ_WRITE_SPLIT=1

# 从库1配置
DB_SLAVE1_HOST=192.168.13.7
DB_SLAVE1_PORT=3306
DB_SLAVE1_USER=root
DB_SLAVE1_PASSWORD=zhiyu666
DB_SLAVE1_NAME=qyd
DB_SLAVE1_MINSIZE=10
DB_SLAVE1_MAXSIZE=50

# 从库2配置
DB_SLAVE2_HOST=192.168.13.8
DB_SLAVE2_PORT=3306
DB_SLAVE2_USER=root
DB_SLAVE2_PASSWORD=zhiyu666
DB_SLAVE2_NAME=qyd
DB_SLAVE2_MINSIZE=10
DB_SLAVE2_MAXSIZE=50

# ==========================================
# Redis 配置（Docker 容器内）
# ==========================================
REDIS_ENABLED=1
REDIS_PASSWORD=redis_fNmAxZ
REDIS_DB=0
REDIS_MAX_CONNECTIONS=200

# ==========================================
# Redis 队列配置（超高性能）
# ==========================================
REDIS_QUEUE_BATCH_SIZE=1000
REDIS_QUEUE_NUM_WORKERS=16
REDIS_QUEUE_CACHE_EXPIRE=3600

# ==========================================
# JWT 配置
# ==========================================
JWT_SECRET_KEY=ZFi/3*B-jK5b6l6hJm1n3@gZ7FqW8KoJM-NHs0jMCE3zvxI04e7rLDiwuiMpY$m%
JWT_ALGORITHM=HS256
JWT_EXPIRE_TIME=86400

# ==========================================
# 服务配置
# ==========================================
DEBUG=0
WORKERS=1

# ==========================================
# CORS 配置
# ==========================================
CORS_ORIGINS=http://192.168.13.6,http://192.168.13.6:80

# ==========================================
# 前端配置
# ==========================================
VITE_API_BASE_URL=http://192.168.13.6:6080

# ==========================================
# 日志配置
# ==========================================
LOG_LEVEL=WARNING
LOG_RETENTION_DAYS=30
```

---

## 📦 部署步骤

### 步骤 1: 拉取最新代码

```bash
cd /opt/zy/qyd_api
git pull
```

### 步骤 2: 配置环境变量

```bash
# 复制上面的高并发配置
vim .env
```

### 步骤 3: 构建镜像

```bash
# 使用快速部署脚本（自动配置国内镜像）
chmod +x docker-deploy-fast.sh
bash docker-deploy-fast.sh
```

或手动构建：

```bash
# 清理旧镜像
docker compose down -v
docker system prune -af

# 构建新镜像
docker compose build --no-cache
```

### 步骤 4: 初始化数据库（首次部署）

```bash
# 先启动 Redis
docker compose up -d redis

# 等待 Redis 启动
sleep 10

# 初始化数据库
docker compose run --rm backend-api python deploy_init.py
```

### 步骤 5: 启动服务（高并发模式）

```bash
# 启动多个容器实例
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 查看状态
docker compose ps
```

**容器实例说明**：
- `backend-api=5`: 5 个后端 API 容器（处理 HTTP 请求）
- `queue-worker=5`: 5 个队列 Worker 容器（处理异步任务）
- `frontend=1`: 1 个前端容器（Nginx）
- `redis=1`: 1 个 Redis 容器

**总处理能力**：
- HTTP 并发: 5 个容器并行处理
- 队列处理: 5 × 16 = 80 个 Worker 并行
- 数据库连接: 5 × 50 × 3 = 750 个连接
- Redis 连接: 5 × 200 = 1000 个连接

### 步骤 6: 配置 Nginx 负载均衡（可选）

如果需要更高性能，在前面加一层 Nginx 负载均衡：

```bash
# 安装 Nginx
sudo apt install nginx -y

# 配置负载均衡
sudo vim /etc/nginx/sites-available/qyd
```

添加配置：

```nginx
upstream backend_api {
    least_conn;  # 最少连接负载均衡
    server 127.0.0.1:6080 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:6081 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:6082 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:6083 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:6084 max_fails=3 fail_timeout=30s;
    keepalive 100;
}

server {
    listen 80;
    server_name 192.168.13.6;
    
    # 前端静态文件
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # 后端 API
    location /api/ {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # API 文档
    location /docs {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/qyd /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

修改 `docker-compose.yml`，映射多个端口：

```yaml
backend-api:
  ports:
    - "6080-6084:6080"  # 映射 5 个端口
```

---

## 🔍 监控和验证

### 1. 查看容器状态

```bash
# 查看所有容器
docker compose ps

# 查看资源使用
docker stats

# 查看日志
docker compose logs -f --tail=100
```

### 2. 测试 API 响应

```bash
# 测试后端 API
curl http://192.168.13.6:6080/docs

# 测试前端
curl http://192.168.13.6/

# 压力测试（使用 ab 工具）
sudo apt install apache2-utils -y
ab -n 10000 -c 100 http://192.168.13.6:6080/docs
```

### 3. 监控数据库连接

```bash
# 查看 MySQL 连接数
mysql -h 192.168.13.6 -u root -p -e "SHOW PROCESSLIST;" | wc -l

# 查看详细连接信息
mysql -h 192.168.13.6 -u root -p -e "SHOW PROCESSLIST;"

# 查看连接状态统计
mysql -h 192.168.13.6 -u root -p -e "SHOW STATUS LIKE 'Threads%';"
```

### 4. 监控 Redis 状态

```bash
# 进入 Redis 容器
docker compose exec redis redis-cli -a redis_fNmAxZ

# 查看信息
INFO stats
INFO clients
INFO memory

# 查看连接数
CLIENT LIST | wc -l

# 查看队列长度
LLEN project_account_queue
```

### 5. 监控系统资源

```bash
# CPU 使用率
top

# 内存使用
free -h

# 磁盘使用
df -h

# 网络连接
netstat -an | grep ESTABLISHED | wc -l

# 文件描述符
lsof | wc -l
```

---

## 📊 性能基准测试

### 预期性能指标

**5 个后端容器 + 5 个队列 Worker**：

| 指标 | 预期值 |
|------|--------|
| HTTP QPS | 20,000 - 50,000 |
| 队列处理速度 | 50,000+ 条/秒 |
| 平均响应时间 | < 50ms |
| P99 响应时间 | < 200ms |
| 数据库连接数 | 750 个 |
| Redis 连接数 | 1,000 个 |
| CPU 使用率 | 60-80% |
| 内存使用 | 12-16GB |

### 压力测试命令

```bash
# 安装压测工具
sudo apt install apache2-utils wrk -y

# 使用 ab 测试
ab -n 100000 -c 1000 -k http://192.168.13.6:6080/api/v1/health

# 使用 wrk 测试（更强大）
wrk -t12 -c1000 -d60s http://192.168.13.6:6080/api/v1/health
```

---

## 🔧 动态扩展

### 根据负载动态调整

```bash
# 查看当前容器数量
docker compose ps

# 扩展到 10 个后端容器
docker compose up -d --scale backend-api=10 --scale queue-worker=10

# 缩减到 3 个后端容器
docker compose up -d --scale backend-api=3 --scale queue-worker=3

# 重启特定服务
docker compose restart backend-api
docker compose restart queue-worker
```

### 滚动更新（零停机）

```bash
# 1. 拉取最新代码
git pull

# 2. 构建新镜像
docker compose build

# 3. 逐个重启容器（保持服务可用）
for i in {1..5}; do
    docker compose up -d --scale backend-api=5 --no-recreate
    sleep 10
done
```

---

## 🐛 故障排查

### 1. 容器频繁重启

```bash
# 查看容器日志
docker compose logs backend-api --tail=500

# 常见原因：
# - 数据库连接失败
# - Redis 连接失败
# - 内存不足
# - 端口冲突
```

### 2. 数据库连接耗尽

```bash
# 查看 MySQL 最大连接数
mysql -h 192.168.13.6 -u root -p -e "SHOW VARIABLES LIKE 'max_connections';"

# 增加最大连接数
mysql -h 192.168.13.6 -u root -p -e "SET GLOBAL max_connections = 2000;"

# 永久修改：编辑 /etc/mysql/mysql.conf.d/mysqld.cnf
max_connections = 2000
```

### 3. Redis 内存不足

```bash
# 查看 Redis 内存使用
docker compose exec redis redis-cli -a redis_fNmAxZ INFO memory

# 清理过期键
docker compose exec redis redis-cli -a redis_fNmAxZ --scan --pattern "*" | xargs redis-cli -a redis_fNmAxZ DEL

# 增加 Redis 内存限制（编辑 docker-compose.yml）
--maxmemory 16gb
```

### 4. 响应时间过长

```bash
# 查看慢查询日志
tail -f /var/log/mysql/slow.log

# 分析 Redis 慢查询
docker compose exec redis redis-cli -a redis_fNmAxZ SLOWLOG GET 10

# 查看容器资源限制
docker inspect qyd-backend-api | grep -A 10 Resources
```

---

## 📈 性能优化建议

### 1. 数据库优化
- ✅ 添加索引（常用查询字段）
- ✅ 优化慢查询
- ✅ 使用连接池
- ✅ 启用查询缓存

### 2. Redis 优化
- ✅ 使用 Pipeline 批量操作
- ✅ 设置合理的过期时间
- ✅ 使用 Hash 存储对象
- ✅ 避免大 Key

### 3. 应用优化
- ✅ 使用异步处理
- ✅ 启用 HTTP Keep-Alive
- ✅ 压缩响应数据
- ✅ 使用 CDN 加速静态资源

### 4. 系统优化
- ✅ 增加文件描述符限制
- ✅ 优化网络参数
- ✅ 使用 SSD 硬盘
- ✅ 启用 BBR 拥塞控制

---

## 🔒 安全加固

```bash
# 1. 修改默认管理员密码
# 登录后台修改

# 2. 配置防火墙
sudo ufw allow 80/tcp
sudo ufw allow 6080/tcp
sudo ufw allow from 192.168.13.0/24 to any port 3306
sudo ufw allow from 192.168.13.0/24 to any port 6379
sudo ufw enable

# 3. 限制 Redis 访问
# 只允许容器内部访问，不暴露到公网

# 4. 使用 HTTPS
# 配置 SSL 证书（Let's Encrypt）

# 5. 定期备份
# 数据库备份
# Redis 备份
# 日志备份
```

---

## 📚 相关文档

- [Docker 快速部署](DOCKER_QUICK_START.md)
- [完整部署指南](DOCKER_DEPLOY_WITH_REDIS.md)
- [性能优化指南](docs/performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md)

---

**最后更新**: 2026-01-26  
**适用场景**: 高并发生产环境（10000+ QPS）
