# RBAC v2 快速开始

## 🚀 5分钟快速上手

### 步骤 1：初始化数据

```bash
# 执行初始化脚本（创建菜单、权限、角色）
python backend/db/init_rbac_v2.py
```

**输出示例：**
```
============================================================
初始化 RBAC v2 数据
============================================================

初始化菜单...
  ✓ 创建菜单: 仪表盘
  ✓ 创建菜单: 用户管理
  ...
✓ 菜单初始化完成，共创建 16 个菜单

初始化权限...
  ✓ 创建权限: 查看用户 (user:view)
  ✓ 创建权限: 创建用户 (user:create)
  ...
✓ 权限初始化完成，共创建 49 个权限

...

✓ RBAC v2 数据初始化完成！

默认管理员账号：
  邮箱: zhiyu
  密码: 2201101122@qq.com
```

### 步骤 2：启动服务

```bash
# 启动后端服务
python backend/start.py
```

### 步骤 3：测试 API

```bash
# 运行测试脚本
chmod +x test_rbac_v2.sh
./test_rbac_v2.sh
```

## 📖 API 使用示例

### 1. 登录获取 Token

```bash
curl -X POST "http://localhost:6080/v1/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }'
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer"
  }
}
```

### 2. 获取当前用户的菜单

```bash
curl -X GET "http://localhost:6080/v1/rbac/user/menus" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": "...",
      "code": "dashboard",
      "title": "仪表盘",
      "path": "/dashboard",
      "icon": "DashboardOutlined",
      "children": []
    },
    {
      "id": "...",
      "code": "user-management",
      "title": "用户管理",
      "path": "/user",
      "icon": "UserOutlined",
      "children": [
        {
          "id": "...",
          "code": "user-list",
          "title": "用户列表",
          "path": "/user/list"
        }
      ]
    }
  ],
  "count": 5
}
```

### 3. 获取当前用户的权限

```bash
curl -X GET "http://localhost:6080/v1/rbac/user/permissions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    "user:view",
    "user:create",
    "user:edit",
    "user:delete",
    "user:export",
    "project:view",
    "project:create",
    ...
  ],
  "count": 49
}
```

### 4. 检查是否有指定权限

```bash
curl -X GET "http://localhost:6080/v1/rbac/user/has-permission?code=user:create" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "has_permission": true
  }
}
```

### 5. 获取菜单树

```bash
curl -X GET "http://localhost:6080/v1/rbac/menu/tree" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. 获取菜单列表（分页）

```bash
curl -X GET "http://localhost:6080/v1/rbac/menu?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 💻 代码集成示例

### 后端：使用权限装饰器

```python
from fastapi import APIRouter, Depends
from app.apis.deps import get_current_user
from app.utils.rbac_v2 import require_permission

app = APIRouter()

# 单个权限
@app.post("/user")
@require_permission("user:create")
async def create_user(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    # 只有拥有 user:create 权限的用户才能访问
    return {"message": "用户创建成功"}

# 任意权限（满足其一即可）
from app.utils.rbac_v2 import require_any_permission

@app.put("/user/{id}")
@require_any_permission("user:edit", "user:delete")
async def update_user(
    id: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    # 拥有 user:edit 或 user:delete 权限即可访问
    return {"message": "用户更新成功"}

# 所有权限（必须全部满足）
from app.utils.rbac_v2 import require_all_permissions

@app.delete("/user/{id}")
@require_all_permissions("user:view", "user:delete")
async def delete_user(
    id: str,
    current_user: dict = Depends(get_current_user)
):
    # 必须同时拥有 user:view 和 user:delete 权限
    return {"message": "用户删除成功"}
```

### 后端：手动检查权限

```python
from app.utils.rbac_v2 import check_permission

@app.get("/user/{id}")
async def get_user(
    id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user['user_id']
    
    # 手动检查权限
    has_perm = await check_permission(user_id, "user:view")
    
    if not has_perm:
        raise HTTPException(status_code=403, detail="没有查看权限")
    
    # 业务逻辑
    return {"user": {...}}
```

### 后端：数据权限过滤

```python
from app.utils.rbac_v2 import filter_by_data_scope
from app.models.project import ProjectInfo

@app.get("/projects")
async def get_projects(
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user['user_id']
    
    # 原始查询
    query = ProjectInfo.all()
    
    # 根据用户的数据权限范围自动过滤
    query = await filter_by_data_scope(user_id, 'project', query)
    
    # 执行查询
    projects = await query
    
    return {"projects": projects}
```

### 前端：权限组件（待实现）

```typescript
// Permission.tsx
import { usePermission } from '@/hooks/usePermission'

interface PermissionProps {
  permission: string | string[]
  children: React.ReactNode
}

export default function Permission({ permission, children }: PermissionProps) {
  const { hasPermission } = usePermission()
  
  const permissions = Array.isArray(permission) ? permission : [permission]
  const hasAnyPermission = permissions.some(p => hasPermission(p))
  
  return hasAnyPermission ? <>{children}</> : null
}

// 使用
<Permission permission="user:create">
  <Button>创建用户</Button>
</Permission>

<Permission permission={["user:edit", "user:delete"]}>
  <Button>操作</Button>
</Permission>
```

### 前端：权限 Hook（待实现）

```typescript
// usePermission.ts
import { useUserStore } from '@/store/useUserStore'

export function usePermission() {
  const { userInfo, permissions } = useUserStore()
  
  const hasPermission = (permission: string | string[]) => {
    // 管理员拥有所有权限
    if (userInfo?.roles?.some(r => r.code === 'ADMIN')) {
      return true
    }
    
    const perms = Array.isArray(permission) ? permission : [permission]
    return perms.some(p => permissions.includes(p))
  }
  
  return { hasPermission }
}

// 使用
function MyComponent() {
  const { hasPermission } = usePermission()
  
  return (
    <div>
      {hasPermission('user:create') && (
        <Button>创建用户</Button>
      )}
      
      {hasPermission(['user:edit', 'user:delete']) && (
        <Button>操作</Button>
      )}
    </div>
  )
}
```

## 🎯 常见场景

### 场景 1：创建新的资源权限

```python
# 1. 批量创建权限
from app.utils.rbac_v2 import create_permissions_batch

permissions = await create_permissions_batch(
    resource='order',  # 资源类型
    actions=['view', 'create', 'edit', 'delete', 'export'],  # 操作
    group='order'  # 分组
)

# 2. 分配给角色
role = await Role.get(code='GM')
await role.permissions.add(*permissions)
```

### 场景 2：创建新菜单

```python
from app.models.rbac_v2 import Menu

# 1. 创建一级菜单
order_menu = await Menu.create(
    code='order-management',
    title='订单管理',
    path='/order',
    icon='ShoppingOutlined',
    sort=6
)

# 2. 创建二级菜单
order_list = await Menu.create(
    code='order-list',
    title='订单列表',
    path='/order/list',
    component='views/Order/List',
    parent_id=order_menu.id,
    sort=1
)

# 3. 分配给角色
role = await Role.get(code='GM')
await role.menus.add(order_menu, order_list)
```

### 场景 3：创建新角色

```python
from app.models.rbac_v2 import Role, DataScope

# 1. 创建角色
sales_role = await Role.create(
    code='SALES',
    name='销售人员',
    description='管理订单和客户',
    level=40,
    data_scope=DataScope.DEPT
)

# 2. 分配菜单
menus = await Menu.filter(code__in=['dashboard', 'order-list']).all()
await sales_role.menus.add(*menus)

# 3. 分配权限
permissions = await Permission.filter(
    resource__in=['order', 'customer']
).all()
await sales_role.permissions.add(*permissions)

# 4. 分配给用户
user = await UserInfo.get(email='sales@example.com')
await user.roles_v2.add(sales_role)
```

## 📚 更多文档

- [完整设计文档](docs/rbac/MODERN_RBAC_DESIGN.md)
- [v1 vs v2 对比](docs/rbac/V1_VS_V2_COMPARISON.md)
- [实施总结](RBAC_V2_IMPLEMENTATION.md)
- [API 文档](http://localhost:6080/docs)

## ❓ 常见问题

### Q1: 如何重新初始化数据？

```bash
# 删除旧数据（可选）
# 然后重新运行初始化脚本
python backend/db/init_rbac_v2.py
```

### Q2: 如何查看所有权限？

```bash
curl -X GET "http://localhost:6080/v1/rbac/user/permissions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Q3: 如何给用户分配角色？

```python
from app.models.user import UserInfo
from app.models.rbac_v2 import Role

user = await UserInfo.get(email='user@example.com')
role = await Role.get(code='GM')
await user.roles_v2.add(role)
```

### Q4: 权限不生效怎么办？

1. 检查用户是否有对应角色
2. 检查角色是否有对应权限
3. 检查权限状态是否为正常（status=1）
4. 重新登录获取新的 Token

## 🎉 开始使用

现在你已经了解了 RBAC v2 的基本使用方法，开始构建你的权限系统吧！

如有问题，请查看完整文档或联系开发团队。
