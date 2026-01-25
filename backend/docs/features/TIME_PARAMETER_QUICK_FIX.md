# 时间参数查询错误 - 快速修复指南

## 问题

```json
{"detail":"strptime() argument 1 must be str, not datetime.datetime"}
```

## 原因

API层和CRUD层都调用了 `parse_time()`，导致重复解析。

## 解决方案

**只在CRUD层调用 `parse_time()`，API层直接传递原始参数。**

## 修复步骤

### 1. 运行自动修复脚本

```bash
python backend/fix_time_parameter_issue.py
```

### 2. 验证修复

```bash
# 测试parse_time函数
python backend/test_time_parameter_fix.py

# 测试API接口（需要先启动后端）
bash backend/test_api_time_query.sh
```

## 代码示例

### ❌ 错误写法

```python
# API层
return await crud.get_multi(
    create_time_start=parse_time(create_time_start),  # 错误！
)
```

### ✅ 正确写法

```python
# API层
return await crud.get_multi(
    create_time_start=create_time_start,  # 正确！
)

# CRUD层会统一处理
if create_time_start:
    query = query.filter(create_time__gte=parse_time(create_time_start))
```

## 支持的格式

- 日期: `2026-01-25`
- 日期时间: `2026-01-25 10:30:00`
- 时间戳(秒): `1737792000`
- 时间戳(毫秒): `1737792000000`

## 修复文件

已修复 9 个文件，7 个文件本来就是正确的。

详细信息见：`TIME_PARAMETER_FIX.md` 或 `时间参数查询错误修复总结.md`
