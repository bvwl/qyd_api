# API Token 失效机制 - 完整说明

## 问题

**用户提问**：API Token 是在 JWT 进行校验的，如何保证切换 API Token 后以前的无法使用？

## 答案

✅ **系统已经实现了完整的 Token 失效机制，无需额外修改。**

## 工作原理

### 1. Token 存储

Token 存储在 `user_tokens` 表中，包含 `status` 字段：
- `status = 1`：有效
- `status = 2`：失效

### 2. Token 验证（`backend/app/core/verify.py`）

```python
# 验证 API Token 时，只查询 status=1 的记录
token_obj = await UserToken.filter(token=api_token, status=1).first()
if not token_obj:
    raise HTTPException(status_code=401, detail="Invalid API Token")
```

**关键**：只有 `status=1` 的 Token 才能通过验证。

### 3. Token 生成（`backend/app/crud/user/token.py`）

```python
async def generate_token(self, user_id: UUID) -> Out:
    # 1. 生成新的 JWT Token（10年有效期）
    new_token = create_access_token(data=token_data, expires_delta=315360000)
    
    # 2. ✅ 关键：将该用户所有旧 Token 设置为失效
    await UserToken.filter(user_id=user_id, status=Status.OK).update(status=Status.NOT)
    
    # 3. 创建新 Token 记录（status=1）
    res = await UserToken.create(token=new_token, user_id=user_id, status=Status.OK)
    
    return Out.model_validate(res)
```

**关键步骤**：
1. 生成新 Token
2. 将该用户所有旧 Token 的 `status` 更新为 2（失效）
3. 创建新 Token 记录，`status=1`（有效）

## 完整流程

```
用户请求生成新 Token
    ↓
生成新的 JWT Token（10年有效期）
    ↓
将该用户所有旧 Token 的 status 设置为 2（失效）
    ↓
创建新 Token 记录，status=1（有效）
    ↓
返回新 Token
```

## 验证效果

### 旧 Token 失效

```bash
# 使用旧 Token 请求
curl -H "API-TOKEN: old_token" http://localhost:6080/v1/user/user

# 响应：401 Unauthorized
{"detail": "Invalid API Token"}
```

### 新 Token 有效

```bash
# 使用新 Token 请求
curl -H "API-TOKEN: new_token" http://localhost:6080/v1/user/user

# 响应：200 OK
{"items": [...], "count": 10}
```

## API 端点

### 生成新 Token

```bash
POST /v1/user/token/generate
Authorization: Bearer <current_jwt_token>
```

**响应**：
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "status": 1,
  "create_time": "2026-01-25 12:00:00"
}
```

## 数据库验证

查看用户的所有 Token：

```sql
SELECT 
    LEFT(token, 50) as token_preview,
    status,
    create_time
FROM tokens
WHERE user_id = 'user_uuid'
ORDER BY create_time DESC;
```

**结果示例**：
```
| token_preview                                      | status | create_time         |
|----------------------------------------------------|--------|---------------------|
| eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE... | 1      | 2026-01-25 12:00:00 | ← 最新，有效
| eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE... | 2      | 2026-01-24 10:00:00 | ← 旧的，已失效
| eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE... | 2      | 2026-01-23 08:00:00 | ← 旧的，已失效
```

## 安全特性

1. ✅ **自动失效**：生成新 Token 时，旧 Token 自动失效
2. ✅ **数据库级别控制**：失效状态存储在数据库中，重启服务不影响
3. ✅ **查询优化**：使用索引 `(user_id, status, create_time)` 提高查询效率
4. ✅ **JWT 格式**：Token 使用 JWT 格式，包含用户信息和角色
5. ✅ **长期有效**：新 Token 有效期为 10 年，适合 API 调用场景

## 测试步骤

1. **生成第一个 Token**
2. **使用第一个 Token 访问 API**（✅ 成功）
3. **生成第二个 Token**
4. **使用第一个 Token 访问 API**（❌ 失败，返回 401）
5. **使用第二个 Token 访问 API**（✅ 成功）

## 相关文件

- **Token 验证**：`backend/app/core/verify.py`
- **Token 生成**：`backend/app/crud/user/token.py`
- **Token API**：`backend/app/apis/v1/user/token.py`
- **Token 模型**：`backend/app/models/user.py`
- **详细文档**：`backend/API_TOKEN_INVALIDATION.md`

## 总结

✅ **当前实现已经完全满足需求**：

- Token 验证时只查询 `status=1` 的记录
- 生成新 Token 时自动将旧 Token 的 `status` 设置为 2
- 旧 Token 无法通过验证，返回 401 错误
- 新 Token 可以正常使用

**无需任何修改，机制已经完善。**
