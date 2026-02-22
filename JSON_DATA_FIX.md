# JSON 数据格式错误修复

## 更新时间
2026-02-22

## 问题描述

在日志中发现 MySQL 报错：

```
(3140, 'Invalid JSON text: "Missing a comma or \'}\' after an object member." 
at position 9 in value for column \'project_account.data\'.')
```

## 原因分析

1. **数据源问题**：传入 Redis 队列的数据中，`data` 字段包含无效的 JSON 格式
2. **缺少验证**：在写入数据库前没有验证 JSON 格式的有效性
3. **错误传播**：无效数据被重复重试，导致大量错误日志

## 解决方案

### 1. 添加 JSON 数据验证

修改了 `backend/app/utils/redis_queue.py`，在数据处理前验证和清理 JSON 字段：

```python
# 验证和清理 JSON 字段
if 'data' in item and item['data'] is not None:
    try:
        # 如果 data 是字符串，尝试解析为 JSON
        if isinstance(item['data'], str):
            item['data'] = json.loads(item['data'])
        # 如果 data 是字典，验证可以序列化
        elif isinstance(item['data'], dict):
            json.dumps(item['data'])  # 验证可以序列化
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(
            f"无效的 JSON 数据，已清空 data 字段: {e}, "
            f"原始数据: {str(item.get('data', ''))[:100]}"
        )
        item['data'] = None  # 清空无效的 JSON 数据
```

### 2. 增强 JSON 错误处理

添加了专门的 JSON 错误处理逻辑：

```python
# 检查是否是 JSON 格式错误
if "Invalid JSON" in error_msg or "JSON" in error_msg:
    # 使用错误去重
    error_key = f"json_error:{self.queue_name}"
    should_log, count = should_log_error(error_key)
    
    if should_log:
        # 首次记录详细错误和数据样本
        # 后续只记录累计次数
    
    # JSON 错误不重试，直接删除任务
    # 避免无效数据反复重试
```

### 3. 记录问题数据样本

首次遇到 JSON 错误时，记录问题数据样本：

```python
# 记录第一条有问题的数据样本
if items:
    sample_data = items[0]
    logger.error(
        f"问题数据样本: "
        f"account={sample_data.get('account', 'N/A')}, "
        f"data={str(sample_data.get('data', 'N/A'))[:200]}"
    )
```

## 修改的文件

1. **backend/app/utils/redis_queue.py**
   - 添加 JSON 数据验证和清理
   - 增强 JSON 错误处理
   - 记录问题数据样本
   - JSON 错误不重试，直接删除

## 效果对比

### 修复前

```
ERROR [Worker-5] 数据库操作失败 [project_account]: (3140, 'Invalid JSON text...')
ERROR [Worker-5] 数据库操作失败 [project_account]: (3140, 'Invalid JSON text...')
ERROR [Worker-5] 数据库操作失败 [project_account]: (3140, 'Invalid JSON text...')
... (无限重试，重复记录)
```

### 修复后

```
WARNING [Worker-5] 无效的 JSON 数据，已清空 data 字段: Expecting ',' delimiter: line 1 column 10 (char 9), 
原始数据: {"key": "value" "invalid"}

# 如果验证后仍有错误（首次）
ERROR [Worker-5] JSON 格式错误 [project_account]: (3140, 'Invalid JSON text...')
问题数据样本: account=test@example.com, data={"invalid": json}
已删除 1 个无效 JSON 数据的任务

# 如果再次发生（5分钟内）
ERROR [Worker-5] JSON 格式错误 [project_account]: (3140, 'Invalid JSON text...') 
(此错误在过去5分钟内已发生 5 次，请检查数据源)
```

## 预防措施

### 1. 数据源验证

在数据进入队列前就进行验证：

```python
# 在 API 层验证
from pydantic import BaseModel, validator
import json

class ProjectAccountCreate(BaseModel):
    account: str
    data: dict | None = None
    
    @validator('data')
    def validate_json_data(cls, v):
        if v is not None:
            try:
                # 验证可以序列化
                json.dumps(v)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid JSON data: {e}")
        return v
```

### 2. 数据清理

定期检查和清理无效数据：

```python
# 查找无效 JSON 数据
SELECT id, account, data 
FROM project_account 
WHERE data IS NOT NULL 
AND JSON_VALID(data) = 0;

# 清理无效数据
UPDATE project_account 
SET data = NULL 
WHERE data IS NOT NULL 
AND JSON_VALID(data) = 0;
```

### 3. 监控告警

设置监控告警，及时发现数据质量问题：

```python
# 统计 JSON 错误
from app.utils.error_tracker import get_error_stats

stats = get_error_stats()
json_errors = {k: v for k, v in stats.items() if 'json_error' in k}

if json_errors:
    # 发送告警
    print(f"JSON 错误统计: {json_errors}")
```

## 排查步骤

如果继续出现 JSON 错误：

### 1. 查看日志中的数据样本

```bash
# 查找 JSON 错误日志
grep "JSON 格式错误" backend/logs/app.log | head -5

# 查找问题数据样本
grep "问题数据样本" backend/logs/app.log | head -5
```

### 2. 检查数据源

```python
# 检查 API 调用
# 查看是哪个接口传入了无效数据
```

### 3. 验证数据库中的数据

```sql
-- 查找无效 JSON 数据
SELECT id, account, data 
FROM project_account 
WHERE data IS NOT NULL 
AND JSON_VALID(data) = 0
LIMIT 10;

-- 查看具体内容
SELECT id, account, CAST(data AS CHAR) as data_text
FROM project_account 
WHERE id = 'xxx';
```

### 4. 手动修复

```sql
-- 清空无效数据
UPDATE project_account 
SET data = NULL 
WHERE id = 'xxx';

-- 或者修复数据
UPDATE project_account 
SET data = '{"corrected": "data"}' 
WHERE id = 'xxx';
```

## 常见 JSON 错误

### 1. 缺少逗号

```json
// 错误
{"key1": "value1" "key2": "value2"}

// 正确
{"key1": "value1", "key2": "value2"}
```

### 2. 多余的逗号

```json
// 错误
{"key1": "value1", "key2": "value2",}

// 正确
{"key1": "value1", "key2": "value2"}
```

### 3. 单引号

```json
// 错误
{'key': 'value'}

// 正确
{"key": "value"}
```

### 4. 未转义的特殊字符

```json
// 错误
{"text": "Line 1
Line 2"}

// 正确
{"text": "Line 1\nLine 2"}
```

### 5. NaN 或 Infinity

```json
// 错误
{"number": NaN}

// 正确
{"number": null}
```

## 验证修复

```bash
# 1. 重启服务
docker-compose restart backend-api queue-worker

# 2. 查看日志
tail -f backend/logs/app.log | grep -E "JSON|数据库操作"

# 3. 检查错误统计
cd backend
python -c "from app.utils.error_tracker import get_error_stats; import json; print(json.dumps(get_error_stats(), indent=2))"

# 4. 验证数据库
mysql -u qyd -p qyd -e "SELECT COUNT(*) FROM project_account WHERE data IS NOT NULL AND JSON_VALID(data) = 0;"
```

## 总结

通过以下改进：

1. ✅ 添加 JSON 数据验证和清理
2. ✅ 增强 JSON 错误处理
3. ✅ 记录问题数据样本
4. ✅ JSON 错误不重试，避免无限循环
5. ✅ 使用错误去重，减少日志量

现在系统能够：
- 自动检测和清理无效 JSON 数据
- 避免无效数据反复重试
- 提供详细的错误信息和数据样本
- 减少重复错误日志

## 相关文档

- `REDIS_ERROR_FIX_SUMMARY.md` - Redis 错误修复总结
- `LOG_CONFIG_UPDATE.md` - 日志配置更新说明
- `backend/app/utils/error_tracker.py` - 错误追踪器
- `backend/app/utils/redis_queue.py` - Redis 队列处理
