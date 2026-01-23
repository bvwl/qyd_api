# 权限检查修复

## 问题描述

用户拥有"项目管理员"（GM）角色，但在前端项目列表中看不到编辑和删除按钮。

## 原因分析

前端代码使用 `hasPermission('GM')` 来检查是否是GM角色，但 `hasPermission` 函数原本只检查 `permissions` 数组中的权限字符串，不检查用户的角色代码。

### 问题代码
```typescript
// ProjectList.tsx
const isGM = hasPermission('GM')  // 'GM' 是角色代码，不是权限字符串

// useUserStore.ts (修改前)
hasPermission: (permission: string | string[]) => {
  const { permissions, userInfo } = get()
  
  // 只检查 permissions 数组
  return permissions.includes(permission)  // 'GM' 不在 permissions 中
}
```

## 解决方案

修改 `hasPermission` 函数，使其同时支持：
1. 权限字符串检查（如 'user:create'）
2. 角色代码检查（如 'ADMIN', 'GM', 'IT', 'MANUAL'）

### 修改后的代码

**文件**: `frontend/src/store/useUserStore.ts`

```typescript
hasPermission: (permission: string | string[]) => {
  const { permissions, userInfo } = get()
  
  // 管理员拥有所有权限
  if (userInfo?.roles?.some(role => role.code === 'ADMIN')) {
    return true
  }
  
  // 支持单个权限或权限数组
  if (Array.isArray(permission)) {
    // 检查是否有任何一个权限或角色匹配
    return permission.some(p => {
      // 先检查是否是角色代码
      if (userInfo?.roles?.some(role => role.code === p)) {
        return true
      }
      // 再检查是否是权限字符串
      return permissions.includes(p)
    })
  }
  
  // 单个权限：先检查角色，再检查权限
  if (userInfo?.roles?.some(role => role.code === permission)) {
    return true
  }
  
  return permissions.includes(permission)
}
```

## 工作原理

### 检查顺序
1. **管理员检查**: 如果用户是ADMIN，直接返回true（拥有所有权限）
2. **角色代码检查**: 检查用户的 `roles` 数组中是否有匹配的角色代码
3. **权限字符串检查**: 检查 `permissions` 数组中是否有匹配的权限字符串

### 支持的用法

#### 1. 检查角色
```typescript
const isAdmin = hasPermission('ADMIN')
const isGM = hasPermission('GM')
const isIT = hasPermission('IT')
```

#### 2. 检查权限字符串
```typescript
const canCreateUser = hasPermission('user:create')
const canDeleteProject = hasPermission('project:delete')
```

#### 3. 检查多个权限（任意一个）
```typescript
const canManage = hasPermission(['ADMIN', 'GM'])
const canEdit = hasPermission(['user:edit', 'user:update'])
```

#### 4. 混合检查
```typescript
// 检查是否是管理员或有特定权限
const canAccess = hasPermission(['ADMIN', 'project:view'])
```

## 使用示例

### 项目列表
```typescript
const isAdmin = hasPermission('ADMIN')  // 检查ADMIN角色
const isGM = hasPermission('GM')        // 检查GM角色

{(isAdmin || isGM) && (
  <Button onClick={handleEdit}>编辑</Button>
  <Button onClick={handleDelete}>删除</Button>
)}
```

### 用户列表
```typescript
const isAdmin = hasPermission('ADMIN')

{isAdmin && (
  <Button onClick={handleManageRoles}>管理角色</Button>
)}
```

## 数据结构

### userInfo.roles
```typescript
[
  {
    id: "uuid",
    code: "GM",           // 角色代码
    name: "项目管理员",    // 角色名称
    description: "..."
  }
]
```

### permissions
```typescript
[
  "user:view",
  "user:create",
  "project:view",
  "project:edit",
  // ...
]
```

## 测试验证

### 1. 使用GM账户登录
```typescript
// userInfo.roles
[{ code: "GM", name: "项目管理员" }]

// 测试
hasPermission('GM')      // ✅ true
hasPermission('ADMIN')   // ❌ false
hasPermission(['ADMIN', 'GM'])  // ✅ true
```

### 2. 使用ADMIN账户登录
```typescript
// userInfo.roles
[{ code: "ADMIN", name: "管理员" }]

// 测试
hasPermission('ADMIN')   // ✅ true
hasPermission('GM')      // ✅ true (ADMIN拥有所有权限)
hasPermission('anything') // ✅ true (ADMIN拥有所有权限)
```

### 3. 前端验证
1. 使用GM账户登录
2. 访问项目列表
3. 应该能看到编辑和删除按钮
4. 访问项目钱包
5. 不应该看到编辑和删除按钮

## 优势

1. **向后兼容**: 原有的权限字符串检查仍然有效
2. **灵活性**: 同时支持角色和权限检查
3. **简洁性**: 不需要修改现有的组件代码
4. **一致性**: 所有组件使用相同的权限检查方式

## 注意事项

1. **角色优先**: 先检查角色代码，再检查权限字符串
2. **ADMIN特权**: ADMIN角色始终返回true
3. **大小写敏感**: 角色代码区分大小写（'GM' ≠ 'gm'）
4. **数组检查**: 数组中任意一个匹配即返回true

## 相关文件

- `frontend/src/store/useUserStore.ts` - 权限检查逻辑
- `frontend/src/views/Project/ProjectList.tsx` - 使用示例
- `frontend/src/views/Project/ProjectAccount.tsx` - 使用示例
- `frontend/src/views/Project/ProjectWallet.tsx` - 使用示例

---

**修复时间**: 2026-01-23  
**修复状态**: ✅ 完成  
**测试状态**: 待测试
