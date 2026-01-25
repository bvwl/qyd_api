# 项目账号 Host 自动绑定功能

## 更新时间
2026-01-25

## 功能说明

在创建或更新项目账号时，可以通过传入 `host` 字段来自动查询并绑定对应的服务器信息。

### 使用场景

当你知道服务器的 host 地址，但不知道其 UUID 时，可以直接传入 host，系统会自动查询对应的 server_id 并进行绑定。

## API 变更

### Schema 变更

#### Create Schema
```python
class Create(BaseModel):
    account: str = Field(..., description="账号")
    password: str | None = Field(None, description="密码（加密存储）")
    # ... 其他字段
    project_id: UUID = Field(..., description="所属项目ID")
    server_id: UUID | None = Field(None, description="关联服务器信息ID")
    host: str | None = Field(None, description="服务器host（可选，如果提供则自动查询server_id）")  # 新增
```

#### Update Schema
```python
class Update(BaseModel):
    # ... 其他字段
    server_id: UUID | None = Field(None, description="关联服务器信息ID")
    host: str | None = Field(None, description="服务器host（可选，如果提供则自动查询server_id）")  # 新增
```

## 使用方式

### 1. 创建账号时使用 host

**之前的方式（需要知道 server_id）：**
```json
{
  "account": "test@example.com",
  "password": "password123",
  "project_id": "uuid-of-project",
  "server_id": "uuid-of-server",  // 需要先查询服务器获取 UUID
  "status": 1,
  "account_type": 1
}
```

**新的方式（直接使用 host）：**
```json
{
  "account": "test@example.com",
  "password": "password123",
  "project_id": "uuid-of-project",
  "host": "192.168.1.100",  // 直接传入 host，自动查询 server_id
  "status": 1,
  "account_type": 1
}
```

### 2. 更新账号时使用 host

```json
{
  "host": "192.168.1.200"  // 更新绑定的服务器
}
```

### 3. 同时传入 host 和 server_id

如果同时传入 `host` 和 `server_id`，系统会优先使用 `host` 查询，并覆盖 `server_id`。

```json
{
  "account": "test@example.com",
  "host": "192.168.1.100",  // 优先使用 host
  "server_id": "some-uuid"  // 会被 host 查询结果覆盖
}
```

## 处理逻辑

### 创建账号（create）

```python
async def create(self, item: Create) -> Out:
    # 1. 如果提供了 host，查询对应的 server_id
    if item.host:
        server = await ServerInfo.get_or_none(host=item.host)
        if server:
            item.server_id = server.id  # 自动设置 server_id
        else:
            # host 不存在，记录警告但不中断（宽松模式）
            print(f"⚠️  未找到 host={item.host} 的服务器")
    
    # 2. 过滤掉 host 字段（不存储到数据库）
    filtered_item = {
        k: v for k, v in item.model_dump().items() 
        if v is not None and k not in ['variable', 'balance_history', 'host']
    }
    
    # 3. 创建记录（使用查询到的 server_id）
    res = await ProjectAccount.create(**filtered_item)
```

### 更新账号（update）

```python
async def update(self, id: UUID, item: Update) -> Out:
    # 1. 如果提供了 host，查询对应的 server_id
    if item.host:
        server = await ServerInfo.get_or_none(host=item.host)
        if server:
            item.server_id = server.id  # 自动设置 server_id
    
    # 2. 过滤掉 host 字段
    update_data = item.model_dump(
        exclude_unset=True, 
        exclude={'balance', 'variable', 'balance_history', 'host'}
    )
    
    # 3. 更新记录
    await res.update_from_dict(update_data)
```

### Upsert 操作

upsert 操作也支持 host 自动绑定，逻辑与 create 相同。

## 错误处理

### host 不存在

当传入的 host 在服务器信息表中不存在时：

- **行为**：记录警告日志，但不中断操作
- **结果**：`server_id` 保持为 `None`（创建）或保持原值（更新）
- **日志**：`⚠️  未找到 host=xxx 的服务器`

**示例：**
```python
# 传入不存在的 host
{
  "account": "test@example.com",
  "host": "nonexistent.host.com"
}

# 结果
{
  "id": "uuid",
  "account": "test@example.com",
  "server_id": null,  // host 不存在，server_id 为 null
  "server": null
}
```

### 严格模式（可选）

如果需要严格模式（host 不存在时抛出错误），可以修改代码：

```python
if item.host:
    server = await ServerInfo.get_or_none(host=item.host)
    if server:
        item.server_id = server.id
    else:
        # 严格模式：抛出错误
        raise HTTPException(
            status_code=404, 
            detail=f'未找到 host={item.host} 的服务器'
        )
```

## 数据库字段

`host` 字段**不会存储到数据库**，它只是一个临时字段，用于查询 `server_id`。

数据库中实际存储的是 `server_id`（外键）。

## API 示例

### 创建账号（使用 host）

**请求：**
```bash
curl -X POST "http://localhost:6080/v1/project/account" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account": "test@example.com",
    "password": "password123",
    "project_id": "project-uuid",
    "host": "192.168.1.100",
    "status": 1,
    "account_type": 1,
    "balance": 100
  }'
```

**响应：**
```json
{
  "message": "成功",
  "id": "account-uuid",
  "account": "test@example.com",
  "status": 1,
  "account_type": 1,
  "balance": 100,
  "project_id": "project-uuid",
  "server_id": "server-uuid",  // 自动查询并绑定
  "server": {
    "id": "server-uuid",
    "host": "192.168.1.100",
    "name": "服务器名称"
  },
  "create_time": "2026-01-25 10:00:00",
  "update_time": "2026-01-25 10:00:00"
}
```

### 更新账号（使用 host）

**请求：**
```bash
curl -X PUT "http://localhost:6080/v1/project/account/{account_id}" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "192.168.1.200"
  }'
```

**响应：**
```json
{
  "message": "成功",
  "id": "account-uuid",
  "account": "test@example.com",
  "server_id": "new-server-uuid",  // 更新为新的服务器
  "server": {
    "id": "new-server-uuid",
    "host": "192.168.1.200",
    "name": "新服务器名称"
  }
}
```

## 测试

### 运行测试脚本

```bash
cd backend
python test_host_binding.py
```

### 测试内容

1. ✅ 通过 host 创建账号，自动绑定 server_id
2. ✅ host 不存在时的处理（宽松模式）
3. ✅ 更新时通过 host 重新绑定服务器

## 优势

### 1. 简化 API 调用

不需要先查询服务器 UUID，直接使用 host 即可。

**之前：**
```python
# 1. 先查询服务器
server = await get_server_by_host("192.168.1.100")
# 2. 再创建账号
await create_account(server_id=server.id)
```

**现在：**
```python
# 一步完成
await create_account(host="192.168.1.100")
```

### 2. 更直观

host 地址比 UUID 更容易记忆和使用。

### 3. 兼容性

- 仍然支持直接传入 `server_id`
- `host` 是可选字段，不影响现有代码

## 注意事项

### 1. host 唯一性

确保服务器信息表中的 `host` 字段是唯一的，否则可能查询到错误的服务器。

### 2. 性能

每次传入 `host` 都会执行一次数据库查询。如果已知 `server_id`，直接传入 `server_id` 性能更好。

### 3. 优先级

如果同时传入 `host` 和 `server_id`，`host` 优先。

## 相关文档

- [项目账号加密更新](PROJECT_ACCOUNT_ENCRYPTION_UPDATE.md)
- [前端表单修复](FRONTEND_FORMS_FIX_COMPLETE.md)
- [后端开发规范](docs/conventions.md)

## 总结

通过新增 `host` 字段，项目账号可以更方便地绑定服务器信息，无需先查询服务器 UUID。

这个功能特别适合批量导入或 API 集成场景，可以大大简化代码逻辑。
