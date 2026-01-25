# Redis数据库分离方案

## 问题背景

项目账号和项目提现功能都使用Redis队列进行异步处理。如果它们使用相同的Redis数据库，可能会导致：
1. **数据混淆**：两个队列的数据可能互相干扰
2. **性能问题**：共享同一个数据库可能导致性能瓶颈
3. **维护困难**：难以独立监控和管理各个队列

## 解决方案

为不同的功能模块分配独立的Redis数据库：

### Redis数据库分配

| 功能模块 | 队列数据库 | 缓存数据库 | 说明 |
|---------|-----------|-----------|------|
| 项目账号 | DB 0 | DB 1 | 项目账号的批量处理和缓存 |
| 项目提现 | DB 2 | DB 3 | 项目提现的批量处理和缓存 |

### 架构设计

```
Redis Server
├── DB 0: project_account 队列数据
│   ├── qyd_project_account_item_*     (任务数据)
│   └── qyd_project_account_keys_zset  (任务队列)
│
├── DB 1: project_account 缓存数据
│   └── qyd_project_account_cache_*    (缓存数据)
│
├── DB 2: project_withdrawal 队列数据
│   ├── qyd_project_withdrawal_item_*     (任务数据)
│   └── qyd_project_withdrawal_keys_zset  (任务队列)
│
└── DB 3: project_withdrawal 缓存数据
    └── qyd_project_withdrawal_cache_*    (缓存数据)
```

## 实现细节

### 1. RedisQueueHandler基类修改

在 `backend/app/utils/redis_queue.py` 中添加了 `queue_db` 和 `cache_db` 参数：

```python
class RedisQueueHandler:
    def __init__(
        self,
        queue_name: str,
        model_class,
        unique_fields: List[str],
        batch_size: int = 200,
        num_workers: int = 4,
        queue_db: int = 0,  # 队列使用的Redis数据库编号
        cache_db: int = 1   # 缓存使用的Redis数据库编号
    ):
        # ...
        self.queue_db = queue_db
        self.cache_db = cache_db
```

### 2. 项目账号队列配置

`backend/app/utils/project_account_queue.py`：

```python
class ProjectAccountQueue(RedisQueueHandler):
    def __init__(self):
        super().__init__(
            queue_name="project_account",
            model_class=ProjectAccount,
            unique_fields=["account", "project_id"],
            batch_size=REDIS_QUEUE_BATCH_SIZE,
            num_workers=REDIS_QUEUE_NUM_WORKERS
            # 默认使用 queue_db=0, cache_db=1
        )
```

### 3. 项目提现队列配置

`backend/app/utils/project_withdrawal_queue.py`：

```python
class ProjectWithdrawalQueue(RedisQueueHandler):
    def __init__(self):
        super().__init__(
            queue_name="project_withdrawal",
            model_class=ProjectWithdrawal,
            unique_fields=["project_id"],
            batch_size=REDIS_QUEUE_BATCH_SIZE,
            num_workers=REDIS_QUEUE_NUM_WORKERS,
            queue_db=2,  # 使用 DB 2 作为队列数据库
            cache_db=3   # 使用 DB 3 作为缓存数据库
        )
```

## 验证测试

### 运行测试脚本

```bash
python backend/test_redis_separation.py
```

### 测试结果

```
项目账号队列配置:
  队列名称: project_account
  队列DB: 0
  缓存DB: 1

项目提现队列配置:
  队列名称: project_withdrawal
  队列DB: 2
  缓存DB: 3

✓ 验证通过：两个队列使用不同的Redis数据库
✓ 数据隔离验证通过：两个队列的数据互不影响
```

## 优势

### 1. 数据隔离
- 每个功能模块的数据完全独立
- 避免数据混淆和冲突
- 提高数据安全性

### 2. 性能优化
- 减少单个数据库的压力
- 提高并发处理能力
- 避免相互影响

### 3. 易于维护
- 可以独立监控各个队列
- 可以独立清理各个数据库
- 便于问题排查和调试

### 4. 扩展性
- 未来添加新功能时，可以轻松分配新的数据库
- 支持更细粒度的资源管理

## 监控和管理

### 查看队列状态

```bash
# 连接到Redis
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ

# 查看项目账号队列（DB 0）
SELECT 0
KEYS qyd_project_account_*

# 查看项目账号缓存（DB 1）
SELECT 1
KEYS qyd_project_account_cache_*

# 查看项目提现队列（DB 2）
SELECT 2
KEYS qyd_project_withdrawal_*

# 查看项目提现缓存（DB 3）
SELECT 3
KEYS qyd_project_withdrawal_cache_*
```

### 清理队列数据

```bash
# 清理项目账号队列
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ -n 0 FLUSHDB

# 清理项目账号缓存
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ -n 1 FLUSHDB

# 清理项目提现队列
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ -n 2 FLUSHDB

# 清理项目提现缓存
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ -n 3 FLUSHDB
```

## 未来扩展

如果需要添加新的队列功能，可以继续分配新的数据库：

| 功能模块 | 队列数据库 | 缓存数据库 |
|---------|-----------|-----------|
| 新功能1 | DB 4 | DB 5 |
| 新功能2 | DB 6 | DB 7 |
| ... | ... | ... |

Redis默认支持16个数据库（DB 0-15），足够满足大多数场景。

## 注意事项

1. **Redis配置**：确保Redis配置文件中 `databases` 参数至少为16（默认值）
2. **连接池**：每个数据库都有独立的连接池，注意监控连接数
3. **备份策略**：备份时需要考虑所有使用的数据库
4. **迁移**：如果需要迁移数据，需要分别处理各个数据库

## 相关文件

- `backend/app/utils/redis_queue.py` - Redis队列基类
- `backend/app/utils/project_account_queue.py` - 项目账号队列
- `backend/app/utils/project_withdrawal_queue.py` - 项目提现队列
- `backend/test_redis_separation.py` - 分离测试脚本
- `backend/start_queue_worker.py` - 队列处理启动脚本

## 版本历史

### v1.1.0 (2026-01-25)
- ✅ 实现Redis数据库分离
- ✅ 项目账号使用 DB 0/1
- ✅ 项目提现使用 DB 2/3
- ✅ 添加分离测试脚本
- ✅ 更新文档
