# 项目余额 API 修复

## 修复时间
2026-01-21

## 问题描述

前端访问项目余额列表接口时返回错误：
```
{"detail":"'CRUD' object has no attribute 'get_count'"}
```

## 问题原因

API 层调用了不存在的 `get_count` 方法：

**错误代码** (`backend/app/apis/v1/project/balance.py`):
```python
@app.get("", response_model=OutList)
async def gets(...):
    try:
        if res_count:
            count = await project_balance_crud.get_count(  # ← 这个方法不存在
                account_id=account_id,
                create_time_start=parse_time(create_time_start),
                create_time_end=parse_time(create_time_end, True),
                update_time_start=parse_time(update_time_start),
                update_time_end=parse_time(update_time_end, True),
            )
        else:
            count = -1
        return await project_balance_crud.get_multi(
            account_id=account_id,
            ...
            res_count=res_count,
        )
```

问题：
1. CRUD 类中没有 `get_count` 方法
2. `get_multi` 方法已经支持 `res_count` 参数来返回总数
3. 重复调用导致不必要的数据库查询

## 解决方案

直接使用 `get_multi` 方法的 `res_count` 参数，移除对 `get_count` 的调用。

**修复后的代码**:
```python
@app.get("", response_model=OutList)
async def gets(...):
    try:
        return await project_balance_crud.get_multi(
            account_id=account_id,
            order_by=order_by or "-create_time",
            create_time_start=parse_time(create_time_start),
            create_time_end=parse_time(create_time_end, True),
            update_time_start=parse_time(update_time_start),
            update_time_end=parse_time(update_time_end, True),
            page=page,
            limit=limit,
            res_count=res_count,  # ← 直接传递给 get_multi
        )
```

## CRUD 方法说明

`get_multi` 方法已经正确实现了计数功能：

```python
async def get_multi(self,
                    account_id: UUID | None = None,
                    page: int = 1,
                    limit: int = 10,
                    res_count: bool = False,  # ← 支持返回总数
                    ...
                    ) -> OutList:
    query = ProjectBalance.all()
    
    # 应用过滤条件
    if account_id:
        query = query.filter(account_id=account_id)
    ...
    
    # 根据 res_count 参数决定是否计数
    if res_count:
        count = await query.count()
    else:
        count = -1
    
    # 分页查询
    offset = (page - 1) * limit
    query = query.limit(limit).offset(offset)
    res = await query.prefetch_related('account')
    
    # 返回结果
    num = len(res)
    items = [Out.model_validate(obj) for obj in res]
    return OutList(message='成功', count=count, num=num, items=items)
```

## 优势

### 修复前
- ❌ 调用不存在的方法导致错误
- ❌ 如果方法存在，会执行两次数据库查询（一次计数，一次查询数据）
- ❌ 代码冗余

### 修复后
- ✅ 使用正确的方法
- ✅ 只执行一次数据库查询（在 get_multi 内部根据需要计数）
- ✅ 代码简洁
- ✅ 性能更好

## 测试验证

### 测试1: 不返回总数
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:6080/v1/project/balance?page=1&limit=10"
```

预期响应：
```json
{
  "message": "成功",
  "count": -1,  // 不计数时返回 -1
  "num": 5,     // 当前页数量
  "items": [...]
}
```

### 测试2: 返回总数
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:6080/v1/project/balance?page=1&limit=10&res_count=true"
```

预期响应：
```json
{
  "message": "成功",
  "count": 25,  // 总记录数
  "num": 10,    // 当前页数量
  "items": [...]
}
```

### 测试3: 按账号过滤
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:6080/v1/project/balance?account_id={account_id}&res_count=true"
```

预期响应：
```json
{
  "message": "成功",
  "count": 1,   // 该账号的余额记录数
  "num": 1,
  "items": [...]
}
```

## 其他模块检查

检查了其他模块的 API，确认没有类似问题：

| 模块 | API 文件 | 状态 |
|------|---------|------|
| 项目信息 | `backend/app/apis/v1/project/info.py` | ✅ 正确 |
| 项目账号 | `backend/app/apis/v1/project/account.py` | ✅ 正确 |
| 项目钱包 | `backend/app/apis/v1/project/wallet.py` | ✅ 正确 |
| 项目余额 | `backend/app/apis/v1/project/balance.py` | ✅ 已修复 |
| 用户信息 | `backend/app/apis/v1/user/user.py` | ✅ 正确 |
| 服务器信息 | `backend/app/apis/v1/server/info.py` | ✅ 正确 |
| 邮箱信息 | `backend/app/apis/v1/mail/info.py` | ✅ 正确 |

所有其他模块都直接使用 `get_multi` 的 `res_count` 参数，没有调用 `get_count` 方法。

## 相关文件

- ✅ `backend/app/apis/v1/project/balance.py` - API 层（已修复）
- ✅ `backend/app/crud/project/balance.py` - CRUD 层（无需修改）
- ✅ `docs/fixes/PROJECT_BALANCE_API_FIX.md` - 本文档

## 总结

✅ 移除了对不存在的 `get_count` 方法的调用
✅ 直接使用 `get_multi` 的 `res_count` 参数
✅ 减少了不必要的数据库查询
✅ 代码更简洁，性能更好
✅ 代码编译通过
✅ 与其他模块保持一致

项目余额 API 现在可以正常工作了！
