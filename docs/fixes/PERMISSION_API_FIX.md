# 权限管理API修复总结

## 修复时间
2026-01-23

## 问题描述

前端权限管理页面调用角色路由权限接口时返回404错误：
```
GET /v1/user/role/{role_id}/routes
响应: {"detail":"Not Found"}
```

## 根本原因

后端 `backend/app/apis/v1/user/role.py` 文件中缺少以下两个接口：
1. `GET /{id}/routes` - 获取角色的路由权限
2. `POST /{id}/routes` - 设置角色的路由权限

这两个接口在RBAC权限管理系统中是必需的，用于：
- 前端权限管理页面显示角色已有的权限
- 管理员配置角色的路由权限

## 修复方案

### 1. 添加获取角色路由权限接口

```python
@app.get("/{id}/routes", response_model=list, description="获取角色的路由权限", summary="获取角色的路由权限")
async def get_role_routes(
    id: UUID = Path(..., description="角色ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取角色关联的所有路由权限
    
    返回该角色可以访问的所有路由ID列表
    """
    from app.models.user import UserRole
    
    # 获取角色并预加载路由
    role = await UserRole.get_or_none(id=id).prefetch_related('routes')
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 返回路由ID列表
    route_ids = [str(route.id) for route in role.routes]
    return route_ids
```

### 2. 添加设置角色路由权限接口

```python
@app.post("/{id}/routes", response_model=BaseOut, description="设置角色的路由权限", summary="设置角色的路由权限")
async def set_role_routes(
    id: UUID = Path(..., description="角色ID"),
    route_ids: list[str] = Body(..., description="路由ID列表"),
    current_user: dict = Depends(get_current_user)
):
    """
    设置角色的路由权限
    
    - 清除角色现有的所有路由权限
    - 设置新的路由权限列表
    - 传入空列表可以清除所有权限
    """
    from app.models.user import UserRole, FrontendRoute
    
    # 获取角色
    role = await UserRole.get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 清除现有权限
    await role.routes.clear()
    
    # 如果提供了新的路由ID列表，则添加
    if route_ids:
        # 验证所有路由ID是否存在
        routes = await FrontendRoute.filter(id__in=route_ids).all()
        if len(routes) != len(route_ids):
            raise HTTPException(status_code=400, detail="部分路由ID不存在")
        
        # 添加新的路由权限
        await role.routes.add(*routes)
    
    return {"message": f"成功设置角色权限，共 {len(route_ids)} 个路由"}
```

## 测试结果

### API测试

```bash
# 1. 获取角色的路由权限
curl -X GET "http://127.0.0.1:6080/v1/user/role/{role_id}/routes" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 响应示例：
[
  "d92745cd-e1a6-4e87-a7e5-46ed297da9a5",
  "9678e888-4d83-4105-864b-df785034b862",
  "11997020-7bc1-4cbb-8336-d5618d85fee0",
  ...
]

# 2. 设置角色的路由权限
curl -X POST "http://127.0.0.1:6080/v1/user/role/{role_id}/routes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["route_id_1", "route_id_2", "route_id_3"]'

# 响应示例：
{
  "message": "成功设置角色权限，共 3 个路由",
  "count": 1
}
```

### 自动化测试

运行测试脚本：
```bash
bash scripts/test/test_permission_apis.sh
```

测试结果：
```
✓ JWT认证正常
✓ 路由树接口正常
✓ 角色列表接口正常
✓ 获取角色路由权限接口正常 (HTTP 200)
✓ 设置角色路由权限接口正常 (HTTP 200)
✓ 验证成功：权限设置立即生效
```

## 修改的文件

### 后端
```
modified:   backend/app/apis/v1/user/role.py
  + 添加 GET /{id}/routes 接口
  + 添加 POST /{id}/routes 接口
```

### 测试脚本
```
created:    scripts/test/test_permission_apis.sh
  - 完整的权限管理API测试脚本
```

### 文档
```
created:    docs/fixes/PERMISSION_API_FIX.md (本文件)
```

## 功能说明

### 获取角色路由权限
- **端点**: `GET /v1/user/role/{id}/routes`
- **功能**: 返回指定角色关联的所有路由ID列表
- **用途**: 前端权限管理页面显示角色已有的权限
- **返回**: 路由ID数组

### 设置角色路由权限
- **端点**: `POST /v1/user/role/{id}/routes`
- **功能**: 设置角色的路由权限（替换现有权限）
- **用途**: 管理员配置角色的路由权限
- **参数**: 路由ID数组
- **返回**: 成功消息

## 数据库关系

系统使用多对多关系管理角色和路由：

```
用户 (UserInfo) ←→ 角色 (UserRole) ←→ 路由 (FrontendRoute)
     多对多              多对多
```

- 一个用户可以有多个角色
- 一个角色可以有多个路由权限
- 一个路由可以分配给多个角色

## 使用场景

### 场景1：查看角色权限
```bash
# 管理员想查看"项目管理员"角色有哪些权限
GET /v1/user/role/{gm_role_id}/routes

# 返回该角色的所有路由ID
# 前端根据这些ID在路由树中勾选对应的权限
```

### 场景2：配置角色权限
```bash
# 管理员想给"技术人员"角色配置权限
# 1. 前端显示路由树，管理员勾选需要的权限
# 2. 前端收集所有勾选的路由ID
# 3. 调用接口设置权限
POST /v1/user/role/{it_role_id}/routes
Body: ["route_id_1", "route_id_2", ...]

# 权限立即生效
# 该角色的用户下次登录时会看到新的菜单
```

### 场景3：移除所有权限
```bash
# 临时禁用某个角色的所有权限
POST /v1/user/role/{role_id}/routes
Body: []

# 传入空数组会清除该角色的所有权限
```

## 相关文档

- [权限管理快速开始](../guides/PERMISSION_QUICK_START.md)
- [权限管理使用说明](../guides/PERMISSION_MANAGE_README.md)
- [RBAC实现总结](../../backend/RBAC_IMPLEMENTATION_SUMMARY.md)
- [测试脚本](../../scripts/test/test_permission_apis.sh)

## API端点总览

### 路由管理
- `GET /v1/user/route/tree` - 获取路由树（包含角色信息）
- `GET /v1/user/route` - 获取路由列表
- `GET /v1/user/route/{id}` - 获取单个路由
- `POST /v1/user/route` - 创建路由
- `PUT /v1/user/route/{id}` - 更新路由
- `DELETE /v1/user/route/{id}` - 删除路由

### 角色管理
- `GET /v1/user/role` - 获取角色列表
- `GET /v1/user/role/{id}` - 获取单个角色
- `POST /v1/user/role` - 创建角色
- `PUT /v1/user/role/{id}` - 更新角色
- `DELETE /v1/user/role/{id}` - 删除角色

### 角色权限管理（新增）
- `GET /v1/user/role/{id}/routes` ✅ - 获取角色的路由权限
- `POST /v1/user/role/{id}/routes` ✅ - 设置角色的路由权限

## 注意事项

1. **权限立即生效**: 设置角色权限后，该角色的用户需要重新登录才能看到新的菜单

2. **权限验证**: 设置权限时会验证所有路由ID是否存在，如果有无效ID会返回400错误

3. **清除权限**: 传入空数组 `[]` 可以清除角色的所有权限

4. **多对多关系**: 修改角色权限不会影响其他角色，每个角色的权限是独立的

5. **管理员权限**: 建议只允许管理员角色调用这些接口

## 后续建议

1. 添加权限变更日志，记录谁在什么时候修改了哪个角色的权限
2. 添加权限审计功能，定期检查角色权限配置
3. 实现权限模板功能，快速为新角色配置常用权限组合
4. 添加权限继承功能，子角色可以继承父角色的权限

---

**最后更新**: 2026-01-23
**状态**: ✅ 修复完成并验证
**测试**: 全部通过

