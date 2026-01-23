# Upsert接口部分更新优化

## 更新内容

优化了项目账号的upsert接口，使其像PUT接口一样只更新传入的非空字段，避免覆盖现有数据。

## 问题背景

### 之前的问题

upsert接口在更新现有记录时，会将所有字段都更新，包括None值，导致：

```python
# 假设数据库中有记录：
{
    "account": "test@example.com",
    "password": "encrypted_password",
    "status": 1,
    "account_type": 1,
    "data": {"key": "value"},
    "balance": 100.00
}

# 如果只想更新balance，传入：
{
    "account": "test@example.com",
    "project_id": "xxx",
    "balance": 150.00
}

# 之前的结果：其他字段被清空
{
    "account": "test@example.com",
    "password": None,  # ❌ 被清空了
    "status": None,    # ❌ 被清空了
    "account_type": None,  # ❌ 被清空了
    "data": None,      # ❌ 被清空了
    "balance": 150.00
}
```

### 现在的行为

```python
# 现在的结果：只更新传入的字段
{
    "account": "test@example.com",
    "password": "encrypted_password",  # ✅ 保留原值
    "status": 1,                       # ✅ 保留原值
    "account_type": 1,                 # ✅ 保留原值
    "data": {"key": "value"},          # ✅ 保留原值
    "balance": 150.00                  # ✅ 更新为新值
}
```

## 实现方式

### 1. CRUD层优化 (`backend/app/crud/project/account.py`)

```python
async def upsert(self, item: Create) -> Out:
    """
    创建或更新项目账号
    - 如果记录存在，只更新传入的非空字段（类似PUT）
    - 如果记录不存在，创建新记录
    """
    existing = await ProjectAccount.get_or_none(
        account=item.account,
        project_id=item.project_id
    )
    
    if existing:
        # 只更新非空字段
        update_data = item.model_dump(
            exclude_unset=True,   # 排除未设置的字段
            exclude_none=True,    # 排除值为None的字段
            exclude={'balance', 'variable', 'balance_history', 'project_id', 'account'}
        )
        
        # 处理余额字段...
        
        if update_data:
            await existing.update_from_dict(update_data)
            await existing.save()
        
        return Out.model_validate(existing)
    else:
        # 创建新记录
        return await self.create(item)
```

**关键参数**：
- `exclude_unset=True`: 排除前端未传入的字段
- `exclude_none=True`: 排除值为None的字段
- `exclude={...}`: 排除特殊处理的字段（余额、唯一标识等）

### 2. Redis队列优化 (`backend/app/utils/redis_queue.py`)

```python
for item in uncached_items:
    key = tuple(item[field] for field in self.unique_fields)
    if key in existing_records:
        # 更新现有记录 - 只更新非空字段
        record = existing_records[key]
        has_update = False
        for field, value in item.items():
            # 跳过唯一字段和None值
            if field not in self.unique_fields and value is not None:
                setattr(record, field, value)
                has_update = True
        
        # 只有在有实际更新时才添加到更新列表
        if has_update:
            updates.append(record)
```

**优化点**：
- 跳过None值，不更新为空
- 跳过唯一标识字段，避免冲突
- 只有在有实际更新时才执行数据库操作

## 使用示例

### 单个upsert

```python
# 只更新balance字段
await project_account_crud.upsert(Create(
    account="test@example.com",
    project_id="xxx-xxx-xxx",
    balance=150.00  # 只传入要更新的字段
))

# 更新多个字段
await project_account_crud.upsert(Create(
    account="test@example.com",
    project_id="xxx-xxx-xxx",
    balance=150.00,
    status=2,
    data={"new_key": "new_value"}
))
```

### 批量upsert（Redis队列）

```bash
# API调用
POST /api/v1/project/account/batch-upsert
Content-Type: application/json

[
    {
        "account": "test1@example.com",
        "project_id": "xxx-xxx-xxx",
        "balance": 100.00
    },
    {
        "account": "test2@example.com",
        "project_id": "xxx-xxx-xxx",
        "balance": 200.00,
        "status": 2
    }
]
```

**处理流程**：
1. 数据添加到Redis队列
2. 后台worker异步处理
3. 查询现有记录（使用从库）
4. 只更新非空字段
5. 批量写入数据库（使用主库）

## 字段处理规则

### 普通字段

| 传入值 | 数据库现有值 | 更新结果 | 说明 |
|--------|-------------|---------|------|
| "new_value" | "old_value" | "new_value" | ✅ 更新为新值 |
| None | "old_value" | "old_value" | ✅ 保留原值 |
| 未传入 | "old_value" | "old_value" | ✅ 保留原值 |

### 特殊字段

#### 唯一标识字段（account, project_id）
- **不会被更新**
- 用于查找记录
- 即使传入也会被忽略

#### 余额字段（balance）
- **特殊处理**
- 更新时会自动计算变动余额（variable）
- 更新历史记录（balance_history）

#### 关联字段（server_id）
- 可以更新
- 传入None会保留原值
- 传入新值会更新

## 对比PUT接口

### 相同点

- ✅ 都只更新传入的非空字段
- ✅ 都使用 `exclude_unset=True` 和 `exclude_none=True`
- ✅ 都保留未传入字段的原值

### 不同点

| 特性 | PUT | UPSERT |
|------|-----|--------|
| 记录不存在 | 返回404错误 | 创建新记录 |
| 需要ID | 是（路径参数） | 否（通过唯一字段查找） |
| 查找方式 | 通过ID | 通过account+project_id |
| 使用场景 | 明确知道记录ID | 不确定记录是否存在 |

## 性能优化

### 单个upsert
- 查询：1次（查找现有记录）
- 更新：1次（如果记录存在）
- 创建：1次（如果记录不存在）

### 批量upsert（Redis队列）
- 查询：分批查询（每批50条，使用从库）
- 更新：批量更新（每批50条，使用主库）
- 创建：批量创建（每批50条，使用主库）
- 缓存：Redis缓存避免重复处理

## 注意事项

### 1. 余额字段的特殊处理

余额字段（balance）有特殊逻辑：

```python
# 更新余额时会自动：
# 1. 更新balance_history（保留最近7天）
# 2. 计算variable（今天余额 - 昨天余额）
# 3. 更新balance字段
```

### 2. 唯一标识字段

account和project_id是唯一标识，用于查找记录：

```python
# 这两个字段组合必须唯一
existing = await ProjectAccount.get_or_none(
    account=item.account,
    project_id=item.project_id
)
```

### 3. Redis队列处理

批量upsert使用Redis队列异步处理：

```python
# 数据流程：
# 1. API接收数据 → 添加到Redis队列
# 2. 后台worker → 从队列取数据
# 3. 批量查询 → 使用从库
# 4. 批量更新/创建 → 使用主库
# 5. 添加缓存 → 避免重复处理
```

### 4. 空值处理

```python
# ✅ 正确：只传入要更新的字段
{
    "account": "test@example.com",
    "project_id": "xxx",
    "balance": 100.00
}

# ❌ 错误：显式传入None会被忽略（不会更新）
{
    "account": "test@example.com",
    "project_id": "xxx",
    "balance": 100.00,
    "password": None  # 这个字段不会被更新
}

# ✅ 正确：如果要清空字段，传入空字符串
{
    "account": "test@example.com",
    "project_id": "xxx",
    "balance": 100.00,
    "password": ""  # 这个会更新为空字符串
}
```

## 测试建议

### 测试场景1：只更新余额

```python
# 1. 创建记录
await project_account_crud.create(Create(
    account="test@example.com",
    project_id="xxx",
    password="encrypted",
    status=1,
    balance=100.00
))

# 2. 只更新余额
result = await project_account_crud.upsert(Create(
    account="test@example.com",
    project_id="xxx",
    balance=150.00
))

# 3. 验证：其他字段保持不变
assert result.password == "encrypted"
assert result.status == 1
assert result.balance == 150.00
```

### 测试场景2：更新多个字段

```python
result = await project_account_crud.upsert(Create(
    account="test@example.com",
    project_id="xxx",
    balance=200.00,
    status=2,
    data={"key": "value"}
))

# 验证：只更新传入的字段
assert result.balance == 200.00
assert result.status == 2
assert result.data == {"key": "value"}
assert result.password == "encrypted"  # 保持不变
```

### 测试场景3：创建新记录

```python
result = await project_account_crud.upsert(Create(
    account="new@example.com",
    project_id="xxx",
    balance=100.00
))

# 验证：创建了新记录
assert result.account == "new@example.com"
assert result.balance == 100.00
```

## 相关文件

- `backend/app/crud/project/account.py` - CRUD层实现
- `backend/app/utils/redis_queue.py` - Redis队列处理
- `backend/app/apis/v1/project/account.py` - API接口
- `backend/app/schemas/project/account.py` - 数据模型

## 总结

现在upsert接口的行为与PUT接口一致：

- ✅ 只更新传入的非空字段
- ✅ 保留未传入字段的原值
- ✅ 避免意外覆盖数据
- ✅ 支持单个和批量操作
- ✅ Redis队列异步处理
- ✅ 使用读写分离优化性能

这样可以安全地使用upsert接口更新部分字段，不用担心覆盖其他数据！
