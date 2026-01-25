# 时间参数查询错误修复

## 问题描述

在前端调用带时间参数的查询接口时，后端返回错误：

```json
{"detail":"strptime() argument 1 must be str, not datetime.datetime"}
```

### 错误示例

```bash
curl 'http://127.0.0.1:6080/v1/project/account?update_time_start=2026-01-25&update_time_end=2026-01-25'
```

返回：
```json
{"detail":"strptime() argument 1 must be str, not datetime.datetime"}
```

## 问题原因

代码存在**重复解析时间参数**的问题：

1. **API 层**：接收字符串参数后，调用 `parse_time()` 将其转换为 `datetime` 对象
2. **CRUD 层**：再次调用 `parse_time()` 处理已经是 `datetime` 对象的参数

由于 `parse_time()` 函数内部使用 `datetime.strptime()` 解析字符串，当传入的参数已经是 `datetime` 对象时，就会抛出类型错误。

### 错误代码示例

**API 层 (backend/app/apis/v1/project/account.py)**:
```python
# ❌ 错误：在API层调用parse_time()
return await project_account_crud.get_multi(
    create_time_start=parse_time(create_time_start),  # 转换为datetime
    create_time_end=parse_time(create_time_end, True),
    update_time_start=parse_time(update_time_start),
    update_time_end=parse_time(update_time_end, True),
    ...
)
```

**CRUD 层 (backend/app/crud/project/account.py)**:
```python
# ❌ 错误：再次调用parse_time()，但参数已经是datetime对象
if create_time_start:
    query = query.filter(create_time__gte=parse_time(create_time_start))  # 失败！
if create_time_end:
    query = query.filter(create_time__lte=parse_time(create_time_end, is_end=True))
```

## 解决方案

**移除 API 层的 `parse_time()` 调用，让 CRUD 层统一处理时间参数解析。**

这样做的好处：
1. 符合分层架构原则：API 层负责接收参数，CRUD 层负责数据处理
2. 避免重复解析
3. 统一时间处理逻辑

### 修复后的代码

**API 层**:
```python
# ✅ 正确：直接传递原始参数
return await project_account_crud.get_multi(
    create_time_start=create_time_start,  # 保持字符串
    create_time_end=create_time_end,
    update_time_start=update_time_start,
    update_time_end=update_time_end,
    ...
)
```

**CRUD 层**:
```python
# ✅ 正确：统一在CRUD层解析
if create_time_start:
    query = query.filter(create_time__gte=parse_time(create_time_start))
if create_time_end:
    query = query.filter(create_time__lte=parse_time(create_time_end, is_end=True))
```

## 修复范围

使用自动化脚本 `backend/fix_time_parameter_issue.py` 修复了以下 9 个 API 文件：

1. `app/apis/v1/mail/outlook.py`
2. `app/apis/v1/server/info.py`
3. `app/apis/v1/user/user.py`
4. `app/apis/v1/user/route.py`
5. `app/apis/v1/project/withdrawal.py`
6. `app/apis/v1/project/info.py`
7. `app/apis/v1/project/balance.py`
8. `app/apis/v1/project/account.py`
9. `app/apis/v1/project/wallet.py`

以下文件在修复前已经是正确的（直接传递原始参数）：

10. `app/apis/v1/mail/info.py`
11. `app/apis/v1/user/log.py`
12. `app/apis/v1/user/token.py`
13. `app/apis/v1/user/role.py`
14. `app/apis/v1/server/account.py`
15. `app/apis/v1/server/group.py`
16. `app/apis/v1/server/country.py`

## 影响的 CRUD 文件

以下 CRUD 文件保持不变（它们的逻辑是正确的）：

- `app/crud/project/account.py`
- `app/crud/project/withdrawal.py`
- `app/crud/project/info.py`
- `app/crud/project/balance.py`
- `app/crud/project/wallet.py`
- `app/crud/mail/info.py`
- `app/crud/server/info.py`
- `app/crud/server/account.py`
- `app/crud/server/group.py`
- `app/crud/server/country.py`
- `app/crud/user/user.py`
- `app/crud/user/role.py`
- `app/crud/user/route.py`
- `app/crud/user/token.py`
- `app/crud/user/log.py`

## 验证

### 测试脚本

运行 `backend/test_time_parameter_fix.py` 验证 `parse_time()` 函数的行为：

```bash
python backend/test_time_parameter_fix.py
```

### 手动测试

```bash
# 测试日期格式
curl 'http://127.0.0.1:6080/v1/project/account?update_time_start=2026-01-25&update_time_end=2026-01-25'

# 测试日期时间格式
curl 'http://127.0.0.1:6080/v1/project/account?update_time_start=2026-01-25%2010:00:00&update_time_end=2026-01-25%2023:59:59'

# 测试时间戳格式
curl 'http://127.0.0.1:6080/v1/project/account?update_time_start=1737792000000&update_time_end=1737878399000'
```

## 支持的时间格式

`parse_time()` 函数支持以下格式：

1. **日期格式**: `YYYY-MM-DD`
   - 示例: `2026-01-25`
   - 开始时间: `2026-01-25 00:00:00`
   - 结束时间: `2026-01-25 23:59:59.999999`

2. **日期时间格式**: `YYYY-MM-DD HH:mm:ss`
   - 示例: `2026-01-25 10:30:00`

3. **10位时间戳**（秒）
   - 示例: `1737792000`

4. **13位时间戳**（毫秒）
   - 示例: `1737792000000`

## 最佳实践

### API 层开发规范

```python
@app.get("", response_model=OutList)
async def gets(
    # 时间参数定义
    create_time_start: str | int | None = Query(
        None,
        description="创建时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    create_time_end: str | int | None = Query(
        None,
        description="创建时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    ...
):
    # ✅ 正确：直接传递原始参数给CRUD层
    return await crud.get_multi(
        create_time_start=create_time_start,
        create_time_end=create_time_end,
        ...
    )
```

### CRUD 层开发规范

```python
async def get_multi(
    self,
    create_time_start: str | int | None = None,
    create_time_end: str | int | None = None,
    ...
) -> OutList:
    query = Model.all()
    
    # ✅ 正确：在CRUD层统一调用parse_time()
    if create_time_start:
        query = query.filter(create_time__gte=parse_time(create_time_start))
    if create_time_end:
        query = query.filter(create_time__lte=parse_time(create_time_end, is_end=True))
    
    ...
```

## 相关文件

- 修复脚本: `backend/fix_time_parameter_issue.py`
- 测试脚本: `backend/test_time_parameter_fix.py`
- 时间工具: `backend/app/utils/time_tool.py`
- 本文档: `TIME_PARAMETER_FIX.md`

## 总结

这次修复解决了所有时间参数查询接口的错误，确保了：

1. ✅ 时间参数只在 CRUD 层解析一次
2. ✅ API 层保持简洁，只负责参数传递
3. ✅ 支持多种时间格式（日期、日期时间、时间戳）
4. ✅ 所有相关接口统一修复，避免遗漏

修复日期: 2026-01-25
