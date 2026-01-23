# Balance History 小数位修复

## 📋 问题描述

`balance` 字段是 `Decimal(18, 6)`，保留 6 位小数，但 `balance_history` 中存储的值只保留了默认的小数位数，导致精度不一致。

**示例**：
```json
{
  "balance": "10.123456",      // 6 位小数 ✅
  "balance_history": {
    "2026-01-23": 10.12        // 只有 2 位小数 ❌
  }
}
```

## ✅ 修复方案

使用 `Decimal.quantize()` 方法确保 `balance_history` 中的值也保留 6 位小数：

```python
# 修改前
record.balance_history[today] = float(new_balance)

# 修改后
record.balance_history[today] = float(new_balance.quantize(Decimal('0.000001')))
```

## 🧪 测试验证

### 测试1：创建记录

```bash
# 请求
curl -X POST '/v1/project/account/upsert' \
  -d '{"account":"test","balance":10.123456,"project_id":"xxx"}'

# 结果
{
  "balance": "10.123456",
  "variable": "10.120000",
  "balance_history": {
    "2026-01-23": 10.123456    // ✅ 6 位小数
  }
}
```

### 测试2：更新记录

```bash
# 请求
curl -X POST '/v1/project/account/upsert' \
  -d '{"account":"test","balance":20.987654,"project_id":"xxx"}'

# 结果
{
  "balance": "20.987654",
  "variable": "20.990000",
  "balance_history": {
    "2026-01-23": 20.987654    // ✅ 6 位小数
  }
}
```

## 📁 修改的文件

1. `backend/app/utils/redis_queue.py`
   - 更新记录时：`float(new_balance.quantize(Decimal('0.000001')))`
   - 创建记录时：`float(new_balance.quantize(Decimal('0.000001')))`

2. `backend/app/crud/project/account.py`
   - `create()` 方法：`float(balance.quantize(Decimal('0.000001')))`
   - `update()` 方法：`float(new_balance.quantize(Decimal('0.000001')))`
   - `upsert()` 方法：`float(new_balance.quantize(Decimal('0.000001')))`

## 💡 技术说明

### Decimal.quantize() 方法

```python
from decimal import Decimal

# 保留 6 位小数
value = Decimal('10.123456789')
result = value.quantize(Decimal('0.000001'))
# 结果：Decimal('10.123457')  # 四舍五入到 6 位

# 转换为 float 存储到 JSON
float_value = float(result)
# 结果：10.123457
```

### 为什么使用 float？

`balance_history` 是 JSON 字段，存储在数据库中：
- JSON 不支持 Decimal 类型
- 需要转换为 float 才能序列化
- 使用 `quantize()` 确保精度后再转换

## 📊 字段精度对比

| 字段 | 类型 | 小数位 | 示例 |
|------|------|--------|------|
| balance | Decimal(18, 6) | 6 位 | 10.123456 |
| variable | Decimal(18, 6) | 2 位 | 10.12 |
| balance_history | JSON (float) | 6 位 | {"2026-01-23": 10.123456} |

**注意**：`variable` 保留 2 位小数是因为代码中使用了 `quantize(Decimal('0.01'))`。

## 📅 更新信息

- **更新时间**: 2026-01-23
- **问题**: balance_history 小数位与 balance 不一致
- **修复**: 使用 quantize 保留 6 位小数
- **状态**: ✅ 已修复并测试通过

---

**相关文档**:
- [Balance Variable 计算修复](BALANCE_VARIABLE_FIX.md)
- [Balance 自动计算详细文档](BALANCE_AUTO_CALCULATION_IN_QUEUE.md)
- [Redis 缓存更新逻辑修复](REDIS_CACHE_UPDATE_LOGIC_FIX.md)
