# API 认证审计和修复方案

## 审计结果

### 已有认证的 API ✅
1. `app/apis/v1/mail/info.py` - 邮箱信息 API
2. `app/apis/v1/project/info.py` - 项目信息 API
3. `app/apis/v1/project/wallet.py` - 项目钱包 API
4. `app/apis/v1/server/account.py` - 服务器账号 API
5. `app/apis/v1/user/user.py` - 用户管理 API
6. `app/apis/v1/user/user_role.py` - 用户角色管理 API（使用 get_admin_user）

### 缺少认证的 API ❌
1. `app/apis/v1/mail/outlook.py` - Outlook 操作 API
2. `app/apis/v1/project/account.py` - 项目账号 API
3. `app/apis/v1/project/balance.py` - 项目余额 API
4. `app/apis/v1/server/country.py` - 国家信息 API
5. `app/apis/v1/server/group.py` - 分组信息 API
6. `app/apis/v1/server/info.py` - 服务器信息 API
7. `app/apis/v1/user/log.py` - 日志管理 API
8. `app/apis/v1/user/role.py` - 角色管理 API
9. `app/apis/v1/user/route.py` - 路由管理 API
10. `app/apis/v1/user/token.py` - Token 管理 API

### 不需要认证的 API ✅
1. `app/apis/v1/user/auth.py` - 用户认证 API（登录、注册）

## 认证方案

### 1. 双重认证支持

已更新 `app/apis/deps.py` 支持两种认证方式：

**JWT Token 认证**：
```
Authorization: Bearer <jwt_token>
```

**API Token 认证**：
```
API-TOKEN: <api_token>
```

### 2. 认证依赖函数

```python
# 基础认证（支持 JWT 和 API Token）
get_current_user()

# 管理员权限验证
get_admin_user()

# GM 权限验证
get_gm_user()
```

### 3. 使用方法

在每个 API 端点函数中添加认证参数：

```python
from fastapi import Depends
from app.apis.deps import get_current_user

@app.get("")
async def gets(
    # ... 其他参数
    current_user: dict = Depends(get_current_user)
):
    """获取列表"""
    # 业务逻辑
```

## 修复步骤

### 方法 1：手动修复（推荐）

对于每个缺少认证的文件：

1. 添加导入：
```python
from fastapi import Depends  # 如果还没有
from app.apis.deps import get_current_user
```

2. 为每个端点函数添加参数：
```python
current_user: dict = Depends(get_current_user)
```

### 方法 2：使用脚本批量修复

运行提供的脚本：
```bash
cd backend
python add_auth_to_apis.py
```

**注意**：脚本可能无法完美处理所有情况，建议手动检查。

## 需要修复的文件详情

### 1. mail/outlook.py
所有端点都需要添加认证：
- `GET /auth/url` - 获取授权 URL
- `POST /auth/token` - 换取 Token
- `POST /send` - 发送邮件
- `POST /messages` - 获取邮件
- `POST /check` - 检查邮箱状态

### 2. project/account.py
所有 CRUD 端点都需要添加认证：
- `POST /` - 创建
- `GET /{id}` - 获取单个
- `GET /` - 获取列表
- `PUT /{id}` - 更新
- `DELETE /{id}` - 删除
- `POST /upsert` - 创建或更新

### 3. project/balance.py
所有 CRUD 端点都需要添加认证（同上）

### 4. server/country.py
所有 CRUD 端点都需要添加认证（同上）

### 5. server/group.py
所有 CRUD 端点都需要添加认证（同上）

### 6. server/info.py
所有 CRUD 端点都需要添加认证（同上）

### 7. user/log.py
所有 CRUD 端点都需要添加认证（同上）

### 8. user/role.py
所有 CRUD 端点都需要添加认证（同上）

### 9. user/route.py
所有 CRUD 端点都需要添加认证（同上）

### 10. user/token.py
所有 CRUD 端点都需要添加认证（同上）

## 验证方法

### 1. 检查 OpenAPI 文档

访问 `http://127.0.0.1:6080/openapi.json`，检查每个端点是否有 `security` 字段：

```json
{
  "paths": {
    "/v1/xxx/xxx": {
      "get": {
        "security": [
          {
            "HTTPBearer": []
          }
        ]
      }
    }
  }
}
```

### 2. 测试未认证访问

```bash
# 应该返回 401 Unauthorized
curl -X GET "http://127.0.0.1:6080/v1/project/account"
```

### 3. 测试 JWT 认证

```bash
# 应该返回 200 OK
curl -X GET "http://127.0.0.1:6080/v1/project/account" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### 4. 测试 API Token 认证

```bash
# 应该返回 200 OK
curl -X GET "http://127.0.0.1:6080/v1/project/account" \
  -H "API-TOKEN: <your_api_token>"
```

## 安全性提升

修复后的效果：

- ✅ 所有 API（除登录/注册）都需要认证
- ✅ 支持 JWT 和 API Token 双重认证
- ✅ 防止未授权访问
- ✅ 统一的认证处理逻辑
- ✅ 更好的安全性

## 后续工作

1. ✅ 更新 `app/apis/deps.py` - 已完成
2. ⏳ 为 10 个文件添加认证 - 待完成
3. ⏳ 测试所有端点 - 待完成
4. ⏳ 更新 README.md - 待完成
5. ⏳ 删除多余的文档 - 待完成

## 文档清理

需要删除的多余文档：
- `backend/JWT_IMPLEMENTATION_GUIDE.md`
- `backend/API_TOKEN_IMPLEMENTATION.md`
- `backend/JWT_SUMMARY.md`
- `backend/QUICK_JWT_REFERENCE.md`
- `backend/QUICK_PASSWORD_REFERENCE.md`
- `backend/PASSWORD_ENCRYPTION_SUMMARY.md`
- `backend/USER_ROLE_MANAGEMENT_SUMMARY.md`
- `backend/CLEANUP_SUMMARY.md`
- `backend/FILE_ORGANIZATION.md`
- `backend/FIX_ROLE_IDS_ISSUE.md`
- `backend/JWT_COMPLETION_REPORT.md`

保留的文档：
- `backend/README.md` - 主文档（需要更新）
- `backend/db/README.md` - 数据库初始化说明
- `backend/db/INITIALIZATION_SUMMARY.md` - 数据库初始化总结
- `backend/app/tests/README.md` - 测试说明
- `backend/app/logs/README.md` - 日志说明
- `backend/app/logs/USAGE.md` - 日志使用说明

## 总结

这是一个重要的安全性修复，确保所有 API 都有适当的认证保护。修复完成后，系统将更加安全可靠。
