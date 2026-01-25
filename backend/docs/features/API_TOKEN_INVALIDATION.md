# API Token 失效机制说明

## 问题描述

用户询问：**API Token 是在 JWT 进行校验的，如何保证切换 API Token 后以前的无法使用？**

## 解决方案

系统已经实现了完整的 Token 失效机制，确保生成新 Token 后，旧 Token 自动失效。

## 实现原理

### 1. Token 存储结构

Token 存储在 `user_tokens` 表中，包含以下关键字段：

```python
class UserToken(BaseModel):
    user = fields.ForeignKeyField("models.UserInfo", related_name="tokens")
    token = fields.TextField(description="访问令牌")
    status = fields.IntEnumField(Status, default=Status.OK, description="是否已失效")
    # Status.OK = 1 (有效)
    # Status.NOT = 2 (失效)
```

### 2. Token 验证逻辑

在 `backend/app/core/verify.py` 中，Token 验证时会检查 `status` 字段：

```python
async def get_current_user_or_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    api_token: Optional[str] = Header(None, alias="API-TOKEN")
):
    # 2. 尝试 API Token 认证
    if api_token:
        # ✅ 关键：只查询 status=1 的 Token
        token_obj = await UserToken.filter(token=api_token, status=1).first()
        if not token_obj:
            raise HTTPException(status_code=401, detail="Invalid API Token")
        # ... 返回用户信息
```

**关键点**：验证时使用 `status=1` 过滤条件，只有状态为"有效"的 Token 才能通过验证。

### 3. Token 生成逻辑

在 `backend/app/crud/user/token.py` 的 `generate_token()` 方法中：

```python
async def generate_token(self, user_id: UUID) -> Out:
    """
    为用户生成新的JWT Token，10年有效期
    旧Token将被设置为失效状态
    """
    # 1. 获取用户信息
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    
    # 2. 生成新的 JWT Token（10年有效期）
    token_data = {
        'id': str(user.id),
        'email': user.email,
        'roles': user_roles
    }
    new_token = create_access_token(
        data=token_data,
        expires_delta=315360000  # 10年
    )
    
    # 3. ✅ 关键：将该用户的所有旧 Token 设置为失效
    await UserToken.filter(user_id=user_id, status=Status.OK).update(status=Status.NOT)
    
    # 4. 创建新 Token 记录（status=1）
    res = await UserToken.create(
        token=new_token,
        user_id=user_id,
        status=Status.OK
    )
    
    return Out.model_validate(res)
```

**关键步骤**：
1. 生成新 Token 之前，先将该用户所有有效的 Token（`status=1`）更新为失效（`status=2`）
2. 然后创建新的 Token 记录，状态为有效（`status=1`）

## 工作流程

```
用户请求生成新 Token
    ↓
1. 查询用户信息和角色
    ↓
2. 生成新的 JWT Token（10年有效期）
    ↓
3. 将该用户所有旧 Token 的 status 设置为 2（失效）
    ↓
4. 创建新 Token 记录，status=1（有效）
    ↓
5. 返回新 Token
```

## API 端点

### 生成新 Token

```bash
POST /v1/user/token/generate
Authorization: Bearer <current_jwt_token>
```

**响应示例**：
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "status": 1,
  "create_time": "2026-01-25 12:00:00",
  "update_time": "2026-01-25 12:00:00"
}
```

## 验证机制

### 旧 Token 验证失败

```bash
# 使用旧 Token 请求
curl -H "API-TOKEN: old_token_here" http://localhost:6080/v1/user/user

# 响应：401 Unauthorized
{
  "detail": "Invalid API Token"
}
```

**原因**：旧 Token 的 `status` 已被设置为 2，查询 `status=1` 时找不到记录。

### 新 Token 验证成功

```bash
# 使用新 Token 请求
curl -H "API-TOKEN: new_token_here" http://localhost:6080/v1/user/user

# 响应：200 OK
{
  "items": [...],
  "count": 10
}
```

**原因**：新 Token 的 `status` 为 1，可以通过验证。

## 数据库查询示例

### 查看用户的所有 Token

```sql
SELECT 
    id,
    LEFT(token, 50) as token_preview,
    status,
    create_time
FROM tokens
WHERE user_id = 'user_uuid_here'
ORDER BY create_time DESC;
```

**结果示例**：
```
| id   | token_preview                                      | status | create_time         |
|------|----------------------------------------------------|--------|---------------------|
| uuid | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE... | 1      | 2026-01-25 12:00:00 |
| uuid | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE... | 2      | 2026-01-24 10:00:00 |
| uuid | eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE... | 2      | 2026-01-23 08:00:00 |
```

只有最新的 Token（status=1）可以使用，旧的 Token（status=2）已失效。

## 安全特性

1. **自动失效**：生成新 Token 时，旧 Token 自动失效，无需手动操作
2. **数据库级别控制**：失效状态存储在数据库中，重启服务不影响
3. **查询优化**：使用索引 `(user_id, status, create_time)` 提高查询效率
4. **JWT 格式**：Token 使用 JWT 格式，包含用户信息和角色，支持无状态验证
5. **长期有效**：新 Token 有效期为 10 年，适合 API 调用场景

## 注意事项

### 1. 注册时的 Token

在 `backend/app/apis/v1/user/auth.py` 的 `register()` 函数中，使用的是旧的 Token 生成方式（MD5），**不会自动失效旧 Token**：

```python
# 生成API token（注册时）
timestamp_ms = int(time.time() * 1000)
api_token = gen_api_token(item.email, timestamp_ms)

# 保存token到数据库
await UserToken.create(
    user_id=user_out.id,
    token=api_token,
    status=1
)
```

**建议**：如果需要在注册时也支持 Token 失效机制，应该调用 `token_crud.generate_token()` 方法。

### 2. 两种认证方式

系统支持两种认证方式：

1. **JWT Token**（Authorization: Bearer xxx）- 用于前端登录
2. **API Token**（API-TOKEN: xxx）- 用于 API 调用

两种方式都会经过 `get_current_user_or_token()` 验证，API Token 会检查 `status` 字段。

## 测试方法

### 手动测试步骤

1. **生成第一个 Token**：
```bash
curl -X POST http://localhost:6080/v1/user/token/generate \
  -H "Authorization: Bearer <your_jwt_token>"
```

2. **使用第一个 Token 访问 API**（应该成功）：
```bash
curl http://localhost:6080/v1/user/user \
  -H "API-TOKEN: <token_1>"
```

3. **生成第二个 Token**：
```bash
curl -X POST http://localhost:6080/v1/user/token/generate \
  -H "Authorization: Bearer <your_jwt_token>"
```

4. **使用第一个 Token 访问 API**（应该失败，返回 401）：
```bash
curl http://localhost:6080/v1/user/user \
  -H "API-TOKEN: <token_1>"
```

5. **使用第二个 Token 访问 API**（应该成功）：
```bash
curl http://localhost:6080/v1/user/user \
  -H "API-TOKEN: <token_2>"
```

### 自动化测试脚本

已创建测试脚本 `backend/test_token_invalidation.py`，可以自动验证 Token 失效机制。

## 总结

✅ **系统已经实现了完整的 Token 失效机制**：

1. Token 验证时只查询 `status=1` 的记录
2. 生成新 Token 时自动将旧 Token 的 `status` 设置为 2
3. 旧 Token 无法通过验证，返回 401 错误
4. 新 Token 可以正常使用

**无需额外修改**，当前实现已经满足需求。
