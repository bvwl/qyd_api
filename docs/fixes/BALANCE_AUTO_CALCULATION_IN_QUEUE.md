# Balance 自动计算功能（Redis 队列）

## 📋 需求说明

在 Redis 队列处理中添加 balance 自动计算逻辑：
1. 当传入 `balance` 时，自动计算 `variable` 和 `balance_history`
2. 如果没有传 `balance`，不处理这些字段
3. 避免用户传入的 `variable` 和 `balance_history` 被使用（应该被忽略）

## ✅ 实现方案

### 1. 计算逻辑

**balance_history（余额历史）**
- 存储最近 7 天的余额记录
- 格式：`{"2026-01-23": 100.0, "2026-01-22": 80.0, ...}`
- 同一天多次更新会覆盖（实时更新）
- 按日期倒序排序，保留最近 7 条

**variable（变动余额）**
- 计算公式：
  - 首次创建：`variable = balance`（从 0 增加到 balance）
  - 更新记录：`variable = 今天余额 - 昨天余额`
- 保留 2 位小数

### 2. 处理流程

```
传入数据
  ↓
检查是否包含 balance
  ├─ 是: 继续处理
  │   ↓
  │   1. 过滤掉 variable 和 balance_history（忽略用户传入的值）
  │   2. 更新/创建记录
  │   3. 获取当前日期
  │   4. 更新 balance_history[today] = balance
  │   5. 排序并保留最近 7 条
  │   6. 计算 variable = today_balance - yesterday_balance
  │   7. 保存到数据库
  │
  └─ 否: 正常处理其他字段，不触及 balance/variable/balance_history
```

### 3. 代码实现

**位置**: `backend/app/utils/redis_queue.py`

**关键代码**:

```python
# 过滤数据时排除 variable 和 balance_history
filtered_item = {
    k: v for k, v in item.items() 
    if v is not None and k not in ['variable', 'balance_history']
}

# 检查是否传入了 balance
has_balance = 'balance' in filtered_item

# 如果传入了 balance，需要计算 variable 和 balance_history
if has_balance:
    from datetime import datetime
    from decimal import Decimal
    
    new_balance = Decimal(str(filtered_item['balance']))
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 初始化 balance_history
    if record.balance_history is None:
        record.balance_history = {}
    
    # 实时更新当天的余额记录（覆盖）
    record.balance_history[today] = float(new_balance)
    
    # 按日期排序并保留最近7条记录
    sorted_data = dict(sorted(record.balance_history.items(), key=lambda x: x[0], reverse=True))
    record.balance_history = dict(list(sorted_data.items())[:7])
    
    # 实时计算变动余额：当前余额 - 昨天的余额
    if len(record.balance_history) >= 2:
        dates = list(record.balance_history.keys())
        today_balance = Decimal(str(record.balance_history[dates[0]]))  # 今天的余额（最新）
        yesterday_balance = Decimal(str(record.balance_history[dates[1]]))  # 昨天的余额
        record.variable = (today_balance - yesterday_balance).quantize(Decimal('0.01'))
    else:
        record.variable = Decimal('0.00')
```

## 🧪 测试场景

### 测试场景1: 首次创建（传入 balance）

**请求**:
```json
{
  "account": "test_account",
  "balance": 100,
  "project_id": "xxx-xxx-xxx"
}
```

**预期结果**:
```json
{
  "balance": 100.0,
  "variable": 100.0,
  "balance_history": {
    "2026-01-23": 100.0
  }
}
```

**说明**:
- balance 设置为 100
- variable 为 100（首次创建，相当于从 0 增加到 100）
- balance_history 记录今天的余额

### 测试场景2: 第二天更新（传入 balance）

**请求**:
```json
{
  "account": "test_account",
  "balance": 150,
  "project_id": "xxx-xxx-xxx"
}
```

**预期结果**:
```json
{
  "balance": 150.0,
  "variable": 50.0,
  "balance_history": {
    "2026-01-23": 150.0
  }
}
```

**说明**:
- balance 更新为 150
- variable = 150 - 100 = 50（如果是同一天，会覆盖之前的记录）
- balance_history 同一天会覆盖

### 测试场景3: 不传 balance，只更新其他字段

**请求**:
```json
{
  "account": "test_account",
  "status": 2,
  "project_id": "xxx-xxx-xxx"
}
```

**预期结果**:
```json
{
  "status": 2,
  "balance": 150.0,
  "variable": 50.0,
  "balance_history": {
    "2026-01-23": 150.0
  }
}
```

**说明**:
- status 更新为 2
- balance/variable/balance_history 保持不变

### 测试场景4: 传入 variable 和 balance_history（应该被忽略）

**请求**:
```json
{
  "account": "test_account",
  "balance": 200,
  "variable": 999,
  "balance_history": {"2020-01-01": 999},
  "project_id": "xxx-xxx-xxx"
}
```

**预期结果**:
```json
{
  "balance": 200.0,
  "variable": 50.0,
  "balance_history": {
    "2026-01-23": 200.0
  }
}
```

**说明**:
- balance 更新为 200
- variable = 200 - 150 = 50（自动计算，忽略传入的 999）
- balance_history 自动计算（忽略传入的 2020-01-01）

### 测试场景5: 跨天更新（模拟多天记录）

假设已有记录：
```json
{
  "balance_history": {
    "2026-01-23": 200.0,
    "2026-01-22": 150.0,
    "2026-01-21": 100.0
  }
}
```

**请求**（第二天）:
```json
{
  "account": "test_account",
  "balance": 250,
  "project_id": "xxx-xxx-xxx"
}
```

**预期结果**:
```json
{
  "balance": 250.0,
  "variable": 50.0,
  "balance_history": {
    "2026-01-24": 250.0,
    "2026-01-23": 200.0,
    "2026-01-22": 150.0,
    "2026-01-21": 100.0
  }
}
```

**说明**:
- balance 更新为 250
- variable = 250 - 200 = 50（今天 - 昨天）
- balance_history 新增今天的记录

## 🔍 测试方法

### 1. 运行测试脚本

```bash
cd backend
python test_balance_calculation.py
```

### 2. 手动测试

```bash
# 1. 启动后端服务
cd backend
python start.py

# 2. 启动队列处理
./start_queue_processing.sh

# 3. 测试首次创建
curl -X POST 'http://127.0.0.1:6080/v1/project/account/upsert' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "account": "test_balance",
    "balance": 100,
    "project_id": "YOUR_PROJECT_ID"
  }'

# 4. 等待 5 秒后查询
sleep 5

curl 'http://127.0.0.1:6080/v1/project/account?account=test_balance' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# 5. 测试更新
curl -X POST 'http://127.0.0.1:6080/v1/project/account/upsert' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "account": "test_balance",
    "balance": 150,
    "project_id": "YOUR_PROJECT_ID"
  }'

# 6. 等待 5 秒后查询
sleep 5

curl 'http://127.0.0.1:6080/v1/project/account?account=test_balance' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

### 3. 查看日志

```bash
# 查看队列处理日志
tail -f backend/logs/app.log | grep "Worker"

# 查看 balance 计算相关日志
tail -f backend/logs/app.log | grep "balance"
```

## 📊 字段说明

### balance（余额）
- 类型：Decimal(18, 6)
- 说明：当前余额
- 来源：用户传入
- 示例：`100.000000`

### variable（变动余额）
- 类型：Decimal(18, 6)
- 说明：余额变动
- 来源：自动计算
- 计算规则：
  - 首次创建：`variable = balance`（从 0 增加到 balance）
  - 更新记录：`variable = 今天余额 - 昨天余额`
- 示例：`50.000000`（表示增加了 50）
- 示例：`-20.000000`（表示减少了 20）
- 示例：`100.000000`（首次创建，balance=100）

### balance_history（余额历史）
- 类型：JSON
- 说明：最近 7 天的余额记录
- 来源：自动维护
- 格式：`{"日期": 余额, ...}`
- 示例：
  ```json
  {
    "2026-01-23": 200.0,
    "2026-01-22": 150.0,
    "2026-01-21": 100.0
  }
  ```

## ⚠️ 注意事项

### 1. 同一天多次更新

如果同一天多次更新 balance，会覆盖之前的记录：

```
第一次: balance=100 → balance_history={"2026-01-23": 100}
第二次: balance=150 → balance_history={"2026-01-23": 150}  # 覆盖
```

这是**预期行为**，因为我们只关心每天的最终余额。

### 2. variable 的计算时机

variable 的计算逻辑：
- **首次创建**：`variable = balance`（相当于从 0 增加到 balance）
- **更新记录**：`variable = 今天余额 - 昨天余额`（基于 balance_history 中的最近两条记录）

**首次创建示例**：
```
创建: balance=100 → balance_history={"2026-01-23": 100}
      → variable = 100（从0增加到100）
```

**同一天多次更新的影响**：
```
初始: balance_history={"2026-01-22": 100}
第一次更新: balance=150 → balance_history={"2026-01-23": 150, "2026-01-22": 100}
            → variable = 150 - 100 = 50

第二次更新: balance=200 → balance_history={"2026-01-23": 200, "2026-01-22": 100}
            → variable = 200 - 100 = 100  # 注意：是 200-100，不是 200-150
```

### 3. 用户传入的 variable 和 balance_history 会被忽略

这是**安全设计**，防止用户篡改计算结果：

```python
# 过滤时排除这两个字段
filtered_item = {
    k: v for k, v in item.items() 
    if v is not None and k not in ['variable', 'balance_history']
}
```

### 4. 不传 balance 时的行为

如果请求中没有 `balance` 字段，不会触及 balance/variable/balance_history：

```json
// 请求
{
  "account": "test",
  "status": 2
}

// 结果：只更新 status，balance/variable/balance_history 保持不变
```

## 🔄 与 CRUD 的一致性

Redis 队列处理的逻辑与 `backend/app/crud/project/account.py` 中的 `update()` 和 `upsert()` 方法保持一致：

| 功能 | CRUD | Redis 队列 |
|------|------|-----------|
| balance_history 存储 | 最近 7 天 | 最近 7 天 |
| 同一天覆盖 | ✅ | ✅ |
| variable 计算 | 今天 - 昨天 | 今天 - 昨天 |
| 保留小数位 | 2 位 | 2 位 |
| 忽略用户传入的 variable | ✅ | ✅ |
| 忽略用户传入的 balance_history | ✅ | ✅ |

## 📁 修改的文件

1. `backend/app/utils/redis_queue.py`
   - 在 `_process_batch()` 方法中添加 balance 计算逻辑
   - 过滤掉用户传入的 variable 和 balance_history
   - 更新记录时自动计算这两个字段

2. `backend/test_balance_calculation.py`（新增）
   - 自动化测试脚本
   - 测试 4 个场景

3. `docs/fixes/BALANCE_AUTO_CALCULATION_IN_QUEUE.md`（本文档）
   - 功能说明文档

## 💡 最佳实践

### 1. 只传入 balance

推荐只传入 balance，让系统自动计算其他字段：

```json
{
  "account": "test",
  "balance": 100,
  "project_id": "xxx"
}
```

### 2. 不要传入 variable 和 balance_history

这两个字段会被忽略，传入也没有意义：

```json
// ❌ 不推荐
{
  "account": "test",
  "balance": 100,
  "variable": 50,  // 会被忽略
  "balance_history": {...},  // 会被忽略
  "project_id": "xxx"
}

// ✅ 推荐
{
  "account": "test",
  "balance": 100,
  "project_id": "xxx"
}
```

### 3. 定期更新 balance

建议每天更新一次 balance，这样可以：
- 保持 balance_history 的准确性
- 正确计算 variable
- 追踪余额变化趋势

### 4. 监控 balance_history

定期检查 balance_history 是否正常：

```bash
# 查询账号的 balance_history
curl 'http://127.0.0.1:6080/v1/project/account?account=test' \
  -H 'Authorization: Bearer TOKEN' | jq '.items[0].balance_history'
```

## 📅 更新信息

- **更新时间**: 2026-01-23
- **需求**: 在 Redis 队列处理中添加 balance 自动计算
- **实现**: 自动计算 variable 和 balance_history，忽略用户传入的值
- **状态**: ✅ 已完成

---

**相关文档**:
- [Redis 缓存数据库分离](REDIS_CACHE_DB_SEPARATION.md)
- [Upsert Redis 队列更新总结](../../UPSERT_REDIS_QUEUE_UPDATE.md)
- [项目账号 CRUD](../../backend/app/crud/project/account.py)
