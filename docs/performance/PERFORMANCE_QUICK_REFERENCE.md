# 性能配置快速参考

## 🎯 性能目标对照表

| 目标性能 | 队列进程数 | 每进程Workers | 批处理大小 | 数据库连接池 | 预期性能 |
|---------|-----------|--------------|-----------|-------------|---------|
| 2000条/秒 | 1 | 8 | 300 | 40 | 2700条/秒 |
| 5000条/秒 | 2 | 10 | 400 | 60 | 6000条/秒 |
| 10000条/秒 | 3 | 12 | 500 | 80 | 12000条/秒 |
| 15000条/秒 | 4 | 12 | 600 | 80 | 16000条/秒 |
| 20000条/秒 | 5 | 12 | 800 | 100 | 22000条/秒 |

## ⚙️ 配置文件选择

### 1. 标准性能（2000条/秒）

```bash
cd backend
cp .env.high_performance .env
```

**配置要点**：
- `APP_WORKERS=4`
- `ENABLE_QUEUE_WORKERS=0`
- `REDIS_QUEUE_NUM_WORKERS=8`
- `REDIS_QUEUE_BATCH_SIZE=300`
- `DB_MAXSIZE=40`

**启动方式**：
```bash
# 终端1
python start.py

# 终端2
python start_queue_worker.py
```

### 2. 超高性能（10000条/秒）

```bash
cd backend
cp .env.ultra_high_performance .env
```

**配置要点**：
- `APP_WORKERS=8`
- `ENABLE_QUEUE_WORKERS=0`
- `REDIS_QUEUE_NUM_WORKERS=12`
- `REDIS_QUEUE_BATCH_SIZE=500`
- `DB_MAXSIZE=80`

**启动方式**：
```bash
# 终端1：HTTP服务
python start.py

# 终端2-4：3个队列进程
python start_queue_worker.py &
python start_queue_worker.py &
python start_queue_worker.py &
```

## 🚀 快速启动命令

### 开发环境（单进程）

```bash
cd backend
python start.py
```

配置：
```bash
APP_WORKERS=1
ENABLE_QUEUE_WORKERS=1
```

### 生产环境（分离模式）

#### 方式1：手动启动

```bash
# HTTP服务
cd backend
python start.py &

# 队列处理（根据性能需求启动1-5个）
python start_queue_worker.py &
python start_queue_worker.py &
python start_queue_worker.py &
```

#### 方式2：使用Supervisor（推荐）

```bash
# 启动所有服务
sudo supervisorctl start qyd:*

# 查看状态
sudo supervisorctl status qyd:*

# 重启服务
sudo supervisorctl restart qyd:*

# 停止服务
sudo supervisorctl stop qyd:*
```

## 📊 性能监控命令

### 队列大小

```bash
# 查看当前队列大小
redis-cli ZCARD qyd:project_account_keys_zset

# 实时监控
watch -n 1 'redis-cli ZCARD qyd:project_account_keys_zset'
```

### 数据库连接

```bash
# 查看连接数
mysql -e "SELECT COUNT(*) FROM information_schema.PROCESSLIST;"

# 实时监控
watch -n 2 'mysql -e "SHOW PROCESSLIST;" | wc -l'
```

### Redis连接

```bash
# 查看连接数
redis-cli INFO clients | grep connected_clients

# 实时监控
watch -n 2 'redis-cli INFO clients | grep connected_clients'
```

### 系统资源

```bash
# CPU和内存
htop

# 或
top

# 进程列表
ps aux | grep python
```

## 🧪 性能测试

### 标准测试（10000条）

```bash
cd backend
python test_queue_performance.py
```

### 超高性能测试（50000条）

```bash
cd backend
python test_ultra_performance.py
```

### 清理测试数据

```bash
cd backend
python test_ultra_performance.py --cleanup
```

## 🔧 常见问题快速解决

### 问题1：性能未达标

**检查**：
```bash
# 1. 查看队列进程数
ps aux | grep start_queue_worker.py | wc -l

# 2. 查看配置
cat .env | grep REDIS_QUEUE
```

**解决**：
- 增加队列进程数
- 增加批处理大小
- 增加worker数量

### 问题2：队列堆积

**检查**：
```bash
redis-cli ZCARD qyd:project_account_keys_zset
```

**解决**：
```bash
# 启动更多队列进程
python start_queue_worker.py &
python start_queue_worker.py &
```

### 问题3：数据库连接耗尽

**检查**：
```bash
mysql -e "SHOW VARIABLES LIKE 'max_connections';"
mysql -e "SHOW PROCESSLIST;" | wc -l
```

**解决**：
```sql
-- 增加MySQL最大连接数
SET GLOBAL max_connections = 1000;
```

或减少连接池：
```bash
# .env
DB_MAXSIZE=60
```

### 问题4：Redis连接耗尽

**检查**：
```bash
redis-cli CONFIG GET maxclients
redis-cli INFO clients
```

**解决**：
```bash
# 增加Redis最大连接数
redis-cli CONFIG SET maxclients 10000
```

## 📈 性能调优速查表

### CPU使用率高

```bash
# 减少worker数量
REDIS_QUEUE_NUM_WORKERS=8

# 增加批处理大小
REDIS_QUEUE_BATCH_SIZE=800
```

### I/O等待高

```bash
# 优化MySQL
innodb_io_capacity = 4000
innodb_flush_log_at_trx_commit = 2

# 使用SSD存储
```

### 内存不足

```bash
# 减少连接池
DB_MAXSIZE=40
REDIS_MAX_CONNECTIONS=100

# 减少进程数
# 只启动2个队列进程
```

### 网络延迟

```bash
# 增加批处理大小
REDIS_QUEUE_BATCH_SIZE=1000

# 增加超时时间
DB_CONNECT_TIMEOUT=20
REDIS_TIMEOUT=10
```

## 🎯 性能优化检查清单

### MySQL优化

- [ ] `max_connections >= 1000`
- [ ] `innodb_buffer_pool_size = 50-70%内存`
- [ ] `innodb_flush_log_at_trx_commit = 2`
- [ ] `innodb_io_capacity = 2000-4000`
- [ ] 使用SSD存储

### Redis优化

- [ ] `maxmemory = 10-20GB`
- [ ] 禁用持久化（`save ""`）
- [ ] `maxclients = 10000`
- [ ] 使用内存存储

### 应用优化

- [ ] 启用读写分离
- [ ] 使用多队列进程
- [ ] 优化批处理大小
- [ ] 充足的连接池
- [ ] 使用Supervisor管理

### 系统优化

- [ ] 使用SSD存储
- [ ] 充足的内存（128GB+）
- [ ] 多核CPU（48核+）
- [ ] 低延迟网络
- [ ] 关闭不必要的服务

## 📚 相关文档

- [扩展到10000+条/秒指南](./SCALE_TO_10K_GUIDE.md)
- [Redis队列分离部署](./REDIS_QUEUE_SEPARATION_GUIDE.md)
- [性能分析报告](./REDIS_QUEUE_PERFORMANCE_ANALYSIS.md)
- [快速开始](./QUEUE_SEPARATION_QUICK_START.md)

## 🆘 获取帮助

### 查看日志

```bash
# 应用日志
tail -f backend/logs/app.log

# API日志
tail -f backend/logs/api.log

# 数据库日志
tail -f backend/logs/database.log

# Supervisor日志
tail -f backend/logs/supervisor_*.log
```

### 诊断命令

```bash
# 完整诊断
./monitor_performance.sh

# 或手动检查
echo "队列大小: $(redis-cli ZCARD qyd:project_account_keys_zset)"
echo "数据库连接: $(mysql -e 'SHOW PROCESSLIST;' | wc -l)"
echo "Redis连接: $(redis-cli INFO clients | grep connected_clients)"
echo "进程数: $(ps aux | grep python | wc -l)"
```

---

**更新时间**：2026-01-23  
**适用版本**：QYD v1.0+
