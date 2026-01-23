# 树形选择快速指南

## 问题
Ant Design Tree 组件的 `checkedKeys` 如果包含父节点，会导致所有子节点都被选中。

## 解决方案
**只在 `checkedKeys` 中放入叶子节点，让Tree组件自动计算父节点的半选状态。**

## 实现步骤

### 1. 后端API返回格式

```python
@app.get("/{id}/routes")
async def get_role_routes(id: UUID):
    # 获取所有路由
    routes = await role.routes.all()
    
    # 构建树结构
    tree = build_tree(routes)
    
    # 找出叶子节点
    def find_leaf_nodes(node_list):
        leaf_ids = []
        for node in node_list:
            if 'children' in node and node['children']:
                leaf_ids.extend(find_leaf_nodes(node['children']))
            else:
                leaf_ids.append(node['id'])
        return leaf_ids
    
    checked_keys = find_leaf_nodes(tree)
    
    # 返回两个字段
    return {
        'tree': tree,           # 完整树结构
        'checked_keys': checked_keys  # 只有叶子节点
    }
```

### 2. 前端使用

```typescript
// 加载数据
const response = await getRoleRoutes(roleId)

// 只设置叶子节点为选中
setCheckedKeys(response.checked_keys)

// Tree组件
<Tree
  checkable
  checkedKeys={checkedKeys}  // 只包含叶子节点
  onCheck={(checked) => setCheckedKeys(checked as string[])}
  treeData={routeTree}
/>
```

### 3. 保存数据

```typescript
// 保存时，Tree的checkedKeys包含所有选中的节点
// 后端会自动补全父节点
await setRoleRoutes(roleId, checkedKeys)
```

## 关键点

1. **叶子节点定义**: 没有子节点的节点
2. **后端职责**: 
   - 保存时自动补全父节点
   - 查询时只返回叶子节点在 checked_keys 中
3. **前端职责**:
   - 只设置叶子节点为选中
   - 让Tree组件自动处理父节点状态
4. **Tree组件行为**:
   - 自动计算父节点的半选状态
   - 不需要手动设置 indeterminate

## 示例

### 数据结构
```
用户管理 (parent)
├── 用户列表 (child1) ✓
├── 角色管理 (child2) ✓
└── 权限管理 (child3) ✗
```

### 保存
```json
// 前端发送（用户选中的）
["child1", "child2"]

// 后端保存（自动补全）
["parent", "child1", "child2"]
```

### 查询
```json
// 后端返回
{
  "tree": [
    {
      "id": "parent",
      "children": [
        { "id": "child1" },
        { "id": "child2" },
        { "id": "child3" }
      ]
    }
  ],
  "checked_keys": ["child1", "child2"]  // 只有叶子节点
}
```

### 显示
```
☑ 用户管理 (半选，由Tree自动计算)
  ✓ 用户列表
  ✓ 角色管理
  ✗ 权限管理
```

## 常见错误

### ❌ 错误1: 返回所有节点ID
```python
# 错误
return [str(route.id) for route in routes]
```
**问题**: 包含父节点，导致所有子节点都被选中

### ❌ 错误2: 手动设置父节点状态
```typescript
// 错误
const halfCheckedKeys = calculateHalfChecked(...)
<Tree halfCheckedKeys={halfCheckedKeys} />
```
**问题**: Tree组件会自动计算，不需要手动设置

### ✅ 正确做法
```python
# 后端：只返回叶子节点
return {
    'tree': tree,
    'checked_keys': leaf_node_ids
}
```

```typescript
// 前端：只设置叶子节点
setCheckedKeys(response.checked_keys)
```

## 适用场景

这个方案适用于所有需要树形选择的场景：
- 权限管理
- 菜单管理
- 组织架构
- 分类管理
- 等等

## 参考文档

- [详细修复文档](./RBAC_TREE_SELECTION_FIX.md)
- [修复总结](./TREE_SELECTION_FIX_SUMMARY.md)
- [验证报告](./VERIFICATION_TREE_FIX.md)

---

**记住**: 只在 `checkedKeys` 中放入叶子节点！
