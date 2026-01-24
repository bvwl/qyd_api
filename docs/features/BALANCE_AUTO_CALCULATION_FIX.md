# Balance 自动计算修复完成

## 问题描述

POST `/v1/project/account` 创建接口传入 `balance` 后，`variable` 和 `balance_history` 没有正确设置。

## 根本原因

1. 后端代码修改后没有重启，导致代码未生效
2. 首次创建时 `variable` 计算逻辑不正确（应该等于 balance，而不是 0）
3. `Decimal` 类型转换不一致

## 修复内容

### 1. 修复 `create` 方法（POST 创建接口）

**文件**: `backend/app/crud/project/account.py`

```python
# 如果传入了 balance，需要更新 variable 和 balance_history
if 'balance' in filtered_item:
    new_balance = Decimal(str(filtered_item['balance']))
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 初始化 balance_history（首次创建只有今天的记录）
    balance_history = {today: float(new_balance.quantize(Decimal('0.000001')))}
    
    # 首次创建，variable 等于 balance（从0增加到balance）
    variable = new_balance.quantize(Decimal('0.01'))
    
    # 使用 update 方法更新字段
    await ProjectAccount.filter(id=res.id).update(
        balance_history=balance_history,
        variable=variable
    )
    
    # 重新查询
    res = await ProjectAccount.get(id=res.id)
```

### 2. 修复 `update` 方法

```python
# 实时计算变动余额：当前余额 - 昨天的余额
if len(res.balance_history) >= 2:
    dates = list(res.balance_history.keys())
    today_balance = Decimal(str(res.balance_history[dates[0]]))
    yesterday_balance = Decimal(str(res.balance_history[dates[1]]))
    update_data['variable'] = (today_balance - yesterday_balance).quantize(Decimal('0.01'))
else:
    # 只有今天的记录，variable 等于 balance（从0增加到balance）
    update_data['variable'] = new_balance.quantize(Decimal('0.01'))
```

### 3. 修复 `upsert` 方法

同样的逻辑应用到 `upsert` 方法中。

### 4. 添加必要的导入

```python
from decimal import Decimal
```

## 修复逻辑

### Balance 自动计算规则

1. **首次创建**（只有1天记录）：
   - `variable = balance`（从0增加到balance）
   - `balance_history = {today: balance}`

2. **更新记录**（有2天或以上记录）：
   - `variable = 今天余额 - 昨天余额`
   - `balance_history` 保留最近7天，同一天覆盖

3. **小数位精度**：
   - `balance`: 6位小数
   - `balance_history`: 6位小数
   - `variable`: 2位小数

## 测试方法

### 1. 重启后端服务

```bash
cd backend
python start.py
```

### 2. 测试创建接口

```bash
curl 'http://127.0.0.1:6080/v1/project/account' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "account":"test@example.com",
    "password":"password123",
    "account_type":1,
    "status":1,
    "project_id":"YOUR_PROJECT_ID",
    "balance":444
  }'
```

### 3. 验证结果

返回的数据应该包含：
- `balance`: "444.000000"
- `variable`: "444.00"（首次创建，等于balance）
- `balance_history`: {"2026-01-24": 444.0}

### 4. 测试更新接口（第二天）

```bash
curl 'http://127.0.0.1:6080/v1/project/account/upsert' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "account":"test@example.com",
    "project_id":"YOUR_PROJECT_ID",
    "balance":500
  }'
```

返回的数据应该包含：
- `balance`: "500.000000"
- `variable`: "56.00"（500 - 444）
- `balance_history`: {"2026-01-24": 500.0, "2026-01-23": 444.0}

## 与 Redis 队列的一致性

现在 CRUD 的 `create`、`update`、`upsert` 方法与 Redis 队列处理逻辑完全一致：

1. ✅ 首次创建：`variable = balance`
2. ✅ 更新记录：`variable = 今天余额 - 昨天余额`
3. ✅ 小数位精度：balance 6位，variable 2位
4. ✅ 历史记录：保留最近7天，同一天覆盖

## 相关文件

- `backend/app/crud/project/account.py` - CRUD 操作（已修复）
- `backend/app/utils/redis_queue.py` - Redis 队列处理（参考实现）
- `backend/app/apis/v1/project/account.py` - API 接口

## 注意事项

1. **必须重启后端服务**才能使代码生效
2. 不要传入 `variable` 和 `balance_history`，系统会自动计算
3. 只有传入 `balance` 时才会触发自动计算
4. 小数位精度已统一：balance 6位，variable 2位

## 完成状态

✅ 修复完成，等待后端重启测试
