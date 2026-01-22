# 余额自动计算逻辑

## 更新时间
2026-01-21

## 功能描述

项目账号的余额字段支持实时自动计算：
- 只需传入 `balance`（当前余额）
- `variable`（变动余额）实时计算：当前余额 - 昨天的余额
- `balance_history` 实时更新，保留最近7天

## 设计理念

与之前的积分系统不同，这里采用**实时更新**策略：
- 用户只需要更新当前余额
- 系统实时记录历史并计算变动
- 同一天多次更新会覆盖当天的记录（实时更新）
- 变动余额始终是：当前余额 - 昨天的余额

## 数据结构

### balance_history 格式

```json
{
  "2026-01-21": 1000.50,
  "2026-01-20": 950.00,
  "2026-01-19": 900.00,
  "2026-01-18": 850.00,
  "2026-01-17": 800.00,
  "2026-01-16": 750.00,
  "2026-01-15": 700.00
}
```

- **Key**: 日期（YYYY-MM-DD 格式）
- **Value**: 当天的余额
- **保留**: 最近7天的记录

## 实现逻辑

### 1. 创建账号

```python
async def create(self, item: Create) -> Out:
    data['balance'] = item.balance if item.balance is not None else 0
    data['variable'] = 0  # 创建时变动余额为0
    data['balance_history'] = {}  # 创建时历史为空
    
    res = await ProjectAccount.create(**data)
    return Out.model_validate(res)
```

**说明**：
- 如果不传 `balance`，默认为 0
- 创建时 `variable` 为 0（没有历史数据可比较）
- 创建时 `balance_history` 为空字典

### 2. 更新余额

```python
async def update(self, id: UUID, item: Update) -> Out:
    if item.balance is not None:
        new_balance = item.balance
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 初始化 balance_history
        if res.balance_history is None:
            res.balance_history = {}
        
        # 实时更新当天的余额记录（覆盖）
        res.balance_history[today] = float(new_balance)
        
        # 按日期排序并保留最近7条记录
        sorted_data = dict(sorted(res.balance_history.items(), key=lambda x: x[0], reverse=True))
        res.balance_history = dict(list(sorted_data.items())[:7])
        
        # 实时计算变动余额：当前余额 - 昨天的余额
        if len(res.balance_history) >= 2:
            dates = list(res.balance_history.keys())
            today_balance = res.balance_history[dates[0]]  # 今天的余额（最新）
            yesterday_balance = res.balance_history[dates[1]]  # 昨天的余额
            update_data['variable'] = today_balance - yesterday_balance
        else:
            update_data['variable'] = 0
        
        update_data['balance'] = new_balance
        update_data['balance_history'] = res.balance_history
```

**关键点**：
1. **实时更新历史**：每次更新都会覆盖当天的记录
2. **保留最近7天**：按日期倒序排序，只保留前7条
3. **实时计算变动**：当前余额 - 昨天的余额
4. **处理边界情况**：如果历史记录少于2条，变动为0

### 3. Upsert（创建或更新）

```python
async def upsert(self, item: Create) -> Out:
    existing = await ProjectAccount.get_or_none(
        account=item.account,
        project_id=item.project_id
    )
    
    if existing:
        # 如果记录存在，实时更新余额
        # 实时计算变动余额和更新历史
        ...
    else:
        # 如果记录不存在，创建新记录
        return await self.create(item)
```

## 使用示例

### 示例1: 创建账号（不传余额）

```bash
POST /v1/project/account
{
  "account": "test@example.com",
  "project_id": "xxx"
}

# 响应
{
  "id": "xxx",
  "account": "test@example.com",
  "balance": 0,           # 默认值
  "variable": 0,          # 默认值
  "balance_history": {},  # 空字典
  ...
}
```

### 示例2: 第一次更新余额

```bash
PUT /v1/project/account/{id}
{
  "balance": 1000.50
}

# 响应
{
  "id": "xxx",
  "account": "test@example.com",
  "balance": 1000.50,
  "variable": 0,  # 只有一天的记录，无法计算变动
  "balance_history": {
    "2026-01-21": 1000.50
  },
  ...
}
```

### 示例3: 第二天更新余额

```bash
PUT /v1/project/account/{id}
{
  "balance": 1050.00
}

# 响应
{
  "id": "xxx",
  "account": "test@example.com",
  "balance": 1050.00,
  "variable": 49.50,  # 1050.00 - 1000.50 = 49.50
  "balance_history": {
    "2026-01-22": 1050.00,
    "2026-01-21": 1000.50
  },
  ...
}
```

### 示例3: 同一天多次更新（实时更新）

```bash
# 第一次更新（上午10点）
PUT /v1/project/account/{id}
{
  "balance": 1000.00
}
# 响应
{
  "balance": 1000.00,
  "variable": 0,  # 假设昨天没有记录
  "balance_history": {
    "2026-01-21": 1000.00
  }
}

# 第二次更新（下午2点）
PUT /v1/project/account/{id}
{
  "balance": 1100.00
}
# 响应（实时更新）
{
  "balance": 1100.00,
  "variable": 0,  # 假设昨天没有记录
  "balance_history": {
    "2026-01-21": 1100.00  # 覆盖了上午的记录
  }
}

# 第三次更新（晚上8点）
PUT /v1/project/account/{id}
{
  "balance": 1050.00
}
# 响应（实时更新）
{
  "balance": 1050.00,
  "variable": 0,  # 假设昨天没有记录
  "balance_history": {
    "2026-01-21": 1050.00  # 再次覆盖
  }
}
```

### 示例5: 8天后的历史记录

```bash
# 连续8天更新余额
Day 1: 1000.00
Day 2: 1050.00
Day 3: 1100.00
Day 4: 1150.00
Day 5: 1200.00
Day 6: 1250.00
Day 7: 1300.00
Day 8: 1350.00

# balance_history 只保留最近7天
{
  "2026-01-28": 1350.00,  # Day 8
  "2026-01-27": 1300.00,  # Day 7
  "2026-01-26": 1250.00,  # Day 6
  "2026-01-25": 1200.00,  # Day 5
  "2026-01-24": 1150.00,  # Day 4
  "2026-01-23": 1100.00,  # Day 3
  "2026-01-22": 1050.00   # Day 2
  # Day 1 的记录被删除
}

# variable = 1350.00 - 1300.00 = 50.00
```

## 计算规则

### 变动余额计算

```python
if len(balance_history) >= 2:
    dates = sorted(balance_history.keys(), reverse=True)  # 按日期倒序
    today_balance = balance_history[dates[0]]      # 今天的余额（最新）
    yesterday_balance = balance_history[dates[1]]  # 昨天的余额
    variable = today_balance - yesterday_balance   # 实时计算
else:
    variable = 0  # 历史记录不足，无法计算
```

**说明**：
- `today_balance` 是当前余额（实时更新）
- `yesterday_balance` 是昨天的余额
- 同一天多次更新，`today_balance` 会实时变化，`variable` 也会实时变化

### 历史记录保留

```python
# 按日期倒序排序
sorted_data = dict(sorted(balance_history.items(), key=lambda x: x[0], reverse=True))

# 只保留最近7条
balance_history = dict(list(sorted_data.items())[:7])
```

## 优势

### 1. 自动化

- ✅ 用户只需传入当前余额
- ✅ 系统实时计算变动
- ✅ 系统实时维护历史

### 2. 数据准确

- ✅ 实时更新，数据最新
- ✅ 按日期排序，保证顺序正确
- ✅ 自动清理旧数据，保持数据量稳定

### 3. 性能优化

- ✅ 只保留7天数据，减少存储
- ✅ 使用 JSON 字段，查询高效
- ✅ 计算在更新时完成，查询时无需计算

### 4. 易于使用

- ✅ API 简单，只需传 balance
- ✅ 前端无需关心计算逻辑
- ✅ 历史数据实时更新

## 边界情况处理

### 情况1: 首次创建账号

```python
balance = 0
variable = 0
balance_history = {}
```

### 情况2: 第一次更新余额

```python
balance = 1000.00
variable = 0  # 只有一天记录，无法计算
balance_history = {"2026-01-21": 1000.00}
```

### 情况3: 同一天多次更新（实时更新）

```python
# 第一次更新（上午）
balance_history["2026-01-21"] = 1000.00
balance = 1000.00
variable = 0  # 假设昨天没有记录

# 第二次更新（下午）- 实时覆盖
balance_history["2026-01-21"] = 1100.00  # 覆盖上午的值
balance = 1100.00
variable = 0  # 假设昨天没有记录

# 第三次更新（晚上）- 实时覆盖
balance_history["2026-01-21"] = 1050.00  # 再次覆盖
balance = 1050.00
variable = 0  # 假设昨天没有记录
```

**说明**：同一天多次更新会实时覆盖当天的历史记录

### 情况4: balance_history 为 None

```python
if res.balance_history is None:
    res.balance_history = {}
```

### 情况5: 超过7天的记录

```python
# 自动删除最旧的记录
sorted_data = dict(sorted(balance_history.items(), key=lambda x: x[0], reverse=True))
balance_history = dict(list(sorted_data.items())[:7])
```

## 前端展示

### 余额趋势图

可以使用 `balance_history` 绘制7天的余额趋势：

```typescript
const chartData = Object.entries(account.balance_history).map(([date, balance]) => ({
  date,
  balance: Number(balance)
}))

// 使用 Chart.js 或 ECharts 绘制折线图
```

### 变动提示

```typescript
const variable = Number(account.variable)
const color = variable > 0 ? 'green' : variable < 0 ? 'red' : 'gray'
const icon = variable > 0 ? '↑' : variable < 0 ? '↓' : '—'

<span style={{ color }}>
  {icon} {Math.abs(variable).toFixed(2)}
</span>
```

## 注意事项

1. **时区问题**: 使用服务器时区的日期，确保一致性
2. **实时更新**: 同一天多次更新会覆盖当天的历史记录
3. **数据类型**: balance_history 中的值为 float，需要转换
4. **历史清理**: 自动保留最近7天，无需手动清理
5. **变动计算**: 始终是当前余额 - 昨天的余额（实时计算）

## 相关文件

### 后端文件
- ✅ `backend/app/crud/project/account.py` - 实现自动计算逻辑
- ✅ `backend/app/schemas/project/account.py` - balance 为可选字段
- ✅ `backend/app/models/project.py` - balance 有默认值

### 文档
- ✅ `docs/fixes/BALANCE_AUTO_CALCULATION.md` - 本文档
- ✅ `docs/fixes/MERGE_BALANCE_INTO_ACCOUNT.md` - 合并余额表文档

## 总结

✅ 只需传入 balance，variable 实时计算
✅ balance_history 实时更新，保留最近7天
✅ 同一天多次更新会覆盖当天的记录（实时更新）
✅ 变动余额始终是：当前余额 - 昨天的余额
✅ 边界情况处理完善
✅ 前端可以绘制余额趋势图
✅ 代码逻辑清晰，易于维护

这个设计采用**实时更新**策略，确保数据始终是最新的！
