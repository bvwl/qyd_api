# RBAC 树形选择修复完成

## 问题描述

在权限管理界面中，当用户选择部分子菜单时，出现以下问题：

1. **原始问题**：如果二级菜单有个没选，整个主菜单包括其他选择的二级菜单也会丢失
2. **第一次修复后的问题**：后端自动补全父节点后，前端把所有节点（包括父节点）都设置为选中状态，导致未选择的子菜单也被自动选中

## 根本原因

Ant Design Tree 组件的 `checkedKeys` 属性有特殊的行为：
- 如果把父节点ID放入 `checkedKeys`，Tree会认为该父节点及其所有子节点都被选中
- Tree组件会自动计算父节点的半选状态（indeterminate），不需要手动设置

之前的实现：
- 后端保存了所有节点（包括自动补全的父节点）
- 前端查询时获取所有节点，并把所有节点ID都设置为 `checkedKeys`
- 结果：Tree组件认为所有节点都被选中

## 解决方案

### 后端修改

修改 `GET /v1/user/role/{id}/routes` API，返回两个字段：

```python
{
    "tree": [...],          # 完整的路由树结构（用于显示）
    "checked_keys": [...]   # 只包含叶子节点的ID（用于Tree的checkedKeys）
}
```

**关键逻辑**：
1. 保存时：接收前端传来的所有选中节点，自动补全父节点
2. 查询时：返回完整树结构，但 `checked_keys` 只包含叶子节点
3. 叶子节点定义：没有子节点的节点

### 前端修改

修改 `frontend/src/views/User/PermissionManage.tsx`：

```typescript
// 加载角色权限时
const response = await getRoleRoutes(roleId)
// 只设置叶子节点为选中状态
setCheckedKeys(response.checked_keys)
// Tree组件会自动计算父节点的半选状态
```

## 实现细节

### 后端代码 (`backend/app/apis/v1/user/role.py`)

```python
@app.get("/{id}/routes", response_model=dict)
async def get_role_routes(id: UUID, current_user: dict = Depends(get_current_user)):
    """
    获取角色的路由权限列表
    
    返回格式：
    {
        "tree": [...],  # 完整的路由树结构
        "checked_keys": [...]  # 只包含叶子节点的ID列表
    }
    """
    # 获取角色的所有路由
    routes = await role.routes.all()
    
    # 构建树结构
    tree = build_tree(None)
    
    # 找出所有叶子节点
    def find_leaf_nodes(route_list):
        leaf_ids = []
        for route in route_list:
            if 'children' in route and route['children']:
                leaf_ids.extend(find_leaf_nodes(route['children']))
            else:
                leaf_ids.append(route['id'])
        return leaf_ids
    
    checked_keys = find_leaf_nodes(tree)
    
    return {
        'tree': tree,
        'checked_keys': checked_keys
    }
```

### 前端代码 (`frontend/src/views/User/PermissionManage.tsx`)

```typescript
const loadRoleRoutes = async (roleId: string) => {
  const response = await getRoleRoutes(roleId)
  
  if (response && response.checked_keys && Array.isArray(response.checked_keys)) {
    // 只设置叶子节点为选中状态
    // Tree组件会自动计算父节点的半选状态
    setCheckedKeys(response.checked_keys)
  }
}
```

### API类型定义 (`frontend/src/api/user.ts`)

```typescript
export const getRoleRoutes = (roleId: string) => {
  return api.get<any, { tree: Route[]; checked_keys: string[] }>(
    `/v1/user/role/${roleId}/routes`
  )
}
```

## 测试验证

### 测试场景1：选择部分子菜单

```bash
# 选择用户管理下的两个子菜单：用户列表、角色管理
curl -X POST "http://127.0.0.1:6080/v1/user/role/{role_id}/routes" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '["a541e8bf-7444-400f-91e3-38ee905ec1b6","f45c0b35-142b-410a-9484-601ea3ebc988"]'

# 响应：
{
  "message": "权限设置成功",
  "count": 3  # 2个子菜单 + 1个自动补全的父菜单
}
```

### 测试场景2：查询权限

```bash
curl "http://127.0.0.1:6080/v1/user/role/{role_id}/routes" \
  -H "Authorization: Bearer {token}"

# 响应：
{
  "tree": [
    {
      "id": "6066f561-feac-4010-a08c-145a22a8db0c",
      "title": "用户管理",
      "children": [
        {
          "id": "a541e8bf-7444-400f-91e3-38ee905ec1b6",
          "title": "用户列表"
        },
        {
          "id": "f45c0b35-142b-410a-9484-601ea3ebc988",
          "title": "角色管理"
        }
      ]
    }
  ],
  "checked_keys": [
    "a541e8bf-7444-400f-91e3-38ee905ec1b6",  # 只包含叶子节点
    "f45c0b35-142b-410a-9484-601ea3ebc988"
  ]
}
```

### 预期行为

1. **保存时**：
   - 前端传递用户选中的所有节点（包括半选的父节点）
   - 后端自动补全所有父节点
   - 保存完整的树结构

2. **查询时**：
   - 后端返回完整的树结构（tree）
   - 但 checked_keys 只包含叶子节点
   - 前端只设置叶子节点为选中

3. **显示时**：
   - Tree组件根据 checkedKeys 自动计算父节点状态
   - 如果所有子节点都选中，父节点显示为全选
   - 如果部分子节点选中，父节点显示为半选
   - 未选中的子节点保持未选中状态

## 优势

1. **数据完整性**：后端保存完整的树结构，包括父节点
2. **显示正确性**：前端只设置叶子节点，让Tree组件自动计算父节点状态
3. **用户体验**：半选状态正确显示，未选中的子菜单不会被自动选中
4. **向后兼容**：保存逻辑不变，只是查询返回格式优化

## 相关文件

### 后端
- `backend/app/apis/v1/user/role.py` - 角色路由权限API
- `backend/app/apis/v1/rbac/role.py` - RBAC v2角色菜单API（同样的逻辑）

### 前端
- `frontend/src/views/User/PermissionManage.tsx` - 权限管理界面
- `frontend/src/api/user.ts` - API调用定义

## 测试脚本

```bash
# 运行测试
bash test_tree_selection_fix.sh
```

## 总结

通过区分"保存的节点"和"选中的节点"，我们解决了树形选择的问题：
- 保存时包含所有节点（包括父节点）
- 显示时只标记叶子节点为选中
- Tree组件自动处理父节点的半选状态

这样既保证了数据完整性，又确保了用户界面的正确显示。
