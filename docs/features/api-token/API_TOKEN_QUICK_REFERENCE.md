# API Token 失效机制 - 快速参考

## 问题

**API Token 切换后，如何保证旧 Token 无法使用？**

## 答案

✅ **已实现，无需修改。**

## 核心机制

### 1. Token 状态

```
status = 1  →  有效
status = 2  →  失效
```

### 2. 验证逻辑

```python
# 只查询 status=1 的 Token
token_obj = await UserToken.filter(token=api_token, status=1).first()
```

### 3. 生成逻辑

```python
# 1. 将旧 Token 设置为失效（status=2）
await UserToken.filter(user_id=user_id, status=1).update(status=2)

# 2. 创建新 Token（status=1）
await UserToken.create(token=new_token, user_id=user_id, status=1)
```

## 工作流程

```
生成新 Token
    ↓
旧 Token status: 1 → 2（失效）
    ↓
新 Token status: 1（有效）
    ↓
验证时只查询 status=1
    ↓
旧 Token 无法通过验证 ❌
新 Token 可以通过验证 ✅
```

## API 使用

### 生成新 Token

```bash
POST /v1/user/token/generate
Authorization: Bearer <jwt_token>
```

### 使用 Token

```bash
# 方式1：API-TOKEN Header
curl -H "API-TOKEN: your_token" http://localhost:6080/v1/user/user

# 方式2：Authorization Bearer
curl -H "Authorization: Bearer your_token" http://localhost:6080/v1/user/user
```

## 验证效果

| Token | Status | 验证结果 |
|-------|--------|---------|
| 旧 Token | 2 | ❌ 401 Unauthorized |
| 新 Token | 1 | ✅ 200 OK |

## 数据库查询

```sql
-- 查看用户的所有 Token
SELECT 
    LEFT(token, 50) as token,
    status,
    create_time
FROM tokens
WHERE user_id = 'user_uuid'
ORDER BY create_time DESC;
```

## 关键文件

| 文件 | 功能 |
|------|------|
| `backend/app/core/verify.py` | Token 验证 |
| `backend/app/crud/user/token.py` | Token 生成 |
| `backend/app/apis/v1/user/token.py` | Token API |
| `backend/app/models/user.py` | Token 模型 |

## 测试步骤

1. 生成 Token 1
2. 使用 Token 1 → ✅ 成功
3. 生成 Token 2
4. 使用 Token 1 → ❌ 失败（401）
5. 使用 Token 2 → ✅ 成功

## 安全特性

- ✅ 自动失效
- ✅ 数据库级别控制
- ✅ 查询优化（索引）
- ✅ JWT 格式
- ✅ 10年有效期

## 总结

**当前实现完全满足需求，无需任何修改。**

生成新 Token 时，旧 Token 自动失效，只有最新的 Token 可以使用。
