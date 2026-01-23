# 权限树修复验证指南

## 问题
取消某个二级菜单时，整个一级菜单都被取消了。

## 修复内容
在 `frontend/src/views/User/PermissionManage.tsx` 中：
- 新增 `getAllParentKeys()` 函数，自动添加所有选中节点的父节点
- 修改 `handleSave()` 函数，保存时包含父节点ID

## 验证步骤

### 1. 启动服务
```bash
# 启动后端
cd backend
python start.py

# 启动前端（新终端）
cd frontend
npm run dev
```

### 2. 测试场景

#### 场景1：取消部分子菜单
1. 打开 http://localhost:5173
2. 登录系统（zhiyu / 2201101122@qq.com）
3. 进入"权限管理"页面
4. 选择"手动操作员"角色
5. 勾选"服务器管理"下的所有子菜单：
   - ✅ 国家管理
   - ✅ 分组管理
   - ✅ 服务器列表
   - ✅ 服务器账号
6. 点击"保存权限"
7. 取消勾选"国家管理"
8. 点击"保存权限"
9. 刷新页面，重新查看该角色的权限

**预期结果：**
- ✅ "服务器管理"父菜单仍然存在
- ✅ "国家管理"被取消
- ✅ 其他子菜单（分组管理、服务器列表、服务器账号）仍然存在

#### 场景2：只选择一个子菜单
1. 选择"手动操作员"角色
2. 取消所有权限
3. 只勾选"服务器管理" > "国家管理"
4. 点击"保存权限"
5. 刷新页面

**预期结果：**
- ✅ "服务器管理"父菜单存在
- ✅ "国家管理"子菜单存在
- ✅ 其他子菜单不存在

#### 场景3：多级嵌套菜单
1. 选择"手动操作员"角色
2. 勾选"用户管理" > "用户列表"
3. 点击"保存权限"
4. 刷新页面

**预期结果：**
- ✅ "用户管理"父菜单存在
- ✅ "用户列表"子菜单存在

### 3. 查看控制台日志

打开浏览器开发者工具（F12），在保存权限时查看控制台输出：

```
保存的权限ID: ["server", "server-group", "server-list", "server-account"]
```

应该能看到父节点ID（如 "server"）被自动添加。

### 4. 后端验证

使用API测试工具验证保存的数据：

```bash
# 获取角色的路由权限
curl -X GET "http://localhost:6080/api/v1/user/role/{role_id}/routes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

返回的数据应该包含完整的树形结构，包括父节点。

## 技术细节

### 修复前
```typescript
// Tree 组件的 onCheck 返回
checkedKeys = ['server-group', 'server-list', 'server-account']
// ❌ 缺少父节点 'server'

// 直接保存
await setRoleRoutes(selectedRole.id, checkedKeys)
// 结果：父节点丢失
```

### 修复后
```typescript
// Tree 组件的 onCheck 返回
checkedKeys = ['server-group', 'server-list', 'server-account']

// 自动添加父节点
const allKeysToSave = getAllParentKeys(checkedKeys, routeTree)
// allKeysToSave = ['server', 'server-group', 'server-list', 'server-account']
//                   ↑ 自动添加

// 保存完整数据
await setRoleRoutes(selectedRole.id, allKeysToSave)
// 结果：树形结构完整
```

## 相关文件
- `frontend/src/views/User/PermissionManage.tsx` - 修复的主文件
- `docs/fixes/PERMISSION_TREE_FIX.md` - 详细文档
- `frontend/tests/test-permission-tree.html` - 测试页面

## 如果问题仍然存在

1. 清除浏览器缓存
2. 重启前端服务
3. 检查控制台是否有错误
4. 查看 `getAllParentKeys` 函数的输出日志
5. 验证后端保存的数据是否正确

## 总结

这个修复确保了在使用树形选择组件时，即使只选择部分子节点，父节点也会被正确保存，从而维护了菜单的完整树形结构。
