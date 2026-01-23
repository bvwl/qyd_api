# 前端权限管理修复

## 问题
前端权限管理页面显示"加载权限失败"错误。

## 原因
前端路由使用的是 `PermissionManageWorking.tsx` 组件，该组件使用旧的API响应格式：
- **旧格式**: 返回路由数组 `[route1, route2, ...]`
- **新格式**: 返回对象 `{ tree: [...], checked_keys: [...] }`

## 修复内容

### 文件: `frontend/src/views/User/PermissionManageWorking.tsx`

#### 修改前
```typescript
const handleSelectRole = async (role: Role) => {
  const response = await fetch(`/v1/user/role/${role.id}/routes`, ...)
  const routes = await response.json()
  
  if (response.ok) {
    const ids = extractIds(routes)  // 提取所有节点ID
    setCheckedKeys(ids)
  }
}
```

#### 修改后
```typescript
const handleSelectRole = async (role: Role) => {
  const response = await fetch(`/v1/user/role/${role.id}/routes`, ...)
  const data = await response.json()
  
  if (response.ok) {
    // 新的API返回格式: { tree: [...], checked_keys: [...] }
    // checked_keys 只包含叶子节点
    if (data && data.checked_keys && Array.isArray(data.checked_keys)) {
      setCheckedKeys(data.checked_keys)
    }
  }
}
```

## 关键改进

1. **使用新的响应格式**: 从 `data.checked_keys` 获取选中的节点
2. **只设置叶子节点**: `checked_keys` 只包含叶子节点，Tree组件会自动计算父节点的半选状态
3. **删除 extractIds 函数**: 不再需要手动提取所有节点ID

## 测试

### 测试步骤
1. 打开权限管理页面 `/user/permission`
2. 选择一个角色
3. 查看权限树是否正确加载
4. 验证选中状态是否正确

### 预期结果
- ✅ 权限树正确加载
- ✅ 只有叶子节点被标记为选中
- ✅ 父节点显示正确的半选状态
- ✅ 未选中的子节点保持未选中

## 相关文件

- `frontend/src/views/User/PermissionManageWorking.tsx` - 实际使用的组件
- `frontend/src/views/User/PermissionManage.tsx` - 备用组件（已更新但未使用）
- `frontend/src/router/index.tsx` - 路由配置

## 注意事项

前端有两个权限管理组件：
1. `PermissionManageWorking.tsx` - 当前使用的组件（已修复）
2. `PermissionManage.tsx` - 备用组件（也已修复）

如果将来需要切换组件，两个组件都已经支持新的API格式。

---

**修复时间**: 2026-01-23  
**修复状态**: ✅ 完成
