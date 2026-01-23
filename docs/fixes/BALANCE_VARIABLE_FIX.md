# Balance Variable 计算修复

## 📋 问题描述

用户发现首次创建账号时，传入 `balance=10`，但结果显示：
```json
{
  "balance": "10.000000",
  "variable": "0.000000",      // ❌ 错误：应该是 10
  "balance_history": null       // ❌ 错误：应该有当天记录
}
```

**预期结果**：
```json
{
  "balance": "10.000000",
  "variable": "10.000000",      // ✅ 正确：从0增加到10
  "balance_history": {
    "2026-01-23": 10.0          // ✅ 正确：记录当天余额
  }
}
```

## 🔍 问题原因

在 Redis 队列处理和 CRUD 的创建逻辑中，首次创建时：
1. `variable` 被设置为 `0`，但应该等于 `balance`（因为是从 0 增加到 balance）
2. `balance_history` 没有被正确初始化

## ✅ 修复方案

### 1. 修复 Redis 队列处理

**文件**: `backend/app/utils/redis_queue.py`

**修改前**:
```python
# 创建新记录
if 'balance' in filtered_item:
    new_balance = Decimal(str(filtered_item['balance']))
    today = datetime.now().strftime('%Y-%m-%d')
    
    filtered_item['balance_history'] = {today: float(new_balance)}
    filtered_item['variable'] = Decimal('0.00')  # ❌ 错误
```

**修改后**:
```python
# 创建新记录
if 'balance' in filtered_item:
    new_balance = Decimal(str(filtered_item['balance']))
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 初始化 balance_history（记录当天的余额）
    filtered_item['balance_history'] = {today: float(new_balance)}
    # 创建时变动余额等于当前余额（从0增加到balance）
    filtered_item['variable'] = new_balance.quantize(Decimal('0.01'))  # ✅ 正确
```

### 2. 修复 CRUD 创建逻辑

**文件**: `backend/app/crud/project/account.py`

**修改前**:
```python
# 余额字段：如果传入则使用，否则使用默认值0
data['balance'] = item.balance if item.balance is not None else 0
data['variable'] = 0  # ❌ 错误
data['balance_history'] = {}  # ❌ 错误
```

**修改后**:
```python
# 余额字段：如果传入则使用，否则使用默认值0
if item.balance is not None:
    balance = Decimal(str(item.balance))
    today = datetime.now().strftime('%Y-%m-%d')
    
    data['balance'] = balance
    # 创建时变动余额等于当前余额（从0增加到balance）
    data['variable'] = balance  # ✅ 正确
    # 创建时记录当天的余额
    data['balance_history'] = {today: float(balance)}  # ✅ 正确
else:
    data['balance'] = 0
    data['variable'] = 0
    data['balance_history'] = {}
```

## 📊 计算逻辑说明

### variable（变动余额）计算规则

| 场景 | 计算公式 | 示例 |
|------|---------|------|
| 首次创建 | `variable = balance` | balance=100 → variable=100 |
| 更新记录（有历史） | `variable = 今天余额 - 昨天余额` | 今天150，昨天100 → variable=50 |
| 更新记录（无历史） | `variable = balance` | balance=100 → variable=100 |

### balance_history（余额历史）维护规则

1. **首次创建**：记录当天日期和余额
   ```json
   {"2026-01-23": 100.0}
   ```

2. **同一天更新**：覆盖当天的记录
   ```json
   // 第一次
   {"2026-01-23": 100.0}
   
   // 第二次（同一天）
   {"2026-01-23": 150.0}  // 覆盖
   ```

3. **跨天更新**：新增记录，保留最近 7 天
   ```json
   {
     "2026-01-24": 200.0,  // 新增
     "2026-01-23": 150.0,
     "2026-01-22": 100.0,
     ...  // 最多保留7条
   }
   ```

## 🧪 测试验证

### 测试脚本

```bash
# 运行快速测试
./test_balance_fix.sh
```

### 手动测试

```bash
# 1. 首次创建
curl -X POST 'http://127.0.0.1:6080/v1/project/account/upsert' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "account": "test_balance",
    "balance": 100,
    "project_id": "YOUR_PROJECT_ID"
  }'

# 2. 等待队列处理
sleep 5

# 3. 查询结果
curl 'http://127.0.0.1:6080/v1/project/account?account=test_balance' \
  -H 'Authorization: Bearer YOUR_TOKEN' | jq '.items[0] | {
    balance: .balance,
    variable: .variable,
    balance_history: .balance_history
  }'

# 预期输出：
# {
#   "balance": "100.000000",
#   "variable": "100.000000",
#   "balance_history": {
#     "2026-01-23": 100.0
#   }
# }
```

### 测试场景

#### 场景1：首次创建（传入 balance=100）

**请求**:
```json
{
  "account": "test",
  "balance": 100,
  "project_id": "xxx"
}
```

**预期结果**:
```json
{
  "balance": "100.000000",
  "variable": "100.000000",
  "balance_history": {
    "2026-01-23": 100.0
  }
}
```

#### 场景2：同一天第二次更新（balance=150）

**请求**:
```json
{
  "account": "test",
  "balance": 150,
  "project_id": "xxx"
}
```

**预期结果**:
```json
{
  "balance": "150.000000",
  "variable": "150.000000",  // 因为只有今天的记录
  "balance_history": {
    "2026-01-23": 150.0  // 覆盖之前的100
  }
}
```

#### 场景3：第二天更新（balance=200）

**请求**（假设第二天）:
```json
{
  "account": "test",
  "balance": 200,
  "project_id": "xxx"
}
```

**预期结果**:
```json
{
  "balance": "200.000000",
  "variable": "50.000000",  // 200 - 150 = 50
  "balance_history": {
    "2026-01-24": 200.0,
    "2026-01-23": 150.0
  }
}
```

## 📁 修改的文件

1. `backend/app/utils/redis_queue.py`
   - 修复创建新记录时的 variable 和 balance_history 初始化

2. `backend/app/crud/project/account.py`
   - 修复 create() 方法中的 variable 和 balance_history 初始化

3. `docs/fixes/BALANCE_AUTO_CALCULATION_IN_QUEUE.md`
   - 更新文档，说明首次创建时 variable = balance

4. `UPSERT_REDIS_QUEUE_UPDATE.md`
   - 更新总结文档

5. `backend/test_balance_calculation.py`
   - 更新测试脚本的预期结果

6. `test_balance_fix.sh`（新增）
   - 快速测试脚本

7. `docs/fixes/BALANCE_VARIABLE_FIX.md`（本文档）
   - 修复说明文档

## 💡 设计理念

### 为什么首次创建时 variable = balance？

**variable 表示余额变动**，即相对于之前的余额增加或减少了多少。

- **首次创建**：之前余额为 0，现在余额为 balance
  - 变动 = balance - 0 = balance
  - 所以 `variable = balance`

- **更新记录**：之前余额为昨天的余额，现在余额为今天的余额
  - 变动 = 今天余额 - 昨天余额
  - 所以 `variable = today_balance - yesterday_balance`

### 为什么要记录 balance_history？

1. **追踪余额变化趋势**：可以看到最近 7 天的余额变化
2. **计算 variable**：需要昨天的余额来计算变动
3. **数据审计**：保留历史记录，便于问题排查

## ⚠️ 注意事项

### 1. 同一天多次更新

同一天多次更新会覆盖 balance_history 中的记录：

```
第一次: balance=100 → balance_history={"2026-01-23": 100}
                     → variable=100

第二次: balance=150 → balance_history={"2026-01-23": 150}  // 覆盖
                     → variable=150  // 因为只有今天的记录
```

这是**预期行为**，因为我们只关心每天的最终余额。

### 2. variable 的含义

- **正数**：余额增加
  - 例如：variable=50 表示增加了 50
- **负数**：余额减少
  - 例如：variable=-20 表示减少了 20
- **首次创建**：等于 balance
  - 例如：balance=100, variable=100

### 3. 与之前版本的差异

| 版本 | 首次创建 variable | 首次创建 balance_history |
|------|------------------|-------------------------|
| 旧版本 | 0 | {} 或 null |
| 新版本 | balance | {today: balance} |

**升级影响**：
- 已有数据不受影响
- 新创建的数据会使用新逻辑
- 建议：如果需要，可以写脚本修复历史数据

## 📅 更新信息

- **更新时间**: 2026-01-23
- **问题**: 首次创建时 variable=0，balance_history=null
- **修复**: variable=balance，balance_history 记录当天余额
- **影响范围**: Redis 队列处理 + CRUD 创建
- **状态**: ✅ 已修复

---

**相关文档**:
- [Balance 自动计算详细文档](BALANCE_AUTO_CALCULATION_IN_QUEUE.md)
- [Upsert Redis 队列更新总结](../../UPSERT_REDIS_QUEUE_UPDATE.md)
- [Redis 缓存数据库分离](REDIS_CACHE_DB_SEPARATION.md)
