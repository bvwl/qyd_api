# RBAC v2 前端集成指南

## 📋 已完成的调整

### 1. API 调用层 ✅

创建了 `frontend/src/api/rbac.ts`，包含：

- **用户权限 API**
  - `getUserMenus()` - 获取当前用户的菜单树
  - `getUserPermissions()` - 获取当前用户的权限列表
  - `checkUserPermission()` - 检查是否有指定权限

- **菜单管理 API**
  - `getMenuTree()` - 获取菜单树
  - `getMenuList()` - 获取菜单列表（分页）
  - `createMenu()` - 创建菜单
  - `updateMenu()` - 更新菜单
  - `deleteMenu()` - 删除菜单

- **权限管理 API**（待后端实现）
  - `getPermissionsGrouped()` - 获取分组权限
  - `getPermissionList()` - 获取权限列表
  - `createPermission()` - 创建权限

- **角色管理 API**（待后端实现）
  - `getRoleList()` - 获取角色列表
  - `getRoleMenus()` - 获取角色的菜单
  - `setRoleMenus()` - 设置角色的菜单
  - `getRolePermissions()` - 获取角色的权限
  - `setRolePermissions()` - 设置角色的权限

### 2. 状态管理 ✅

更新了 `frontend/src/store/useUserStore.ts`：

**新增字段：**
- `menus: Menu[]` - 用户的菜单列表

**新增方法：**
- `fetchUserPermissions()` - 获取用户权限
- `fetchUserMenus()` - 获取用户菜单
- `hasAnyPermission()` - 检查是否有任意权限
- `hasAllPermissions()` - 检查是否有所有权限

**优化：**
- 登录时自动获取权限和菜单
- 支持单个权限或权限数组检查
- 管理员自动拥有所有权限

### 3. 权限 Hook ✅

更新了 `frontend/src/hooks/usePermission.ts`：

**简化实现：**
- 直接使用 `useUserStore` 中的权限数据
- 不再需要单独加载权限
- 移除了 loading 状态（权限在登录时已加载）

**新增方法：**
- `isAdmin()` - 检查是否是管理员

### 4. 权限组件 ✅

更新了 `frontend/src/components/Permission/index.tsx`：

**优化：**
- 移除了 loading 状态检查
- 使用新的 Hook 实现
- 保持原有的 API 不变

## 🚀 使用指南

### 1. 登录后自动获取权限

```typescript
// 登录时会自动获取权限和菜单
const { login } = useUserStore()
await login(email, password)

// 权限和菜单已经加载到 store 中
```

### 2. 在组件中使用权限

```typescript
import { usePermission } from '@/hooks/usePermission'

function MyComponent() {
  const { hasPermission, isAdmin } = usePermission()
  
  return (
    <div>
      {/* 检查单个权限 */}
      {hasPermission('user:create') && (
        <Button>创建用户</Button>
      )}
      
      {/* 检查多个权限（任意一个） */}
      {hasPermission(['user:edit', 'user:delete']) && (
        <Button>操作</Button>
      )}
      
      {/* 检查是否是管理员 */}
      {isAdmin() && (
        <Button>管理员功能</Button>
      )}
    </div>
  )
}
```

### 3. 使用权限组件

```typescript
import Permission from '@/components/Permission'

function MyComponent() {
  return (
    <div>
      {/* 单个权限 */}
      <Permission permission="user:create">
        <Button>创建用户</Button>
      </Permission>
      
      {/* 任意权限 */}
      <Permission anyPermissions={['user:edit', 'user:delete']}>
        <Button>操作</Button>
      </Permission>
      
      {/* 所有权限 */}
      <Permission allPermissions={['user:view', 'user:edit']}>
        <Button>编辑</Button>
      </Permission>
      
      {/* 无权限时显示替代内容 */}
      <Permission 
        permission="user:create"
        fallback={<span>无权限</span>}
      >
        <Button>创建用户</Button>
      </Permission>
    </div>
  )
}
```

### 4. 获取用户菜单

```typescript
import { useUserStore } from '@/store/useUserStore'

function MyComponent() {
  const { menus } = useUserStore()
  
  // menus 是树形结构的菜单列表
  return (
    <Menu>
      {menus.map(menu => (
        <Menu.Item key={menu.id}>
          {menu.title}
        </Menu.Item>
      ))}
    </Menu>
  )
}
```

### 5. 手动刷新权限

```typescript
import { useUserStore } from '@/store/useUserStore'

function MyComponent() {
  const { fetchUserPermissions, fetchUserMenus } = useUserStore()
  
  const handleRefresh = async () => {
    await fetchUserPermissions()
    await fetchUserMenus()
  }
  
  return <Button onClick={handleRefresh}>刷新权限</Button>
}
```

## 📝 权限命名规范

### 格式

```
{resource}:{action}
```

### 示例

```typescript
// 用户管理
'user:view'      // 查看用户
'user:create'    // 创建用户
'user:edit'      // 编辑用户
'user:delete'    // 删除用户
'user:export'    // 导出用户

// 项目管理
'project:view'   // 查看项目
'project:create' // 创建项目
'project:edit'   // 编辑项目
'project:delete' // 删除项目

// 服务器管理
'server:view'    // 查看服务器
'server:create'  // 创建服务器
'server:edit'    // 编辑服务器
'server:delete'  // 删除服务器
```

## 🎯 实际应用示例

### 示例 1：用户列表页面

```typescript
import { useState, useEffect } from 'react'
import { Table, Button, Space } from 'antd'
import Permission from '@/components/Permission'
import { usePermission } from '@/hooks/usePermission'
import { getUserList, deleteUser } from '@/api/user'

export default function UserList() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const { hasPermission } = usePermission()
  
  useEffect(() => {
    loadUsers()
  }, [])
  
  const loadUsers = async () => {
    setLoading(true)
    try {
      const res = await getUserList()
      setUsers(res.data.items)
    } finally {
      setLoading(false)
    }
  }
  
  const handleDelete = async (id: string) => {
    await deleteUser(id)
    loadUsers()
  }
  
  const columns = [
    { title: '邮箱', dataIndex: 'email' },
    { title: '昵称', dataIndex: 'nickname' },
    {
      title: '操作',
      render: (_, record) => (
        <Space>
          {/* 只有有编辑权限的用户才能看到编辑按钮 */}
          <Permission permission="user:edit">
            <Button size="small">编辑</Button>
          </Permission>
          
          {/* 只有有删除权限的用户才能看到删除按钮 */}
          <Permission permission="user:delete">
            <Button 
              size="small" 
              danger
              onClick={() => handleDelete(record.id)}
            >
              删除
            </Button>
          </Permission>
        </Space>
      )
    }
  ]
  
  return (
    <div>
      {/* 只有有创建权限的用户才能看到创建按钮 */}
      <Permission permission="user:create">
        <Button type="primary" style={{ marginBottom: 16 }}>
          创建用户
        </Button>
      </Permission>
      
      <Table 
        columns={columns}
        dataSource={users}
        loading={loading}
        rowKey="id"
      />
    </div>
  )
}
```

### 示例 2：项目详情页面

```typescript
import { useState, useEffect } from 'react'
import { Descriptions, Button, Space } from 'antd'
import { usePermission } from '@/hooks/usePermission'
import { getProjectDetail } from '@/api/project'

export default function ProjectDetail({ id }: { id: string }) {
  const [project, setProject] = useState(null)
  const { hasPermission, hasAnyPermission } = usePermission()
  
  useEffect(() => {
    loadProject()
  }, [id])
  
  const loadProject = async () => {
    const res = await getProjectDetail(id)
    setProject(res.data)
  }
  
  return (
    <div>
      <Descriptions title="项目信息">
        <Descriptions.Item label="项目名称">
          {project?.name}
        </Descriptions.Item>
        <Descriptions.Item label="项目描述">
          {project?.description}
        </Descriptions.Item>
      </Descriptions>
      
      {/* 只有有编辑或删除权限的用户才能看到操作按钮 */}
      {hasAnyPermission(['project:edit', 'project:delete']) && (
        <Space style={{ marginTop: 16 }}>
          {hasPermission('project:edit') && (
            <Button type="primary">编辑</Button>
          )}
          {hasPermission('project:delete') && (
            <Button danger>删除</Button>
          )}
        </Space>
      )}
    </div>
  )
}
```

### 示例 3：动态菜单

```typescript
import { Menu } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useUserStore } from '@/store/useUserStore'
import * as Icons from '@ant-design/icons'

export default function DynamicMenu() {
  const navigate = useNavigate()
  const { menus } = useUserStore()
  
  const getIcon = (iconName?: string) => {
    if (!iconName) return null
    const Icon = Icons[iconName as keyof typeof Icons]
    return Icon ? <Icon /> : null
  }
  
  const renderMenuItems = (menuList: any[]) => {
    return menuList.map(menu => {
      if (menu.children && menu.children.length > 0) {
        return (
          <Menu.SubMenu
            key={menu.id}
            icon={getIcon(menu.icon)}
            title={menu.title}
          >
            {renderMenuItems(menu.children)}
          </Menu.SubMenu>
        )
      }
      
      return (
        <Menu.Item
          key={menu.id}
          icon={getIcon(menu.icon)}
          onClick={() => navigate(menu.path)}
        >
          {menu.title}
        </Menu.Item>
      )
    })
  }
  
  return (
    <Menu mode="inline">
      {renderMenuItems(menus)}
    </Menu>
  )
}
```

## 🔄 迁移指南

### 从旧的权限系统迁移

如果你之前使用的是基于路由的权限系统，需要做以下调整：

#### 1. 更新权限检查

```typescript
// 旧方式
const routes = await getUserRoutes()
const hasPermission = routes.some(r => r.permission === 'user:create')

// 新方式
const { hasPermission } = usePermission()
const canCreate = hasPermission('user:create')
```

#### 2. 更新菜单获取

```typescript
// 旧方式
const routes = await getUserRoutes()
// 需要手动过滤菜单类型

// 新方式
const { menus } = useUserStore()
// 直接使用菜单数据
```

#### 3. 更新权限组件

```typescript
// 旧方式
<Permission permission="UserCreate">
  <Button>创建</Button>
</Permission>

// 新方式
<Permission permission="user:create">
  <Button>创建</Button>
</Permission>
```

## ⚠️ 注意事项

### 1. 权限命名

- 使用小写字母
- 使用冒号分隔资源和操作
- 保持一致性

### 2. 管理员权限

- 管理员（ADMIN）自动拥有所有权限
- 不需要单独检查管理员角色

### 3. 权限缓存

- 权限在登录时加载
- 存储在 localStorage 中
- 刷新页面不会丢失

### 4. 权限更新

- 角色权限变更后，用户需要重新登录
- 或者调用 `fetchUserPermissions()` 手动刷新

## 📚 API 参考

### useUserStore

```typescript
interface UserState {
  token: string
  userInfo: User | null
  permissions: string[]
  menus: Menu[]
  isLoggedIn: boolean
  
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchUserInfo: () => Promise<void>
  fetchUserPermissions: () => Promise<void>
  fetchUserMenus: () => Promise<void>
  hasPermission: (permission: string | string[]) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
}
```

### usePermission

```typescript
interface UsePermission {
  permissions: string[]
  isAdmin: () => boolean
  hasPermission: (permission: string | string[]) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
}
```

### Permission 组件

```typescript
interface PermissionProps {
  permission?: string
  anyPermissions?: string[]
  allPermissions?: string[]
  children: ReactNode
  fallback?: ReactNode
}
```

## 🎉 总结

前端已经完成了 RBAC v2 的集成，主要变化：

1. ✅ 新增 RBAC API 调用层
2. ✅ 更新状态管理（支持菜单和权限）
3. ✅ 简化权限 Hook
4. ✅ 优化权限组件
5. ✅ 保持向后兼容

现在你可以：
- 使用新的权限 API
- 获取用户的菜单和权限
- 使用权限组件控制 UI 显示
- 动态生成菜单

所有功能都已经就绪，可以开始使用了！🎊
