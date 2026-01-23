# 企业级 RBAC 快速开始

## 核心概念

```
用户（User）→ 角色（Role）→ 权限（Permission）+ 菜单（Menu）
```

### 关键区别

| 概念 | 用途 | 示例 |
|------|------|------|
| **权限（Permission）** | 控制功能访问 | `user:create`, `project:edit` |
| **菜单（Menu）** | 控制界面显示 | "用户管理", "项目列表" |
| **角色（Role）** | 连接用户和权限/菜单 | "管理员", "项目经理" |

## 快速开始

### 1. 数据迁移（5分钟）

```bash
cd backend
python db/migrate_to_rbac.py
```

### 2. 创建权限（示例）

```python
# 创建一个权限
permission = await Permission.create(
    code="user:create",
    name="创建用户",
    resource="user",
    action="create",
    permission_type=PermissionType.API,
    api_method="POST",
    api_path="/api/v1/users"
)
```

### 3. 创建菜单（示例）

```python
# 创建一个菜单
menu = await Menu.create(
    name="UserList",
    title="用户列表",
    path="/user/list",
    component="views/User/List",
    icon="UserOutlined",
    required_permission="user:view"  # 需要有这个权限才能看到菜单
)
```

### 4. 分配权限给角色

```python
# 获取角色
role = await Role.get(code="GM")

# 分配权限
permissions = await Permission.filter(
    code__in=["user:view", "user:create", "user:edit"]
).all()
await role.permissions.add(*permissions)

# 分配菜单
menus = await Menu.filter(
    name__in=["UserList", "UserCreate"]
).all()
await role.menus.add(*menus)
```

### 5. 使用权限装饰器

```python
from app.utils.rbac import require_permission

@app.post("/users")
@require_permission("user:create")
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    # 只有有 user:create 权限的用户才能访问
    pass
```

### 6. 使用数据权限

```python
from app.utils.rbac import filter_by_data_scope

@app.get("/projects")
async def get_projects(
    current_user: dict = Depends(get_current_user)
):
    query = Project.all()
    
    # 根据用户的数据权限过滤
    query = await filter_by_data_scope(
        query,
        current_user['user_id'],
        'project'
    )
    
    projects = await query.all()
    return projects
```

## 前端使用

### 1. 权限指令

```vue
<template>
  <button v-permission="'user:create'">创建用户</button>
</template>
```

### 2. 权限组件

```tsx
<Permission permission="user:create">
  <Button>创建用户</Button>
</Permission>
```

### 3. 权限检查

```typescript
import { usePermission } from '@/hooks/usePermission'

function MyComponent() {
  const { hasPermission } = usePermission()
  
  if (hasPermission('user:create')) {
    // 显示创建按钮
  }
}
```

## 常用 API

### 权限管理

```bash
# 获取权限列表
GET /api/v1/system/permission

# 创建权限
POST /api/v1/system/permission

# 获取分组的权限
GET /api/v1/system/permission/grouped
```

### 菜单管理

```bash
# 获取菜单树
GET /api/v1/system/menu/tree

# 获取用户菜单
GET /api/v1/system/menu/user

# 创建菜单
POST /api/v1/system/menu
```

### 角色管理

```bash
# 获取角色的权限
GET /api/v1/system/role/{id}/permissions

# 设置角色的权限
POST /api/v1/system/role/{id}/permissions

# 获取角色的菜单
GET /api/v1/system/role/{id}/menus

# 设置角色的菜单
POST /api/v1/system/role/{id}/menus
```

## 数据权限范围

| 范围 | 说明 | 使用场景 |
|------|------|----------|
| **ALL** | 全部数据 | 超级管理员 |
| **DEPT** | 本部门数据 | 部门经理 |
| **DEPT_AND_CHILD** | 本部门及下级部门 | 区域经理 |
| **SELF** | 仅本人数据 | 普通员工 |
| **CUSTOM** | 自定义范围 | 特殊场景 |

## 权限命名规范

```
{resource}:{action}

资源（resource）：
- user      用户
- role      角色
- permission 权限
- menu      菜单
- project   项目
- server    服务器
- mail      邮件

操作（action）：
- view      查看
- create    创建
- edit      编辑
- delete    删除
- export    导出
- import    导入
- assign    分配
```

## 示例：完整的权限配置

```python
# 1. 创建权限
permissions = [
    {"code": "user:view", "name": "查看用户", "resource": "user", "action": "view"},
    {"code": "user:create", "name": "创建用户", "resource": "user", "action": "create"},
    {"code": "user:edit", "name": "编辑用户", "resource": "user", "action": "edit"},
    {"code": "user:delete", "name": "删除用户", "resource": "user", "action": "delete"},
]

for perm_data in permissions:
    await Permission.create(**perm_data, permission_type=PermissionType.API)

# 2. 创建菜单
user_menu = await Menu.create(
    name="UserManagement",
    title="用户管理",
    path="/user",
    icon="UserOutlined",
    sort=1
)

user_list_menu = await Menu.create(
    name="UserList",
    title="用户列表",
    path="/user/list",
    component="views/User/List",
    parent_id=user_menu.id,
    required_permission="user:view",
    sort=1
)

# 3. 创建角色
role = await Role.create(
    name="用户管理员",
    code="USER_ADMIN",
    description="负责用户管理",
    data_scope=DataScope.ALL,
    level=50
)

# 4. 分配权限
perms = await Permission.filter(resource="user").all()
await role.permissions.add(*perms)

# 5. 分配菜单
menus = await Menu.filter(name__in=["UserManagement", "UserList"]).all()
await role.menus.add(*menus)

# 6. 分配给用户
user = await UserInfo.get(email="zhiyu")
await user.roles.add(role)
```

## 故障排查

### 问题1：权限检查失败
```python
# 检查用户的权限
permissions = await get_user_permissions(user_id)
print([p.code for p in permissions])
```

### 问题2：菜单不显示
```python
# 检查用户的菜单
menus = await get_user_menus(user_id)
print(menus)
```

### 问题3：数据权限不生效
```python
# 检查用户的数据范围
data_scope = await get_user_data_scope(user_id)
print(f"数据范围: {data_scope}")
```

## 下一步

- 📖 阅读完整设计文档：[ENTERPRISE_RBAC_DESIGN.md](./ENTERPRISE_RBAC_DESIGN.md)
- 🚀 查看实施指南：[IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)
- 🧪 运行测试：`pytest app/tests/test_rbac.py`

## 总结

这个企业级 RBAC 系统：
- ✅ 职责清晰：权限和菜单分离
- ✅ 灵活强大：支持多种权限类型
- ✅ 易于使用：装饰器和工具函数
- ✅ 标准规范：符合企业级标准

开始使用吧！🎉
