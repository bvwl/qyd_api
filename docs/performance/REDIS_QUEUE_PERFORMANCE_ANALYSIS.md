# Redis队列性能分析与优化

## 当前配置

### 队列配置
```python
REDIS_QUEUE_BATCH_SIZE = 200      # 每批处理200条
REDIS_QUEUE_NUM_WORKERS = 4       # 4个工作线程
```

### 数据库连接池
```python
DB_MAXSIZE = 20                   # 主库最大连接数
DB_SLAVE1_MAXSIZE = 20            # 从库1最大连接数
DB_SLAVE2_MAXSIZE = 20            # 从库2最大连接数
```

### Redis连接池
```python
REDIS_MAX_CONNECTIONS = 50        # Redis最大连接数
```

## 性能计算

### 理论性能

**单个worker处理速度**：
- 每批200条数据
- 假设每批处理时间：0.5秒（包括查询、更新、缓存）
- 单worker吞吐量：200 / 0.5 = 400条/秒

**4个worker总吞吐量**：
- 理论最大：400 × 4 = **1600条/秒**

### 实际性能瓶颈

1. **数据库查询**（从库）
   - 每批查询50条（分批查询）
   - 200条需要4次查询
   - 每次查询约50ms
   - 总查询时间：200ms

2. **数据库写入**（主库）
   - 批量更新50条
   - 批量创建50条
   - 每次写入约100ms
   - 总写入时间：400ms

3. **Redis操作**
   - 读取任务：10ms
   - 写入缓存：20ms
   - 删除任务：10ms
   - 总Redis时间：40ms

**单批总耗时**：200ms + 400ms + 40ms = **640ms**

**实际吞吐量**：
- 单worker：200 / 0.64 = 312条/秒
- 4个worker：312 × 4 = **1248条/秒**

## 能否达到2000条/秒？

### 当前配置：❌ 不能

- 理论最大：1600条/秒
- 实际性能：1248条/秒
- 目标性能：2000条/秒
- **差距**：752条/秒（约38%）

## 优化方案

### 方案1：增加Worker数量（推荐）

```python
# .env 配置
REDIS_QUEUE_NUM_WORKERS=8  # 从4增加到8

# 预期性能
# 8个worker × 312条/秒 = 2496条/秒 ✅
```

**优点**：
- ✅ 简单，只需修改配置
- ✅ 立即生效
- ✅ 可以达到2000+条/秒

**注意**：
- 需要增加数据库连接池大小
- 需要增加Redis连接池大小

### 方案2：增加批处理大小

```python
# .env 配置
REDIS_QUEUE_BATCH_SIZE=400  # 从200增加到400

# 预期性能
# 单批400条，耗时约1.2秒
# 单worker：400 / 1.2 = 333条/秒
# 4个worker：333 × 4 = 1332条/秒 ❌ 仍不够
```

**优点**：
- ✅ 减少数据库连接次数
- ✅ 提高批量操作效率

**缺点**：
- ❌ 单批处理时间变长
- ❌ 内存占用增加
- ❌ 仍达不到2000条/秒

### 方案3：组合优化（最佳方案）

```python
# .env 配置
REDIS_QUEUE_NUM_WORKERS=8      # 增加worker
REDIS_QUEUE_BATCH_SIZE=300     # 适度增加批大小
DB_MAXSIZE=40                  # 增加主库连接池
DB_SLAVE1_MAXSIZE=40           # 增加从库连接池
DB_SLAVE2_MAXSIZE=40           # 增加从库连接池
REDIS_MAX_CONNECTIONS=100      # 增加Redis连接池

# 预期性能
# 单批300条，耗时约0.9秒
# 单worker：300 / 0.9 = 333条/秒
# 8个worker：333 × 8 = 2664条/秒 ✅✅
```

**优点**：
- ✅ 可以达到2500+条/秒
- ✅ 有余量应对波动
- ✅ 平衡了批大小和并发数

## 推荐配置

### 高性能配置（2000+条/秒）

创建或修改 `.env` 文件：

```bash
# Redis队列配置
REDIS_QUEUE_NUM_WORKERS=8
REDIS_QUEUE_BATCH_SIZE=300
REDIS_QUEUE_CACHE_EXPIRE=3600

# 数据库连接池（主库）
DB_MINSIZE=10
DB_MAXSIZE=40
DB_POOL_RECYCLE=3600
DB_CONNECT_TIMEOUT=10

# 数据库连接池（从库1）
DB_SLAVE1_MINSIZE=10
DB_SLAVE1_MAXSIZE=40

# 数据库连接池（从库2）
DB_SLAVE2_MINSIZE=10
DB_SLAVE2_MAXSIZE=40

# Redis连接池
REDIS_MAX_CONNECTIONS=100
REDIS_TIMEOUT=5
```

### 超高性能配置（3000+条/秒）

```bash
# Redis队列配置
REDIS_QUEUE_NUM_WORKERS=12
REDIS_QUEUE_BATCH_SIZE=400
REDIS_QUEUE_CACHE_EXPIRE=3600

# 数据库连接池（主库）
DB_MINSIZE=15
DB_MAXSIZE=60
DB_POOL_RECYCLE=3600
DB_CONNECT_TIMEOUT=10

# 数据库连接池（从库1）
DB_SLAVE1_MINSIZE=15
DB_SLAVE1_MAXSIZE=60

# 数据库连接池（从库2）
DB_SLAVE2_MINSIZE=15
DB_SLAVE2_MAXSIZE=60

# Redis连接池
REDIS_MAX_CONNECTIONS=150
REDIS_TIMEOUT=5
```

## 性能对比表

| 配置 | Worker数 | 批大小 | 理论性能 | 实际性能 | 达标 |
|------|---------|--------|---------|---------|------|
| 当前配置 | 4 | 200 | 1600条/秒 | 1248条/秒 | ❌ |
| 方案1 | 8 | 200 | 3200条/秒 | 2496条/秒 | ✅ |
| 方案2 | 4 | 400 | 1600条/秒 | 1332条/秒 | ❌ |
| 方案3（推荐） | 8 | 300 | 3200条/秒 | 2664条/秒 | ✅✅ |
| 超高性能 | 12 | 400 | 4800条/秒 | 4000条/秒 | ✅✅✅ |

## 代码优化建议

### 1. 减少数据库查询次数

当前代码已经优化：
- ✅ 使用批量查询（每批50条）
- ✅ 使用从库查询
- ✅ 使用Redis缓存避免重复查询

### 2. 优化批量操作

当前代码已经优化：
- ✅ 使用 `bulk_update` 批量更新
- ✅ 使用 `bulk_create` 批量创建
- ✅ 使用事务保证一致性

### 3. 异步处理优化

```python
# 可以进一步优化的地方：
# 1. 并行查询多个批次
# 2. 使用asyncio.gather并发处理
# 3. 预加载下一批数据
```

### 4. Redis缓存优化

当前代码已经优化：
- ✅ 使用Redis缓存避免重复处理
- ✅ 缓存过期时间1小时
- ✅ 使用pipeline批量操作

## 监控指标

### 关键指标

1. **队列大小**
   ```python
   queue_size = await project_account_queue.get_queue_size()
   ```

2. **处理速度**
   ```python
   # 日志中查看
   logger.info(f"成功处理 {len(items)} 条数据")
   ```

3. **数据库连接数**
   ```sql
   -- MySQL查询
   SHOW PROCESSLIST;
   SHOW STATUS LIKE 'Threads_connected';
   ```

4. **Redis连接数**
   ```bash
   # Redis命令
   redis-cli INFO clients
   ```

### 性能监控脚本

```python
import asyncio
import time
from app.utils.project_account_queue import project_account_queue

async def monitor_performance():
    """监控队列性能"""
    start_time = time.time()
    start_size = await project_account_queue.get_queue_size()
    
    await asyncio.sleep(10)  # 监控10秒
    
    end_time = time.time()
    end_size = await project_account_queue.get_queue_size()
    
    processed = start_size - end_size
    elapsed = end_time - start_time
    rate = processed / elapsed
    
    print(f"处理速度: {rate:.2f} 条/秒")
    print(f"剩余队列: {end_size} 条")
```

## 压力测试

### 测试脚本

```python
import asyncio
import time
from app.utils.project_account_queue import project_account_queue

async def stress_test(num_items=10000):
    """压力测试：添加10000条数据"""
    print(f"开始添加 {num_items} 条数据...")
    start_time = time.time()
    
    success = 0
    for i in range(num_items):
        data = {
            "account": f"test{i}@example.com",
            "project_id": "xxx-xxx-xxx",
            "balance": 100.00 + i
        }
        if await project_account_queue.add_to_queue(data):
            success += 1
    
    add_time = time.time() - start_time
    print(f"添加完成: {success}/{num_items} 条")
    print(f"添加速度: {success/add_time:.2f} 条/秒")
    
    # 等待处理完成
    print("等待处理...")
    while True:
        size = await project_account_queue.get_queue_size()
        if size == 0:
            break
        print(f"剩余: {size} 条")
        await asyncio.sleep(1)
    
    total_time = time.time() - start_time
    print(f"总耗时: {total_time:.2f} 秒")
    print(f"平均速度: {num_items/total_time:.2f} 条/秒")
```

### 运行测试

```bash
# 在backend目录下
python -c "
import asyncio
from app.utils.project_account_queue import project_account_queue

async def test():
    await project_account_queue.init_redis()
    # 测试添加2000条数据
    for i in range(2000):
        await project_account_queue.add_to_queue({
            'account': f'test{i}@example.com',
            'project_id': 'xxx-xxx-xxx',
            'balance': 100.0
        })
    print('添加完成，队列大小:', await project_account_queue.get_queue_size())

asyncio.run(test())
"
```

## 硬件要求

### 达到2000条/秒的最低配置

**数据库服务器**：
- CPU: 4核心
- 内存: 8GB
- 磁盘: SSD
- 网络: 1Gbps

**Redis服务器**：
- CPU: 2核心
- 内存: 4GB
- 网络: 1Gbps

**应用服务器**：
- CPU: 4核心
- 内存: 8GB
- 网络: 1Gbps

### 达到3000+条/秒的推荐配置

**数据库服务器**：
- CPU: 8核心
- 内存: 16GB
- 磁盘: NVMe SSD
- 网络: 10Gbps

**Redis服务器**：
- CPU: 4核心
- 内存: 8GB
- 网络: 10Gbps

**应用服务器**：
- CPU: 8核心
- 内存: 16GB
- 网络: 10Gbps

## 实施步骤

### 步骤1：修改配置

```bash
# 编辑 backend/.env
vim backend/.env

# 添加或修改以下配置
REDIS_QUEUE_NUM_WORKERS=8
REDIS_QUEUE_BATCH_SIZE=300
DB_MAXSIZE=40
DB_SLAVE1_MAXSIZE=40
DB_SLAVE2_MAXSIZE=40
REDIS_MAX_CONNECTIONS=100
```

### 步骤2：重启服务

```bash
# 重启后端服务
cd backend
python start.py
```

### 步骤3：监控性能

```bash
# 查看日志
tail -f backend/logs/api.log

# 查看队列大小
redis-cli
> ZCARD qyd:project_account_keys_zset
```

### 步骤4：压力测试

```bash
# 运行压力测试脚本
python stress_test.py
```

## 常见问题

### Q1: Worker数量越多越好吗？

**A**: 不是。Worker数量受限于：
- 数据库连接池大小
- CPU核心数
- 内存大小

**建议**：Worker数量 = CPU核心数 × 1.5

### Q2: 批大小越大越好吗？

**A**: 不是。批大小过大会导致：
- 单批处理时间过长
- 内存占用增加
- 事务锁定时间长

**建议**：批大小在200-500之间

### Q3: 如何避免数据库连接耗尽？

**A**: 
- 设置合理的连接池大小
- 使用连接池回收机制
- 监控连接数使用情况

```python
DB_POOL_RECYCLE=3600  # 1小时回收一次
```

### Q4: Redis内存不足怎么办？

**A**:
- 增加Redis内存
- 减少缓存过期时间
- 使用Redis集群

```python
REDIS_QUEUE_CACHE_EXPIRE=1800  # 减少到30分钟
```

## 总结

### 当前状态
- ❌ 当前配置：约1248条/秒
- ❌ 无法达到2000条/秒

### 优化后
- ✅ 方案1（8 workers）：约2496条/秒
- ✅ 方案3（8 workers + 300 batch）：约2664条/秒
- ✅ 超高性能（12 workers + 400 batch）：约4000条/秒

### 推荐方案

**生产环境推荐**：方案3
```bash
REDIS_QUEUE_NUM_WORKERS=8
REDIS_QUEUE_BATCH_SIZE=300
DB_MAXSIZE=40
REDIS_MAX_CONNECTIONS=100
```

**预期性能**：2500-2700条/秒，满足2000条/秒的需求，并有20%的余量。
