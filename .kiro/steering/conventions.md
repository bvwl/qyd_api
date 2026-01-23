# 开发规范和最佳实践

## 后端开发规范

### 1. API 开发规范

#### 1.1 路由定义顺序

**重要**：FastAPI 路由匹配是按顺序的，必须将特定路径放在动态路径之前。

```python
# ✅ 正确：特定路径在前
@app.get("/tree")  # 先匹配特定路径
@app.get("/{id}")  # 再匹配动态路径

# ❌ 错误：动态路径会拦截所有请求
@app.get("/{id}")  # 这个会拦截所有GET请求
@app.get("/tree")  # 永远不会被执行
```

#### 1.2 认证和权限

所有API端点必须添加认证依赖：

```python
from app.apis.deps import get_current_user, get_admin_user, get_gm_user

# 基础认证（所有登录用户）
@app.get("/items")
async def get_items(current_user: dict = Depends(get_current_user)):
    pass

# 管理员权限
@app.delete("/items/{id}")
async def delete_item(id: UUID, admin_user: dict = Depends(get_admin_user)):
    pass

# GM权限（管理员或项目管理员）
@app.post("/items")
async def create_item(item: Create, gm_user: dict = Depends(get_gm_user)):
    pass
```

**权限级别**：
- `get_current_user`: 所有登录用户
- `get_gm_user`: GM 和 ADMIN
- `get_admin_user`: 仅 ADMIN

#### 1.3 异常处理顺序

**必须按照以下顺序处理异常**：

```python
try:
    # 业务逻辑
    result = await some_operation()
    return result
except HTTPException:  # 1. 先捕获HTTPException（不要修改）
    raise
except ValueError as e:  # 2. 参数错误 -> 400
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:  # 3. 其他错误 -> 500
    raise HTTPException(status_code=500, detail=str(e))
```

**为什么这个顺序很重要**：
- HTTPException 已经包含正确的状态码，直接抛出
- ValueError 通常是参数验证错误，返回 400
- 其他未知错误返回 500

#### 1.4 查询参数规范

```python
@app.get("", response_model=OutList)
async def gets(
    # 搜索条件
    name: str | None = Query(None, description="名称"),
    status: int | None = Query(None, description="状态"),
    
    # 排序
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|name|create_time|update_time)$",
    ),
    
    # 时间范围（支持多种格式）
    create_time_start: str | int | None = Query(
        None,
        description="创建时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    create_time_end: str | int | None = Query(
        None,
        description="创建时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    
    # 分页
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=1000, description="每页数量"),
    
    # 是否返回总数
    res_count: bool = Query(False, description="是否返回总数"),
    
    # 认证
    current_user: dict = Depends(get_current_user)
):
    pass
```

### 2. 数据库操作规范

#### 2.1 读写分离

**必须使用读写分离工具**：

```python
from app.core.database import db_read, db_write

# ✅ 读操作：使用从库
users = await db_read(User).filter(status=1).all()
user = await db_read(User).get(id=user_id)

# ✅ 写操作：使用主库
await db_write(User).create(email="test@example.com")
await db_write(User).filter(id=user_id).update(name="new_name")
await db_write(User).filter(id=user_id).delete()

# ❌ 错误：直接使用模型（不支持读写分离）
users = await User.all()  # 不推荐
```

#### 2.2 关联数据预加载

**避免 N+1 查询问题**：

```python
# ✅ 正确：预加载关联数据
user = await User.get(id=user_id).prefetch_related('roles', 'projects')
roles = user.roles  # 不会触发额外查询

# ❌ 错误：未预加载，会触发N+1查询
user = await User.get(id=user_id)
roles = await user.roles.all()  # 额外的数据库查询
```

#### 2.3 多对多关系操作

```python
# 清除关联
await role.routes.clear()

# 添加关联
routes = await FrontendRoute.filter(id__in=route_ids).all()
await role.routes.add(*routes)

# 获取关联
routes = await role.routes.all()
```

#### 2.4 手动构建字典（避免Pydantic验证问题）

```python
# ✅ 正确：手动构建字典
route_dict = {
    'id': str(route.id),
    'name': route.name,
    'path': route.path,
    'create_time': route.create_time.strftime("%Y-%m-%d %H:%M:%S"),
    'parent_id': str(route.parent_id) if route.parent_id else None,
}

# ❌ 错误：直接返回模型（可能触发未加载的关联数据验证）
return route  # 如果有未加载的关联字段会报错
```

### 3. 数据权限过滤

#### 3.1 使用数据权限工具

```python
from app.utils.data_permission import filter_by_user_projects, has_resource_access

# 检查资源访问权限
user_roles = current_user.get('roles', [])
if not has_resource_access(user_roles, 'server'):
    raise HTTPException(status_code=403, detail="没有访问服务器的权限")

# 过滤项目数据
user_id = current_user['user_id']
allowed_project_ids = await filter_by_user_projects(user_id)

if allowed_project_ids is None:
    # 全局访问权限，不需要过滤
    projects = await db_read(Project).all()
else:
    # 只能访问特定项目
    projects = await db_read(Project).filter(id__in=allowed_project_ids).all()
```

### 4. JWT Token 规范

#### 4.1 Token 生成

```python
from app.utils.jwt_tool import create_access_token

# 生成短期Token（登录用，默认24小时）
token = create_access_token(data={
    'id': str(user.id),
    'email': user.email,
    'roles': user_roles
})

# 生成长期Token（API用，10年）
api_token = create_access_token(
    data={
        'id': str(user.id),
        'email': user.email,
        'roles': user_roles
    },
    expires_delta=315360000  # 10年
)
```

#### 4.2 Token 验证

系统支持两种认证方式：

```python
# 1. JWT Token (Authorization: Bearer xxx)
# 2. API Token (API-TOKEN: xxx)

# deps.py 会自动处理两种认证方式
async def get_current_user_or_token(
    authorization: Optional[str] = Header(None),
    api_token: Optional[str] = Header(None, alias="API-TOKEN")
):
    # 优先使用 JWT，如果没有则尝试 API Token
    pass
```

### 5. 环境变量使用

**必须使用 .env 文件配置**：

```python
import os

# ✅ 正确：从环境变量读取，提供默认值
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DEBUG = os.getenv("DEBUG", "0") == "1"

# ❌ 错误：硬编码配置
DB_HOST = "127.0.0.1"  # 不要这样做
```

**常用环境变量**：
- 数据库：`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- Redis：`REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`
- JWT：`JWT_SECRET_KEY`, `JWT_ALGORITHM`
- 服务：`HOST`, `PORT`, `DEBUG`, `CORS_ORIGINS`

### 6. 日志记录

```python
from app.utils.logs import getLogger

# 获取模块日志记录器
logger = getLogger('api')  # api.log
db_logger = getLogger('database')  # database.log
app_logger = getLogger('app')  # app.log

# 记录日志
logger.info("用户登录成功", extra={'user_id': user_id})
logger.error("数据库连接失败", exc_info=True)
logger.warning("Token即将过期")
```

**日志级别**：
- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

## 前端开发规范

### 1. API 调用规范

#### 1.1 API 文件组织

```typescript
// src/api/user.ts
import api from './index'

export interface User {
  id: string
  email: string
  nickname: string
}

// 获取列表
export const getUserList = (params?: any) => {
  return api.post<any, { items: User[]; count: number }>('/v1/user/user', params)
}

// 获取单个
export const getUserDetail = (id: string) => {
  return api.get<any, User>(`/v1/user/user/${id}`)
}

// 创建
export const createUser = (data: Partial<User>) => {
  return api.post('/v1/user/user', data)
}

// 更新
export const updateUser = (id: string, data: Partial<User>) => {
  return api.put(`/v1/user/user/${id}`, data)
}

// 删除
export const deleteUser = (id: string) => {
  return api.delete(`/v1/user/user/${id}`)
}
```

#### 1.2 错误处理

```typescript
// ✅ 正确：在组件中处理业务错误
try {
  const result = await createUser(userData)
  message.success('创建成功')
  loadData()
} catch (error) {
  // axios拦截器已经处理了通用错误（401, 403, 500等）
  // 这里只需要处理业务逻辑错误
  console.error('创建用户失败:', error)
}

// ❌ 错误：不要在这里显示通用错误提示
try {
  await createUser(userData)
} catch (error) {
  message.error('创建失败')  // 拦截器已经显示了，不要重复
}
```

### 2. 状态管理规范

#### 2.1 Zustand Store

```typescript
// src/store/useUserStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UserState {
  token: string
  userInfo: User | null
  permissions: string[]
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  hasPermission: (permission: string) => boolean
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      token: '',
      userInfo: null,
      permissions: [],
      
      login: async (email, password) => {
        const res = await loginApi({ email, password })
        set({ token: res.access_token, userInfo: res.user })
      },
      
      logout: () => {
        localStorage.removeItem('access_token')
        set({ token: '', userInfo: null, permissions: [] })
      },
      
      hasPermission: (permission) => {
        const { permissions, userInfo } = get()
        if (userInfo?.roles?.some(role => role.code === 'ADMIN')) {
          return true
        }
        return permissions.includes(permission)
      },
    }),
    {
      name: 'user-storage',
    }
  )
)
```

### 3. 权限控制

#### 3.1 权限组件

```typescript
// 使用权限组件
import Permission from '@/components/Permission'

<Permission permission="user:create">
  <Button>创建用户</Button>
</Permission>

<Permission anyPermissions={['user:edit', 'user:delete']}>
  <Button>操作</Button>
</Permission>
```

#### 3.2 权限Hook

```typescript
// 使用权限Hook
import { usePermission } from '@/hooks/usePermission'

function MyComponent() {
  const { hasPermission } = usePermission()
  
  return (
    <>
      {hasPermission('ADMIN') && <AdminPanel />}
      {hasPermission(['ADMIN', 'GM']) && <ManagerPanel />}
    </>
  )
}
```

### 4. 组件开发规范

#### 4.1 函数组件

```typescript
// ✅ 推荐：使用函数组件 + Hooks
import { useState, useEffect } from 'react'
import { Table, Button } from 'antd'

export default function UserList() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  
  useEffect(() => {
    loadData()
  }, [])
  
  const loadData = async () => {
    setLoading(true)
    try {
      const result = await getUserList()
      setData(result.items)
    } finally {
      setLoading(false)
    }
  }
  
  return <Table dataSource={data} loading={loading} />
}
```

#### 4.2 TypeScript 类型

```typescript
// ✅ 正确：定义清晰的类型
interface User {
  id: string
  email: string
  nickname: string
  roles: Role[]
}

interface Role {
  id: string
  code: string
  name: string
}

// ❌ 错误：使用 any
const user: any = {}  // 不要这样做
```

## 通用规范

### 1. 命名规范

#### 后端（Python）
- **文件名**: `snake_case.py`
- **类名**: `PascalCase`
- **函数名**: `snake_case`
- **变量名**: `snake_case`
- **常量**: `UPPER_SNAKE_CASE`

```python
# 文件: user_service.py
class UserService:
    def get_user_list(self):
        max_count = 100
        API_VERSION = "v1"
```

#### 前端（TypeScript/React）
- **文件名**: `PascalCase.tsx` (组件), `camelCase.ts` (工具)
- **组件名**: `PascalCase`
- **函数名**: `camelCase`
- **变量名**: `camelCase`
- **常量**: `UPPER_SNAKE_CASE`

```typescript
// 文件: UserList.tsx
export default function UserList() {
  const [userList, setUserList] = useState([])
  const MAX_PAGE_SIZE = 100
  
  const loadUserData = async () => {}
}
```

### 2. 注释规范

#### 后端
```python
def create_user(email: str, password: str) -> User:
    """
    创建新用户
    
    Args:
        email: 用户邮箱
        password: 用户密码
        
    Returns:
        User: 创建的用户对象
        
    Raises:
        ValueError: 邮箱格式错误
        HTTPException: 邮箱已存在
    """
    pass
```

#### 前端
```typescript
/**
 * 加载用户列表
 * @param page 页码
 * @param limit 每页数量
 * @returns 用户列表和总数
 */
async function loadUserList(page: number, limit: number) {
  // 实现
}
```

### 3. Git 提交规范

```bash
# 格式: <type>(<scope>): <subject>

# 类型
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关

# 示例
feat(user): 添加用户导出功能
fix(api): 修复Token验证失败的问题
docs(readme): 更新安装说明
refactor(database): 优化数据库查询性能
```

### 4. 代码审查清单

#### 后端
- [ ] 是否添加了认证依赖？
- [ ] 是否使用了读写分离？
- [ ] 异常处理顺序是否正确？
- [ ] 是否预加载了关联数据？
- [ ] 是否添加了数据权限过滤？
- [ ] 路由顺序是否正确？

#### 前端
- [ ] 是否定义了TypeScript类型？
- [ ] 是否添加了权限控制？
- [ ] 是否处理了加载状态？
- [ ] 是否处理了错误情况？
- [ ] 组件是否可复用？

## 常见问题和解决方案

### 1. 路由匹配问题

**问题**：特定路径的API无法访问
**原因**：动态路径在特定路径之前定义
**解决**：调整路由顺序，特定路径在前

### 2. N+1查询问题

**问题**：查询速度慢，数据库查询次数多
**原因**：未预加载关联数据
**解决**：使用 `prefetch_related()` 预加载

### 3. Token过长问题

**问题**：JWT Token超过VARCHAR(255)限制
**原因**：JWT Token约300-350字符
**解决**：使用TEXT字段存储

### 4. 权限验证失败

**问题**：有权限但API返回403
**原因**：Token中的角色信息未更新
**解决**：角色变更后重新生成Token

### 5. CORS错误

**问题**：前端无法访问API
**原因**：CORS配置不正确
**解决**：在.env中添加前端地址到CORS_ORIGINS

## 参考文档

- [权限管理完整文档](../docs/fixes/PERMISSION_COMPLETE.md)
- [JWT Token快速开始](../JWT_TOKEN_QUICK_START.md)
- [数据权限过滤](../DATA_PERMISSION_QUICK_REFERENCE.md)
- [项目结构说明](./structure.md)
- [技术栈说明](./tech.md)
