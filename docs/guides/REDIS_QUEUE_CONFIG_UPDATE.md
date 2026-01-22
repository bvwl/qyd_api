# Redis队列配置更新

## 更新内容

将Redis队列的批量处理数量和工作线程数从硬编码改为通过.env配置文件管理，提高了系统的灵活性和可维护性。

## 修改的文件

### 1. `backend/.env`
添加了两个新的配置项：

```bash
# Redis 队列配置
# 每批处理的数据量
REDIS_QUEUE_BATCH_SIZE=200

# 工作线程数量
REDIS_QUEUE_NUM_WORKERS=4
```

### 2. `backend/.env.example`
同步更新了示例配置文件，添加了完整的Redis配置说明：

```bash
# Redis 队列配置
# 每批处理的数据量（建议100-500）
REDIS_QUEUE_BATCH_SIZE=200

# 工作线程数量（建议2-8，根据服务器性能调整）
REDIS_QUEUE_NUM_WORKERS=4
```

### 3. `backend/app/core/settings.py`
添加了配置读取：

```python
# Redis 队列配置
REDIS_QUEUE_BATCH_SIZE = int(os.getenv("REDIS_QUEUE_BATCH_SIZE", "200"))
REDIS_QUEUE_NUM_WORKERS = int(os.getenv("REDIS_QUEUE_NUM_WORKERS", "4"))
```

### 4. `backend/app/utils/project_account_queue.py`
从配置文件读取参数：

```python
from app.core.settings import REDIS_QUEUE_BATCH_SIZE, REDIS_QUEUE_NUM_WORKERS

class ProjectAccountQueue(RedisQueueHandler):
    def __init__(self):
        super().__init__(
            queue_name="project_account",
            model_class=ProjectAccount,
            unique_fields=["account", "project_id"],
            batch_size=REDIS_QUEUE_BATCH_SIZE,  # 从配置读取
            num_workers=REDIS_QUEUE_NUM_WORKERS  # 从配置读取
        )
```

### 5. `REDIS_QUEUE_GUIDE.md`
更新了配置说明，添加了详细的参数调整建议。

## 配置参数说明

### REDIS_QUEUE_BATCH_SIZE (批量大小)

**默认值**: 200

**建议范围**: 100-500

**说明**: 每批从队列中取出并处理的数据量

**调整建议**:
- **数据量小、处理快**: 设置为100-200
  - 适用于简单的数据插入或更新
  - 单条数据处理时间 < 10ms
  
- **数据量大、处理慢**: 设置为300-500
  - 适用于复杂的业务逻辑
  - 单条数据处理时间 > 50ms
  
- **服务器性能好**: 可以适当增大
  - CPU: 8核以上
  - 内存: 16GB以上
  - 数据库连接池: 50+

### REDIS_QUEUE_NUM_WORKERS (工作线程数)

**默认值**: 4

**建议范围**: 2-8

**说明**: 并发处理队列的工作线程数量

**调整建议**:
- **CPU核心数少（2-4核）**: 设置为2-4
  - 避免过多线程导致上下文切换开销
  
- **CPU核心数多（8核以上）**: 设置为4-8
  - 充分利用多核性能
  
- **数据库连接池有限**: 适当减少
  - 每个worker会占用数据库连接
  - 确保: workers * batch_size < 数据库最大连接数
  
- **需要快速处理**: 适当增加
  - 但要注意数据库和Redis的负载

## 性能调优建议

### 场景1: 高吞吐量
```bash
REDIS_QUEUE_BATCH_SIZE=500
REDIS_QUEUE_NUM_WORKERS=8
```
适用于：
- 服务器性能强劲
- 数据库连接池充足
- 需要快速处理大量数据

### 场景2: 低延迟
```bash
REDIS_QUEUE_BATCH_SIZE=100
REDIS_QUEUE_NUM_WORKERS=4
```
适用于：
- 需要快速响应
- 数据量不大
- 对实时性要求高

### 场景3: 资源受限
```bash
REDIS_QUEUE_BATCH_SIZE=200
REDIS_QUEUE_NUM_WORKERS=2
```
适用于：
- 服务器资源有限
- 数据库连接池较小
- 与其他服务共享资源

### 场景4: 平衡模式（推荐）
```bash
REDIS_QUEUE_BATCH_SIZE=200
REDIS_QUEUE_NUM_WORKERS=4
```
适用于：
- 大多数场景
- 性能和资源的平衡
- 默认配置

## 监控指标

调整配置后，建议监控以下指标：

1. **队列大小**: 
   ```bash
   redis-cli ZCARD qyd:project_account_keys_zset
   ```
   - 如果持续增长，说明处理速度跟不上，需要增加workers或batch_size

2. **处理速度**: 
   查看日志中的"成功处理 X 条数据"
   - 计算每秒处理的数据量
   - 对比队列增长速度

3. **数据库连接数**: 
   ```sql
   SHOW PROCESSLIST;
   ```
   - 确保不超过最大连接数
   - 如果接近上限，需要减少workers

4. **CPU使用率**: 
   ```bash
   top
   ```
   - 如果CPU使用率低，可以增加workers
   - 如果CPU使用率高（>80%），可能需要减少workers

5. **内存使用**: 
   ```bash
   free -h
   ```
   - 确保有足够的内存
   - batch_size越大，内存占用越多

## 使用示例

### 修改配置
编辑 `backend/.env` 文件：

```bash
# 增加批量大小到300
REDIS_QUEUE_BATCH_SIZE=300

# 增加工作线程到6
REDIS_QUEUE_NUM_WORKERS=6
```

### 重启服务
```bash
# 停止服务
# Ctrl+C 或 kill <pid>

# 启动服务
cd backend
python start.py
```

### 验证配置
查看启动日志：
```
队列处理已启动，6 个工作线程 [project_account]
[Worker-0] 启动 [project_account]
[Worker-1] 启动 [project_account]
...
[Worker-5] 启动 [project_account]
```

## 优势

1. **灵活性**: 无需修改代码即可调整性能参数
2. **可维护性**: 配置集中管理，易于维护
3. **环境适配**: 不同环境可以使用不同的配置
4. **快速调优**: 可以快速测试不同的配置组合
5. **文档化**: 配置文件本身就是文档

## 注意事项

1. **重启生效**: 修改配置后需要重启服务才能生效
2. **合理配置**: 不要盲目增大参数，要根据实际情况调整
3. **监控观察**: 调整后要持续监控系统表现
4. **逐步调整**: 建议每次只调整一个参数，观察效果
5. **备份配置**: 修改前备份原配置，以便回滚

## 总结

通过将Redis队列的关键参数移到配置文件中，系统变得更加灵活和易于维护。管理员可以根据实际的服务器性能和业务需求，快速调整队列处理的性能参数，无需修改代码或重新部署。

这种配置化的设计是生产环境的最佳实践，使得系统能够适应不同的运行环境和负载情况。
