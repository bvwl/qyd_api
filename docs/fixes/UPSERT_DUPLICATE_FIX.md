# Upsert 重复记录问题修复

## 🐛 问题描述

使用 upsert 接口时，相同的 `account` 和 `project_id` 组合创建了多条记录，而不是更新现有记录。

### 问题表现

```bash
# 第一次调用
curl -X POST '/v1/project/account/upsert' \
  -d '{"account": "test", "balance": 10, "project_id": "xxx"}'
# 结果：创建记录 id=1

# 第二次调用（相同的 account 和 project_id）
curl -X POST '/v1/project/account/upsert' \
  -d '{"account": "test", "balance": 20, "project_id": "xxx"}'
# 期望：更新记录 id=1，balance=20
# 实际：创建新记录 id=2，balance=20
```

### 查询结果

```json
{
  "count": 2,
  "items": [
    {
      "id": "1",
      "account": "test",
      "balance": "20.000000",
      "project_id": "xxx"
    },
    {
      "id": "2", 
      "account": "test",
      "balance": "10.000000",
      "project_id": "xxx"
    }
  ]
}
```

## 🔍 问题原因

在 `backend/app/utils/redis_queue.py` 中，构建唯一键（key）时存在类型不一致的问题：

### 问题代码

```python
# 查询现有记录时
for record in batch_records:
    # project_id 是 UUID 对象
    key = tuple(getattr(record, field) for field in self.unique_fields)
    # key = ('test', UUID('xxx'))
    existing_records[key] = record

# 准备更新/创建时
for item in uncached_items:
    # project_id 是字符串
    key = tuple(item[field] for field in self.unique_fields)
    # key = ('test', 'xxx')
    
    if key in existing_records:  # ❌ 永远不会匹配
        # 更新
    else:
        # 创建（总是走这里）
```

### 根本原因

- 从数据库查询的记录中，`project_id` 是 `UUID` 对象
- Redis 中的数据，`project_id` 是字符串
- 两个 key 的类型不一致，导致无法匹配现有记录
- 结果：总是创建新记录，而不是更新

## ✅ 修复方案

### 修复代码

```python
# backend/app/utils/redis_queue.py

# 查询现有记录时 - 转为字符串
for record in batch_records:
    key = tuple(str(getattr(record, field)) for field in self.unique_fields)
    # key = ('test', 'xxx')  # 字符串
    existing_records[key] = record

# 准备更新/创建时 - 转为字符串
for item in uncached_items:
    key = tuple(str(item[field]) for field in self.unique_fields)
    # key = ('test', 'xxx')  # 字符串
    
    if key in existing_records:  # ✅ 可以匹配
        # 更新现有记录
    else:
        # 创建新记录
```

### 关键改动

1. **查询时转换**：`str(getattr(record, field))`
2. **比较时转换**：`str(item[field])`
3. **确保类型一致**：都转为字符串进行比较

## 🧪 测试验证

### 测试步骤

```bash
# 1. 清除缓存
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ \
  DEL "qyd:project_account_item_cache_test_xxx"

# 2. 第一次调用（创建）
curl -X POST 'http://127.0.0.1:6080/v1/project/account/upsert' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"account": "test", "balance": 10, "project_id": "xxx"}'

# 3. 查看日志
tail -f backend/logs/app.log | grep Worker
# 输出：[Worker-0] 数据库操作成功，更新 0，创建 1

# 4. 第二次调用（更新）
curl -X POST 'http://127.0.0.1:6080/v1/project/account/upsert' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{"account": "test", "balance": 20, "project_id": "xxx"}'

# 5. 查看日志
tail -f backend/logs/app.log | grep Worker
# 输出：[Worker-0] 数据库操作成功，更新 1，创建 0  ✅

# 6. 验证数据库
curl 'http://127.0.0.1:6080/v1/project/account?project_id=xxx' \
  -H 'Authorization: Bearer TOKEN'
# 结果：只有 1 条记录，balance=20
```

### 测试结果

```
✅ 第一次调用：创建 1 条记录
✅ 第二次调用：更新现有记录（不创建新记录）
✅ 数据库中只有 1 条记录
✅ balance 正确更新为 20
```

### 日志输出

```
# 第一次调用
[Worker-0] 处理数据 key=('test', 'xxx'), existing_keys=[]
[Worker-0] 数据库操作成功，更新 0，创建 1

# 第二次调用（清除缓存后）
[Worker-0] 处理数据 key=('test', 'xxx'), existing_keys=[('test', 'xxx')]
[Worker-0] 数据库操作成功，更新 1，创建 0
```

## 🔧 清理重复数据

如果已经产生了重复数据，可以使用清理脚本：

```bash
cd backend
python scripts/cleanup_duplicate_accounts.py
```

脚本会：
1. 查找所有重复的 `(account, project_id)` 组合
2. 保留最新的记录（按 `update_time` 排序）
3. 删除旧的重复记录

## 📝 相关修改

### 修改的文件

1. `backend/app/utils/redis_queue.py`
   - 修复查询时的 key 构建（添加 `str()` 转换）
   - 修复比较时的 key 构建（添加 `str()` 转换）
   - 添加调试日志

2. `backend/scripts/cleanup_duplicate_accounts.py`
   - 新增清理重复数据的脚本

### 其他改进

1. **添加调试日志**
   ```python
   logger.debug(f"[Worker-{worker_id}] 处理数据 key={key}, existing_keys={list(existing_records.keys())}")
   ```

2. **类型安全**
   - 所有唯一字段都转为字符串
   - 避免 UUID vs 字符串的类型不匹配

## ⚠️ 注意事项

### 1. 缓存影响

如果 Redis 中有缓存，会跳过数据库查询，直接使用缓存结果。测试时需要清除缓存：

```bash
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ \
  DEL "qyd:project_account_item_cache_ACCOUNT_PROJECTID"
```

### 2. 主从同步延迟

如果使用读写分离，可能存在主从同步延迟。刚创建的记录可能在从库中查询不到，导致重复创建。

**解决方案**：
- 增加缓存时间
- 或者查询时使用主库

### 3. 并发问题

如果多个请求同时处理相同的 `(account, project_id)`，可能仍会创建重复记录。

**解决方案**：
- 在数据库层面添加唯一索引
- 使用分布式锁

## 🎯 最佳实践

### 1. 数据库唯一索引

```sql
-- 添加唯一索引，防止重复
ALTER TABLE project_account 
ADD UNIQUE INDEX idx_account_project (account, project_id);
```

### 2. 定期清理

```bash
# 定时任务，每天清理一次重复数据
0 2 * * * cd /path/to/backend && python scripts/cleanup_duplicate_accounts.py
```

### 3. 监控告警

```python
# 监控重复记录数量
duplicates = await ProjectAccount.raw("""
    SELECT account, project_id, COUNT(*) as cnt
    FROM project_account
    GROUP BY account, project_id
    HAVING cnt > 1
""")

if duplicates:
    logger.warning(f"发现 {len(duplicates)} 组重复记录")
```

## 📅 更新信息

- **更新时间**：2026-01-23
- **问题**：Upsert 创建重复记录
- **原因**：UUID vs 字符串类型不匹配
- **修复**：统一转为字符串比较
- **状态**：✅ 已修复并测试通过

---

**相关文档**：
- [Upsert API 修复](UPSERT_API_FIX.md)
- [Redis 队列更新](UPSERT_REDIS_QUEUE_UPDATE.md)
- [队列处理完成](QUEUE_WORKER_AUTO_START_COMPLETE.md)
