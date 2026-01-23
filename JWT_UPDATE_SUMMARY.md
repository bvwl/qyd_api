# JWT认证更新总结

## ✅ 完成的工作

### 1. 统一认证模块 (`backend/app/apis/deps.py`)

**关键改进**：
- ✅ 使用 `HTTPBearer` security scheme
- ✅ Swagger文档显示🔒锁图标
- ✅ JWT Token自动从Header提取，API函数不需要手动传参
- ✅ 移除了API-TOKEN认证方式

**代码结构**：
```python
from fastapi.security import HTTPBearer

# 定义security scheme（显示锁图标）
security = HTTPBearer(
    scheme_name="JWT Bearer",
    description="JWT认证，格式: Bearer <token>",
    auto_error=False
)

# JWT验证函数（自动提取Token）
async def get_current_user_from_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    # 自动从 Authorization: Bearer xxx 中提取token
    pass

# 三个权限级别
- get_current_user()   # 所有登录用户
- get_gm_user()        # GM或ADMIN
- get_admin_user()     # 仅ADMIN
```

### 2. 更新所有API文件（20+个）

所有API文件已统一从 `app.apis.deps` 导入认证依赖：

**项目管理**：
- ✅ `project/wallet.py` - 项目钱包
- ✅ `project/account.py` - 项目账号
- ✅ `project/balance.py` - 项目余额
- ✅ `project/info.py` - 项目信息

**用户管理**：
- ✅ `user/user.py` - 用户管理
- ✅ `user/role.py` - 角色管理
- ✅ `user/route.py` - 路由管理
- ✅ `user/token.py` - Token管理
- ✅ `user/log.py` - 日志管理
- ✅ `user/user_role.py` - 用户角色关联

**服务器管理**：
- ✅ `server/info.py` - 服务器信息
- ✅ `server/account.py` - 服务器账号
- ✅ `server/country.py` - 国家管理
- ✅ `server/group.py` - 分组管理

**邮件管理**：
- ✅ `mail/info.py` - 邮件信息
- ✅ `mail/outlook.py` - Outlook集成

**RBAC**：
- ✅ `rbac/menu.py` - 菜单管理
- ✅ `rbac/role.py` - RBAC角色
- ✅ `rbac/user.py` - RBAC用户

**系统**：
- ✅ `system/database.py` - 数据库信息

### 3. 创建文档和测试

- ✅ `JWT_AUTH_ONLY.md` - 完整的JWT认证文档
- ✅ `SWAGGER_JWT_GUIDE.md` - Swagger使用指南
- ✅ `test_jwt_project_api.sh` - JWT认证测试脚本

## 🎯 关键特性

### 1. Swagger文档中的锁图标 🔒

使用 `HTTPBearer` security scheme后：
- 所有需要认证的API都会显示🔒图标
- 点击右上角的 **Authorize** 按钮可以全局授权
- 授权后所有API自动带上JWT Token

### 2. 不需要手动传入JWT参数

**❌ 错误的做法**（旧方式）：
```python
@app.get("")
async def gets(
    authorization: str = Header(None),  # 不需要！
    current_user: dict = Depends(get_current_user)
):
    pass
```

**✅ 正确的做法**（新方式）：
```python
@app.get("")
async def gets(
    page: int = Query(1),
    current_user: dict = Depends(get_current_user)  # JWT自动提取
):
    # current_user 包含: user_id, email, nickname, roles
    pass
```

### 3. 统一的认证逻辑

所有API使用相同的认证依赖：
```python
from app.apis.deps import get_current_user, get_admin_user, get_gm_user
```

不再使用：
```python
from app.core.verify import ...  # 已废弃
```

## 📝 使用方式

### 在Swagger中使用

1. 访问 `http://localhost:6080/docs`
2. 使用 `POST /api/v1/user/login` 登录获取Token
3. 点击右上角 **🔒 Authorize** 按钮
4. 粘贴Token（不需要 "Bearer " 前缀）
5. 点击 **Authorize**
6. 现在所有API都会自动带上认证

### 使用curl命令

```bash
# 1. 登录
TOKEN=$(curl -s -X POST "http://localhost:6080/api/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"zhiyu","password":"2201101122@qq.com"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# 2. 使用Token访问API
curl -X GET "http://localhost:6080/api/v1/project/wallet?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 前端集成

```typescript
// axios拦截器自动添加Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

## 🔐 权限级别

### 1. get_current_user
- **权限**：所有登录用户
- **用途**：查看、创建、更新操作
- **示例**：查看项目列表、创建项目账号

### 2. get_gm_user
- **权限**：GM或ADMIN角色
- **用途**：项目管理相关操作
- **示例**：删除项目账号、批量操作

### 3. get_admin_user
- **权限**：仅ADMIN角色
- **用途**：系统级别管理操作
- **示例**：删除用户、系统配置

## 📊 数据权限

系统会根据用户角色自动过滤数据：

- **ADMIN/GM**: 查看所有项目的数据
- **IT/MANUAL**: 只能查看分配给自己的项目的数据

这个过滤逻辑通过 `filter_by_user_projects()` 实现。

## 🧪 测试

运行测试脚本：
```bash
./test_jwt_project_api.sh
```

测试内容：
1. ✅ 登录获取JWT Token
2. ✅ 使用JWT访问项目钱包API
3. ✅ 使用JWT访问项目账号API
4. ✅ 使用JWT访问项目余额API
5. ✅ 使用JWT访问项目信息API
6. ✅ 验证无Token访问返回401

## 📚 相关文档

- [JWT认证完整文档](./JWT_AUTH_ONLY.md)
- [Swagger使用指南](./SWAGGER_JWT_GUIDE.md)
- [开发规范](./docs/conventions.md)
- [API文档](http://localhost:6080/docs)

## ⚠️ 注意事项

1. **Token有效期**：默认365天（可在 `.env` 中配置）
2. **Token存储**：前端应将Token存储在 `localStorage` 中
3. **安全性**：生产环境务必使用强密钥（`JWT_SECRET_KEY`）
4. **不再支持**：API-TOKEN 认证方式已移除

## 🎉 总结

现在你的后端API已经完全使用标准的JWT认证：
- ✅ Swagger文档显示锁图标
- ✅ JWT自动从Header提取
- ✅ API函数不需要手动传参
- ✅ 统一的认证逻辑
- ✅ 完善的权限控制
- ✅ 自动的数据权限过滤

你只需要在请求头中传入 `Authorization: Bearer YOUR_TOKEN`，系统会自动处理认证和权限验证！
