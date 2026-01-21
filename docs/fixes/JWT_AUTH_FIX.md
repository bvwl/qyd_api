# JWT 认证 401 错误修复

## 问题描述
用户登录成功后，访问受保护的API时返回 401 Unauthorized 错误。浏览器显示请求头中包含正确的 `Authorization: Bearer <token>`，但后端验证失败。

## 根本原因
在 `backend/app/apis/deps.py` 文件中，`get_current_user_or_token` 函数使用 `await` 调用了 `JwtToken.verify_token(token)`，但该方法在 `backend/app/utils/jwt_tool.py` 中是一个**同步方法**，不是异步方法。

```python
# 错误的调用方式
user_info = await JwtToken.verify_token(token)  # ❌ verify_token 不是 async 方法
```

这导致 JWT 验证抛出异常，代码静默失败并尝试 API Token 认证，最终两种认证都失败返回 401。

## 修复方案

### 1. 修复 `backend/app/apis/deps.py`
移除 `await` 关键字，并正确处理 JWT payload 数据格式：

```python
# 修复后的代码
if authorization and authorization.startswith("Bearer "):
    try:
        token = authorization.replace("Bearer ", "")
        payload = JwtToken.verify_token(token)  # ✓ 同步调用
        # JWT payload 包含: id, email, roles
        # 转换为统一格式: user_id, email, nickname
        return {
            "user_id": payload.get("id"),
            "email": payload.get("email"),
            "nickname": payload.get("email"),  # JWT中没有nickname，使用email
            "roles": payload.get("roles", [])
        }
    except Exception as e:
        # JWT 验证失败，继续尝试 API Token
        pass
```

### 2. JWT Token 数据格式
登录时生成的 JWT token 包含以下字段（`backend/app/apis/v1/user/auth.py`）：
```python
token_data = {
    "id": str(user.id),      # 用户ID
    "email": user.email,      # 邮箱
    "roles": [role.code for role in user.roles]  # 角色代码列表
}
```

验证后需要转换为统一的用户信息格式：
```python
{
    "user_id": "...",   # 从 payload["id"] 获取
    "email": "...",     # 从 payload["email"] 获取
    "nickname": "...",  # JWT中没有，使用email代替
    "roles": [...]      # 从 payload["roles"] 获取
}
```

## 测试结果
修复后测试通过：
- ✓ 登录成功获取 JWT token
- ✓ 使用 JWT token 访问用户列表 API (200)
- ✓ 使用 JWT token 访问项目信息 API (200)
- ✓ 所有受保护的 API 都可以正常访问

## 验证方法
运行测试脚本：
```bash
cd backend
python test_jwt_auth.py
```

或者在浏览器中：
1. 登录系统（http://localhost:3000）
2. 打开浏览器开发者工具 → Network
3. 访问任意页面（用户列表、项目列表等）
4. 检查请求头是否包含 `Authorization: Bearer <token>`
5. 检查响应状态码是否为 200

## 相关文件
- `backend/app/apis/deps.py` - 认证依赖（已修复）
- `backend/app/utils/jwt_tool.py` - JWT 工具类
- `backend/app/apis/v1/user/auth.py` - 登录接口
- `backend/test_jwt_auth.py` - JWT 认证测试脚本

## 注意事项
1. `JwtToken.verify_token()` 是同步方法，不要使用 `await`
2. JWT payload 中的字段名是 `id`，不是 `user_id`
3. 双认证支持：JWT Token 优先，API Token 作为备选
4. 前端已正确配置，会自动在请求头中添加 JWT token
