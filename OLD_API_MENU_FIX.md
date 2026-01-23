# 旧 API 菜单选择问题修复

## 🎯 问题

前端还在使用旧的 API 路径：
- 设置路由：`POST /v1/user/role/{id}/routes`
- 获取路由：`GET /v1/user/role/{id}/routes`

当选择部分二级菜单时，主菜单会丢失。

## ✅ 解决方案

已在旧 API 中添加了自动补全父级菜单的逻辑！

### 修改的文件

`backend/app/apis/v1/user/role.py` - `set_role_routes` 方法

### 核心逻辑

```python
# 递归查找所有父级路由
async def add_parent_routes(route_list):
    parent_ids = set()
    for route in route_list:
        if route.parent_id and str(route.parent_id) not in all_route_ids:
            parent_ids.add(str(route.parent_id))
            all_route_ids.add(str(route.parent_id))
    
    if parent_ids:
        parents = await FrontendRoute.filter(id__in=list(parent_ids)).all()
        if parents:
            await add_parent_routes(parents)

# 补全父级路由
await add_parent_routes(selected_routes)
```

## 🚀 使用方法

### 1. 重启后端

```bash
python backend/start.py
```

### 2. 前端不需要修改

前端继续使用现有的 API 调用即可：

```typescript
// 设置角色路由
await setRoleRoutes(roleId, routeIds)

// 后端会自动补全父级菜单！
```

### 3. 测试

```bash
./test_old_api_menu_fix.sh
```

## 📊 工作流程

```
前端传递：['user-list-id']
         ↓
后端接收：1个节点
         ↓
自动补全：查找父级菜单
         ↓
保存：['user-management-id', 'user-list-id']
         ↓
返回：保存成功，共2个节点
```

## 🎯 效果

- ✅ 前端不需要修改代码
- ✅ 选择部分子菜单，父菜单不会丢失
- ✅ 显示正确的半选状态
- ✅ 向后兼容

## 📝 日志输出

后端会输出详细的日志：

```
角色 GM 权限更新：
  - 前端传递了 1 个节点
  - 自动补全后保存了 2 个节点
```

## ✅ 完成

现在重启后端，问题就解决了！前端不需要任何修改。🎉
