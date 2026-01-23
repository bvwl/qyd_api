# RBAC API 快速参考

## 当前可用的API列表

### 🔐 用户权限 (3个接口)

| 方法 | 路径 | 说明 | 权限 | 频率 |
|------|------|------|------|------|
| GET | `/v1/rbac/user/menus` | 获取当前用户的菜单树 | 登录用户 | 高 |
| GET | `/v1/rbac/user/permissions` | 获取当前用户的权限列表 | 登录用户 | 高 |
| GET | `/v1/rbac/user/has-permission` | 检查是否有指定权限 | 登录用户 | 中 |

### 📋 菜单管理 (6个接口)

| 方法 | 路径 | 说明 | 权限 | 频率 |
|------|------|------|------|------|
| GET | `/v1/rbac/menu/tree` | 获取菜单树 | 登录用户 | 高 |
| GET | `/v1/rbac/menu` | 获取菜单列表（分页） | 登录用户 | 中 |
| GET | `/v1/rbac/menu/{id}` | 获取菜单详情 | 登录用户 | 低 |
| POST | `/v1/rbac/menu` | 创建菜单 | 管理员 | 低 |
| PUT | `/v1/rbac/menu/{id}` | 更新菜单 | 管理员 | 低 |
| DELETE | `/v1/rbac/menu/{id}` | 删除菜单 | 管理员 | 低 |

### 👥 角色管理 (7个接口)

| 方法 | 路径 | 说明 | 权限 | 频率 |
|------|------|------|------|------|
| GET | `/v1/rbac/role` | 获取角色列表 | 登录用户 | 中 |
| GET | `/v1/rbac/role/{id}` | 获取角色详情 | 登录用户 | 低 |
| POST | `/v1/rbac/role` | 创建角色 | 管理员 | 低 |
| PUT | `/v1/rbac/role/{id}` | 更新角色 | 管理员 | 低 |
| DELETE | `/v1/rbac/role/{id}` | 删除角色 | 管理员 | 低 |
| GET | `/v1/rbac/role/{id}/menus` | 获取角色的菜单 | 登录用户 | 中 |
| POST | `/v1/rbac/role/{id}/menus` | 设置角色的菜单 | 管理员 | 中 |

**总计：16个接口**

## 使用示例

### 1. 用户登录后获取菜单和权限

```typescript
// 登录成功后
const { data: menus } = await getUserMenus()
const { data: permissions } = await getUserPermissions()

// 存储到状态管理
store.setMenus(menus)
store.setPermissions(permissions)
```

### 2. 检查用户权限

```typescript
// 方式1：使用API检查
const { data } = await checkUserPermission('user:create')
if (data.has_permission) {
  // 有权限
}

// 方式2：使用本地权限列表检查
const permissions = store.getPermissions()
if (permissions.includes('user:create')) {
  // 有权限
}
```

### 3. 管理菜单

```typescript
// 获取菜单树（用于显示和编辑）
const { data: tree } = await getMenuTree({ status: 1 })

// 创建菜单
await createMenu({
  code: 'user_management',
  title: '用户管理',
  path: '/user',
  icon: 'UserOutlined',
  sort: 1
})

// 更新菜单
await updateMenu(menuId, {
  title: '用户管理（新）',
  sort: 2
})

// 删除菜单
await deleteMenu(menuId)
```

### 4. 管理角色

```typescript
// 获取角色列表
const { data } = await getRoleList({ page: 1, limit: 10 })

// 创建角色
const { data: newRole } = await createRole({
  code: 'OPERATOR',
  name: '操作员',
  description: '普通操作员角色',
  level: 3,
  data_scope: 2
})

// 获取角色的菜单（用于编辑）
const { data: menuIds } = await getRoleMenus(roleId)

// 设置角色的菜单
await setRoleMenus(roleId, ['menu-id-1', 'menu-id-2', 'menu-id-3'])

// 更新角色
await updateRole(roleId, {
  name: '高级操作员',
  level: 2
})

// 删除角色
await deleteRole(roleId)
```

## 权限模型

### 数据流

```
用户登录
  ↓
获取用户角色
  ↓
获取角色关联的菜单
  ↓
构建菜单树和权限列表
  ↓
前端渲染菜单和控制权限
```

### 权限判断

```typescript
// 1. 菜单级别权限（显示/隐藏菜单）
const menus = await getUserMenus()
// 只显示用户有权限的菜单

// 2. 按钮级别权限（显示/隐藏按钮）
const permissions = await getUserPermissions()
if (permissions.includes('user:create')) {
  // 显示"创建用户"按钮
}

// 3. API级别权限（后端验证）
// 后端通过JWT Token验证用户身份和权限
```

## 数据结构

### Menu（菜单）

```typescript
interface Menu {
  id: string
  code: string              // 菜单编码（唯一）
  title: string             // 菜单标题
  path: string              // 路由路径
  component?: string        // 组件路径
  icon?: string             // 图标
  sort: number              // 排序
  parent_id?: string        // 父菜单ID
  is_hidden: boolean        // 是否隐藏
  is_cache: boolean         // 是否缓存
  is_affix: boolean         // 是否固定
  redirect?: string         // 重定向路径
  status: number            // 状态（1:启用 0:禁用）
  children?: Menu[]         // 子菜单
}
```

### Role（角色）

```typescript
interface Role {
  id: string
  code: string              // 角色编码（唯一）
  name: string              // 角色名称
  description?: string      // 描述
  level: number             // 级别（数字越小权限越高）
  data_scope: number        // 数据范围（1:全部 2:本部门 3:本人）
  is_system: boolean        // 是否系统角色（不可删除）
  status: number            // 状态（1:启用 0:禁用）
}
```

## 常见问题

### Q1: 如何添加新菜单？

1. 使用 `POST /v1/rbac/menu` 创建菜单
2. 使用 `POST /v1/rbac/role/{id}/menus` 将菜单分配给角色
3. 用户重新登录或刷新页面即可看到新菜单

### Q2: 如何控制按钮权限？

```typescript
// 方式1：使用Permission组件
<Permission permission="user:create">
  <Button>创建用户</Button>
</Permission>

// 方式2：使用usePermission hook
const { hasPermission } = usePermission()
{hasPermission('user:create') && <Button>创建用户</Button>}
```

### Q3: 角色的菜单如何保存？

前端传递所有选中的菜单ID（包括半选的父节点），后端会自动补全所有父级菜单，确保菜单树完整。

```typescript
// 前端：传递所有选中的节点（包括半选）
await setRoleMenus(roleId, ['menu-1', 'menu-2', 'menu-3'])

// 后端：自动补全父级菜单
// 如果 menu-1 的父菜单是 menu-parent，会自动添加 menu-parent
```

### Q4: 如何实现数据权限？

通过角色的 `data_scope` 字段：

- `1` - 全部数据：可以查看所有数据
- `2` - 本部门：只能查看本部门的数据
- `3` - 本人：只能查看自己的数据

后端在查询数据时根据 `data_scope` 自动过滤。

## 相关文档

- [RBAC清理总结](./RBAC_CLEANUP_SUMMARY.md)
- [RBAC未使用API分析](./RBAC_UNUSED_APIS.md)
- [JWT认证文档](./JWT_AUTH_ONLY.md)
- [Swagger使用指南](./SWAGGER_JWT_GUIDE.md)
