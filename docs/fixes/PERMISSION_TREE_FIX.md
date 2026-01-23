# 权限树父节点丢失问题修复

## 问题描述

在权限管理页面，当取消勾选某个二级菜单时，整个一级菜单都被取消了。

### 复现步骤

1. 打开权限管理页面
2. 选择"手动操作员"角色
3. 勾选"服务器管理"下的所有子菜单
4. 取消勾选其中一个子菜单（如"国家管理"）
5. 点击"保存权限"
6. 刷新页面，重新查看该角色的权限

**问题现象：** "服务器管理"整个父菜单都消失了，而不是只取消"国家管理"。

## 问题原因

Ant Design 的 `Tree` 组件在默认模式下，`onCheck` 事件返回的 `checked` 数组只包含**完全选中的节点**：

- 如果一个父节点的所有子节点都被选中，`checked` 包含父节点ID
- 如果一个父节点只有部分子节点被选中（半选状态），`checked` **不包含**父节点ID，只包含被选中的子节点ID

### 示例

```typescript
// 树形结构
{
  key: 'server',
  title: '服务器管理',
  children: [
    { key: 'server-country', title: '国家管理' },
    { key: 'server-group', title: '分组管理' },
    { key: 'server-list', title: '服务器列表' }
  ]
}

// 全选时，onCheck 返回：
['server', 'server-country', 'server-group', 'server-list']

// 取消"国家管理"后，onCheck 返回：
['server-group', 'server-list']  // ❌ 缺少父节点 'server'
```

当保存权限时，后端只保存了 `['server-group', 'server-list']`，导致父节点 `'server'` 丢失。

## 解决方案

在保存权限时，自动添加所有选中节点的父节点ID。

### 代码修改

**文件：** `frontend/src/views/User/PermissionManage.tsx`

#### 1. 新增函数：获取所有父节点

```typescript
// 获取所有选中节点及其父节点的key
const getAllParentKeys = (selectedKeys: string[], nodes: DataNode[]): string[] => {
  const result = new Set<string>(selectedKeys)
  
  // 递归查找每个选中节点的所有父节点
  const findParents = (targetKey: string, currentNodes: DataNode[], parents: string[] = []): boolean => {
    for (const node of currentNodes) {
      const currentPath = [...parents, node.key as string]
      
      if (node.key === targetKey) {
        // 找到目标节点，将所有父节点加入结果集
        parents.forEach(parentKey => result.add(parentKey))
        return true
      }
      
      if (node.children) {
        if (findParents(targetKey, node.children, currentPath)) {
          return true
        }
      }
    }
    return false
  }
  
  // 为每个选中的key查找其父节点
  selectedKeys.forEach(key => {
    findParents(key, nodes)
  })
  
  return Array.from(result)
}
```

#### 2. 修改保存函数

```typescript
// 保存权限配置
const handleSave = async () => {
  if (!selectedRole) {
    message.warning('请先选择角色')
    return
  }

  try {
    setSaving(true)
    // 获取所有需要保存的节点ID（包括父节点）
    const allKeysToSave = getAllParentKeys(checkedKeys, routeTree)
    console.log('保存的权限ID:', allKeysToSave)
    await setRoleRoutes(selectedRole.id, allKeysToSave)
    message.success('权限保存成功')
  } catch (error) {
    message.error('权限保存失败')
  } finally {
    setSaving(false)
  }
}
```

### 工作原理

1. 用户勾选/取消勾选节点时，`checkedKeys` 只包含完全选中的节点
2. 保存时，`getAllParentKeys` 函数遍历所有选中的节点
3. 对于每个选中的节点，递归查找其所有父节点
4. 将父节点ID也加入到保存列表中
5. 最终保存的ID列表包含：选中的节点 + 它们的所有父节点

### 示例

```typescript
// 用户选中的节点
checkedKeys = ['server-group', 'server-list']

// getAllParentKeys 处理后
allKeysToSave = ['server', 'server-group', 'server-list']
//                 ↑ 自动添加的父节点
```

## 测试验证

### 测试文件

创建了测试页面：`frontend/tests/test-permission-tree.html`

在浏览器中打开该文件，可以看到修复前后的对比。

### 手动测试步骤

1. 启动前端服务：`cd frontend && npm run dev`
2. 打开权限管理页面
3. 选择任意角色
4. 勾选某个一级菜单下的所有子菜单
5. 取消勾选其中一个子菜单
6. 点击"保存权限"
7. 刷新页面，重新查看该角色的权限

**预期结果：**
- ✅ 一级菜单仍然存在
- ✅ 只有被取消的子菜单不见了
- ✅ 其他子菜单正常显示

## 其他考虑的方案

### 方案1：使用 checkStrictly 模式（未采用）

```typescript
<Tree
  checkable
  checkStrictly  // 父子节点完全独立
  checkedKeys={{ checked: checkedKeys, halfChecked: [] }}
  onCheck={(checked: any) => {
    const allCheckedKeys = [
      ...(checked.checked || []),
      ...(checked.halfChecked || [])
    ]
    setCheckedKeys(allCheckedKeys)
  }}
/>
```

**缺点：**
- 用户体验不好，需要手动勾选每个父节点
- 违反了树形选择的常规交互习惯

### 方案2：后端自动补全父节点（未采用）

在后端 `set_role_routes` 接口中自动查找并添加父节点。

**缺点：**
- 增加后端复杂度
- 前端和后端的数据不一致，难以调试
- 违反了"前端负责交互，后端负责存储"的原则

### 方案3：当前方案（已采用）✅

在前端保存时自动添加父节点。

**优点：**
- 用户体验好，保持树形选择的常规交互
- 前端和后端数据一致
- 逻辑清晰，易于维护和调试

## 相关文件

- `frontend/src/views/User/PermissionManage.tsx` - 权限管理页面（主要）✅ 已修复
- `frontend/src/views/User/PermissionManageWorking.tsx` - 权限管理页面（备用）✅ 已修复
- `frontend/tests/test-permission-tree.html` - 测试页面
- `backend/app/apis/v1/user/role.py` - 角色权限API

## 修复的文件

### 1. PermissionManage.tsx（主要页面）

这是当前使用的权限管理页面，包含完整的UI和功能。

**修改内容：**
- 新增 `getAllParentKeys()` 函数
- 修改 `handleSave()` 函数，保存时自动添加父节点

### 2. PermissionManageWorking.tsx（备用页面）

这是一个简化版本的权限管理页面，也存在同样的问题。

**修改内容：**
- 新增 `getAllParentKeys()` 函数
- 修改 `handleSave()` 函数，保存时自动添加父节点

## 总结

这个问题是由于 Ant Design Tree 组件的默认行为导致的。通过在保存时自动添加父节点ID，我们保持了良好的用户体验，同时确保了数据的完整性。

修复后，用户可以自由地勾选/取消勾选任意节点，系统会自动维护正确的树形结构。
