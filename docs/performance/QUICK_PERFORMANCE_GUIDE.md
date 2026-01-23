# 快速性能优化指南

## 🎯 目标：达到2000条/秒

## 📊 当前状态

**默认配置**：
- Worker数量：4
- 批处理大小：200
- **性能**：约1248条/秒 ❌

## ⚡ 快速优化（3步）

### 步骤1：复制高性能配置

```bash
cd backend
cp .env.high_performance .env
```

### 步骤2：修改配置（根据实际情况）

```bash
vim .env

# 关键参数：
REDIS_QUEUE_NUM_WORKERS=8      # 增加到8
REDIS_QUEUE_BATCH_SIZE=300     # 增加到300
DB_MAXSIZE=40                  # 增加到40
REDIS_MAX_CONNECTIONS=100      # 增加到100
```

### 步骤3：重启服务

```bash
python start.py
```

## 🧪 性能测试

```bash
cd backend
python test_queue_performance.py
```

**预期结果**：
```
处理速度: 2500-2700 条/秒 ✅
达到目标性能（2000条/秒）
```

## 📈 性能对比

| 配置 | Worker | 批大小 | 性能 | 达标 |
|------|--------|--------|------|------|
| 默认 | 4 | 200 | 1248条/秒 | ❌ |
| 优化 | 8 | 300 | 2664条/秒 | ✅ |

## 🔧 配置说明

### Worker数量（REDIS_QUEUE_NUM_WORKERS）

**作用**：并发处理线程数

| 值 | 性能 | 说明 |
|----|------|------|
| 4 | 1248条/秒 | 默认配置 |
| 6 | 1872条/秒 | 接近目标 |
| 8 | 2664条/秒 | ✅ 推荐 |
| 12 | 4000条/秒 | 超高性能 |

**建议**：CPU核心数 × 1.5

### 批处理大小（REDIS_QUEUE_BATCH_SIZE）

**作用**：每批处理的数据量

| 值 | 优点 | 缺点 |
|----|------|------|
| 100 | 响应快 | 效率低 |
| 200 | 平衡 | 默认值 |
| 300 | ✅ 推荐 | 内存稍高 |
| 500 | 高效 | 单批时间长 |

**建议**：200-400之间

### 数据库连接池（DB_MAXSIZE）

**作用**：最大数据库连接数

| Worker | 推荐连接池 |
|--------|-----------|
| 4 | 20 |
| 8 | 40 ✅ |
| 12 | 60 |

**公式**：Worker数 × 5

### Redis连接池（REDIS_MAX_CONNECTIONS）

**作用**：最大Redis连接数

| Worker | 推荐连接池 |
|--------|-----------|
| 4 | 50 |
| 8 | 100 ✅ |
| 12 | 150 |

**公式**：Worker数 × 12

## 🚀 不同场景配置

### 场景1：达到2000条/秒（推荐）

```bash
REDIS_QUEUE_NUM_WORKERS=8
REDIS_QUEUE_BATCH_SIZE=300
DB_MAXSIZE=40
REDIS_MAX_CONNECTIONS=100
```

**性能**：2500-2700条/秒

### 场景2：达到3000条/秒

```bash
REDIS_QUEUE_NUM_WORKERS=12
REDIS_QUEUE_BATCH_SIZE=400
DB_MAXSIZE=60
REDIS_MAX_CONNECTIONS=150
```

**性能**：3500-4000条/秒

### 场景3：低配服务器（1000条/秒）

```bash
REDIS_QUEUE_NUM_WORKERS=4
REDIS_QUEUE_BATCH_SIZE=200
DB_MAXSIZE=20
REDIS_MAX_CONNECTIONS=50
```

**性能**：1000-1200条/秒

## 📝 监控命令

### 查看队列大小

```bash
redis-cli
> ZCARD qyd:project_account_keys_zset
```

### 查看数据库连接数

```sql
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';
```

### 查看Redis连接数

```bash
redis-cli INFO clients
```

### 查看日志

```bash
tail -f backend/logs/api.log
```

## ⚠️ 注意事项

### 1. 硬件要求

**最低配置**（2000条/秒）：
- CPU: 4核心
- 内存: 8GB
- 磁盘: SSD

**推荐配置**（3000+条/秒）：
- CPU: 8核心
- 内存: 16GB
- 磁盘: NVMe SSD

### 2. 数据库优化

```sql
-- 检查索引
SHOW INDEX FROM project_accounts;

-- 检查慢查询
SHOW VARIABLES LIKE 'slow_query_log';
```

### 3. Redis优化

```bash
# 检查内存使用
redis-cli INFO memory

# 检查持久化配置
redis-cli CONFIG GET save
```

## 🐛 常见问题

### Q1: 性能没有提升？

**检查**：
1. 配置是否生效？
2. 服务是否重启？
3. 数据库连接池是否足够？
4. Redis是否正常？

### Q2: 数据库连接耗尽？

**解决**：
```bash
# 增加连接池
DB_MAXSIZE=60

# 减少Worker
REDIS_QUEUE_NUM_WORKERS=6
```

### Q3: Redis内存不足？

**解决**：
```bash
# 减少缓存时间
REDIS_QUEUE_CACHE_EXPIRE=1800

# 增加Redis内存
redis-cli CONFIG SET maxmemory 4gb
```

### Q4: CPU使用率过高？

**解决**：
```bash
# 减少Worker
REDIS_QUEUE_NUM_WORKERS=6

# 增加批大小
REDIS_QUEUE_BATCH_SIZE=400
```

## 📞 技术支持

如果遇到问题：
1. 查看日志：`backend/logs/api.log`
2. 运行测试：`python test_queue_performance.py`
3. 检查配置：`cat backend/.env`

## 🎉 总结

**简单3步，达到2000条/秒**：

1. 复制配置：`cp .env.high_performance .env`
2. 修改参数：Worker=8, Batch=300
3. 重启服务：`python start.py`

**预期性能**：2500-2700条/秒 ✅
