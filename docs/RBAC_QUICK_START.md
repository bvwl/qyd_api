# RBAC 权限管理快速入门

## 概述

本系统实现了完整的 RBAC（基于角色的访问控制）权限管理，支持菜单级和按钮级权限控制。

## 核心概念

### 1. 路由类型（route_type）

- **1 - 菜单（MENU）**: 左侧导航菜单项
- **2 - 按钮（BUTTON）**: 页面内的操作按钮
- **3 - 接口（API）**: 后端API接口

### 2. 权限标识（permission）

权限标识采用 `资源:操作` 的格式，例如：
- `user:view` - 查看用户
- `user:create` - 创建用户
- `user:edit` - 编辑用户
- `user:delete` - 删除用户
- `project:view` - 查看项目
- `project:manage` - 管理项目

### 3. 权限层级

```
用户（User）
  └─ 角色（Role）
      └─ 路由（Route）
          ├─ 菜单（MENU）
          ├─ 按钮（BUTTON）
          └─ 接口（API）
```

## 后端实现

### 1. 数据库迁移

已完成字段添加：
```sql
-- 路由类型
route_type SMALLINT NOT NULL DEFAULT 1

-- 权限标识
permission VARCHAR(128) NULL

-- API方法
api_method VARCHAR(16) NULL

-- API路径
api_path VARCHAR(255) NULL
```

### 2. 初始化路由数据

```bash
cd backend
python db/init_routes.py
```

这会创建27个路由（6个一级菜单 + 21个二级菜单）。

### 3. API 端点

#### 路由管理
- `GET /v1/user/route/tree` - 获取路由树
- `GET /v1/user/route/user-routes` - 获取当前用户的路由权限

#### 角色权限管理
- `GET /v1/user/role/{id}/routes` - 获取角色的路由权限
- `POST /v1/user/role/{id}/routes` - 设置角色的路由权限

### 4. 使用示例

```python
from app.models.user import UserRole, FrontendRoute

# 获取角色
role = await UserRole.get(code="ADMIN")

# 获取所有菜单路由
menu_routes = await FrontendRoute.filter(route_type=1, status=1)

# 为角色分配路由权限
await role.routes.add(*menu_routes)

# 获取角色的所有权限
await role.fetch_related('routes')
permissions = [route.permission for route in role.routes if route.permission]
```

## 前端实现

### 1. 权限 Hook

```typescript
import { usePermission } from '@/hooks/usePermission'

function MyComponent() {
  const { hasPermission, loading } = usePermission()
  
  if (loading) return <div>加载中...</div>
  
  return (
    <div>
      {hasPermission('user:create') && (
        <Button>创建用户</Button>
      )}
    </div>
  )
}
```

### 2. 权限组件

```typescript
import Permission from '@/components/Permission'

// 单个权限
<Permission permission="user:create">
  <Button>创建用户</Button>
</Permission>

// 任意权限（满足一个即可）
<Permission anyPermissions={["user:create", "user:edit"]}>
  <Button>操作</Button>
</Permission>

// 所有权限（需要全部满足）
<Permission allPermissions={["user:view", "user:edit"]}>
  <Button>编辑</Button>
</Permission>
```

### 3. API 调用

```typescript
import { getUserRoutes, getRoleRoutes, setRoleRoutes } from '@/api/user'

// 获取当前用户的路由权限
const routes = await getUserRoutes()

// 获取角色的路由权限
const roleRoutes = await getRoleRoutes(roleId)

// 设置角色的路由权限
await setRoleRoutes(roleId, [routeId1, routeId2])
```

## 管理界面

### 1. 路由管理页面

位置：`/user/route`

功能：
- 查看所有路由
- 创建/编辑/删除路由
- 设置路由类型和权限标识

### 2. 角色管理页面

位置：`/user/role`

功能：
- 查看所有角色
- 创建/编辑/删除角色
- 为角色分配路由权限

### 3. 用户管理页面

位置：`/user/list`

功能：
- 查看所有用户
- 创建/编辑/删除用户
- 为用户分配角色

## 权限配置流程

### 1. 创建路由

```bash
# 方式1：通过初始化脚本（推荐）
python backend/db/init_routes.py

# 方式2：通过管理界面
访问 /user/route 页面手动创建
```

### 2. 创建角色

```bash
# 通过管理界面
访问 /user/role 页面创建角色
```

### 3. 分配权限

```bash
# 通过管理界面
1. 访问 /user/role 页面
2. 点击角色的"权限配置"按钮
3. 选择要分配的路由
4. 保存
```

### 4. 分配角色

```bash
# 通过管理界面
1. 访问 /user/list 页面
2. 点击用户的"编辑"按钮
3. 选择要分配的角色
4. 保存
```

## 常见场景

### 场景1：添加新菜单

1. 在 `backend/db/init_routes.py` 中添加路由数据
2. 运行 `python backend/db/init_routes.py`
3. 在角色管理页面为相应角色分配新菜单权限

### 场景2：添加按钮权限

1. 创建按钮类型的路由（route_type=2）
2. 设置权限标识（如 `user:delete`）
3. 在前端使用 Permission 组件包裹按钮
4. 为角色分配该权限

### 场景3：限制API访问

1. 创建接口类型的路由（route_type=3）
2. 设置 API 方法和路径
3. 在后端中间件中检查权限
4. 为角色分配该权限

## 默认角色

系统初始化时创建了以下角色：

- **ADMIN（管理员）**: 拥有所有权限
- **GM（游戏管理员）**: 拥有项目和服务器管理权限
- **USER（普通用户）**: 拥有基本查看权限

## 注意事项

1. **权限标识命名规范**: 使用 `资源:操作` 格式，保持一致性
2. **路由排序**: sort 字段越小越靠前
3. **隐藏菜单**: is_hidden=true 的菜单不会在导航中显示
4. **缓存页面**: is_cache=true 的页面会被缓存
5. **权限继承**: 子路由会继承父路由的权限要求

## 故障排查

### 问题1：用户看不到菜单

检查：
1. 用户是否分配了角色
2. 角色是否分配了对应的路由权限
3. 路由的 status 是否为 1（正常）
4. 路由的 is_hidden 是否为 false

### 问题2：按钮不显示

检查：
1. 是否使用了 Permission 组件
2. permission 属性是否正确
3. 用户的角色是否有该权限

### 问题3：API 返回 403

检查：
1. 后端是否实现了权限检查中间件
2. 用户的角色是否有对应的 API 权限
3. 路由配置中的 api_path 是否正确

## 相关文档

- [RBAC 设计文档](./RBAC_DESIGN.md)
- [项目结构文档](./PROJECT_STRUCTURE.md)
- [API 文档](http://127.0.0.1:6080/docs)
