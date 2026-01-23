# JWT认证统一更新

## 更新内容

已将所有项目账号相关的API统一为**标准JWT认证**，使用 FastAPI 的 `HTTPBearer` security scheme。

## 特性

✅ **Swagger文档显示锁图标** - 使用 `HTTPBearer` security scheme  
✅ **自动提取JWT Token** - 不需要在API函数中手动传入 `authorization` 参数  
✅ **统一认证逻辑** - 所有API使用相同的认证依赖  
✅ **数据权限过滤** - 根据用户角色自动过滤数据  

## 认证方式

### 在Swagger文档中使用

1. 访问 `http://localhost:6080/docs`
2. 点击右上角的 **Authorize** 按钮（锁图标）🔒
3. 输入JWT Token（不需要 "Bearer " 前缀，系统会自动添加）
4. 点击 **Authorize**
5. 现在所有API都会自动带上认证信息

### 使用curl命令

```bash
# 1. 登录获取Token
curl -X POST "http://localhost:6080/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }'

# 响应示例
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

# 2. 使用Token访问API
curl -X GET "http://localhost:6080/api/v1/project/wallet?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 更新的文件

### 核心认证模块

- `backend/app/apis/deps.py` - 统一的JWT认证依赖
  - `security` - HTTPBearer security scheme（在Swagger中显示锁图标）
  - `get_current_user_from_jwt()` - JWT Token验证（自动从Header提取）
  - `get_current_user()` - 基础认证（所有登录用户）
  - `get_admin_user()` - 管理员权限验证
  - `get_gm_user()` - GM权限验证（ADMIN或GM）

**重要特性**：
- 使用 `HTTPBearer` security scheme，Swagger文档会显示🔒图标
- JWT Token自动从 `Authorization: Bearer xxx` Header中提取
- API函数不需要手动添加 `authorization` 参数

### 更新的API文件

所有API文件已统一从 `app.apis.deps` 导入认证依赖：

**项目管理相关**：
- `backend/app/apis/v1/project/wallet.py` - 项目钱包
- `backend/app/apis/v1/project/account.py` - 项目账号
- `backend/app/apis/v1/project/balance.py` - 项目余额
- `backend/app/apis/v1/project/info.py` - 项目信息

**用户管理相关**：
- `backend/app/apis/v1/user/user.py` - 用户管理
- `backend/app/apis/v1/user/role.py` - 角色管理
- `backend/app/apis/v1/user/route.py` - 路由管理
- `backend/app/apis/v1/user/token.py` - Token管理
- `backend/app/apis/v1/user/log.py` - 日志管理
- `backend/app/apis/v1/user/user_role.py` - 用户角色关联

**服务器管理相关**：
- `backend/app/apis/v1/server/info.py` - 服务器信息
- `backend/app/apis/v1/server/account.py` - 服务器账号
- `backend/app/apis/v1/server/country.py` - 国家管理
- `backend/app/apis/v1/server/group.py` - 分组管理

**邮件管理相关**：
- `backend/app/apis/v1/mail/info.py` - 邮件信息
- `backend/app/apis/v1/mail/outlook.py` - Outlook集成

**RBAC相关**：
- `backend/app/apis/v1/rbac/menu.py` - 菜单管理
- `backend/app/apis/v1/rbac/role.py` - RBAC角色
- `backend/app/apis/v1/rbac/user.py` - RBAC用户

**系统相关**：
- `backend/app/apis/v1/system/database.py` - 数据库信息

## API函数示例

### 不需要手动传入JWT参数

```python
from fastapi import APIRouter, Depends
from app.apis.deps import get_current_user, get_admin_user, get_gm_user

app = APIRouter()

# ✅ 正确：JWT会自动从Header中提取
@app.get("")
async def gets(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=1000),
    current_user: dict = Depends(get_current_user)  # 自动验证JWT
):
    # current_user 包含: user_id, email, nickname, roles
    pass

# ❌ 错误：不需要手动添加 authorization 参数
@app.get("")
async def gets(
    authorization: str = Header(None),  # 不需要这个！
    current_user: dict = Depends(get_current_user)
):
    pass
```

## 权限级别

### 1. get_current_user
- 所有登录用户都可以访问
- 用于一般的CRUD操作

```python
@app.get("")
async def gets(current_user: dict = Depends(get_current_user)):
    pass
```

### 2. get_gm_user
- 需要GM或ADMIN角色
- 用于项目管理相关操作

```python
@app.delete("/{id}")
async def delete(id: UUID, gm_user: dict = Depends(get_gm_user)):
    pass
```

### 3. get_admin_user
- 仅ADMIN角色可以访问
- 用于系统级别的管理操作

```python
@app.delete("/{id}")
async def delete(id: UUID, admin_user: dict = Depends(get_admin_user)):
    pass
```

## JWT Token结构

Token中包含的信息：

```json
{
  "id": "user_uuid",
  "email": "user@example.com",
  "roles": ["ADMIN", "GM"]
}
```

## 数据权限

系统会根据用户角色自动过滤数据：

- **ADMIN/GM**: 可以查看所有项目的数据
- **IT/MANUAL**: 只能查看分配给自己的项目的数据

这个过滤逻辑在各个API的 `gets()` 方法中通过 `filter_by_user_projects()` 实现。

## 测试

运行测试脚本验证JWT认证：

```bash
./test_jwt_project_api.sh
```

测试内容：
1. 登录获取JWT Token
2. 使用JWT访问项目钱包API
3. 使用JWT访问项目账号API
4. 使用JWT访问项目余额API
5. 使用JWT访问项目信息API
6. 验证无Token访问返回401

## 前端集成

前端需要在请求头中添加JWT Token：

```typescript
// src/api/index.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

// 请求拦截器：添加JWT Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export default api
```

## 注意事项

1. **Token过期时间**: 默认365天（可在 `.env` 中配置 `JWT_ACCESS_TOKEN_EXPIRE_DAYS`）
2. **Token存储**: 前端应将Token存储在 `localStorage` 中
3. **Token刷新**: 当前版本不支持Token刷新，过期后需要重新登录
4. **安全性**: 
   - Token使用HS256算法签名
   - 密钥配置在 `.env` 的 `JWT_SECRET_KEY` 中
   - 生产环境务必使用强密钥

## 移除的功能

- ❌ API-TOKEN 认证方式（不再支持）
- ❌ `app.core.verify` 中的认证函数（已废弃，统一使用 `app.apis.deps`）

## 迁移指南

如果你的代码还在使用旧的认证方式：

### 后端迁移

```python
# ❌ 旧方式
from app.core.verify import get_current_user

# ✅ 新方式
from app.apis.deps import get_current_user
```

### 前端迁移

```typescript
// ❌ 旧方式（使用API-TOKEN）
headers: {
  'API-TOKEN': 'your_api_token'
}

// ✅ 新方式（使用JWT）
headers: {
  'Authorization': `Bearer ${jwt_token}`
}
```

## 相关文档

- [JWT Token快速开始](./JWT_TOKEN_QUICK_START.md)
- [权限管理完整文档](./docs/fixes/PERMISSION_COMPLETE.md)
- [开发规范](./docs/conventions.md)
