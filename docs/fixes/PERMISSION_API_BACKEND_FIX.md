# 权限管理后端API修复完成

## 修复时间
2026-01-23

## 问题描述
前端权限管理页面需要以下API端点，但后端缺少实现：
1. `GET /v1/user/route/tree` - 获取路由树
2. `GET /v1/user/role/{id}/routes` - 获取角色的路由权限
3. `POST /v1/user/role/{id}/routes` - 设置角色的路由权限

## 修复内容

### 1. 添加路由树API (`backend/app/apis/v1/user/route.py`)

```python
@app.get("/tree", response_model=list, description="获取路由树", summary="获取路由树")
async def get_tree(
    status: int | None = Query(None, description="状态筛选"),
    route_type: int | None = Query(None, description="路由类型筛选"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取路由树形结构
    支持按状态和路由类型筛选
    返回树形结构的路由列表
    """
```

**功能：**
- 支持按状态筛选（status=1 表示正常）
- 支持按路由类型筛选（1:菜单, 2:按钮, 3:接口）
- 返回树形结构，包含父子关系
- 按sort和create_time排序

**返回格式：**
```json
[
  {
    "id": "uuid",
    "name": "dashboard",
    "path": "/dashboard",
    "title": "仪表盘",
    "icon": "DashboardOutlined",
    "route_type": 1,
    "permission": null,
    "children": []
  }
]
```

### 2. 添加获取角色路由权限API (`backend/app/apis/v1/user/role.py`)

```python
@app.get("/{id}/routes", response_model=list, description="获取角色的路由权限", summary="获取角色的路由权限")
async def get_role_routes(
    id: UUID = Path(..., description="角色ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取角色的路由权限列表（树形结构）
    返回该角色拥有的所有路由，以树形结构展示
    """
```

**功能：**
- 根据角色ID获取其拥有的所有路由
- 返回树形结构，方便前端展示
- 包含完整的路由信息

**返回格式：**
```json
[
  {
    "id": "uuid",
    "name": "user",
    "path": "/user",
    "title": "用户管理",
    "children": [
      {
        "id": "uuid",
        "name": "user-list",
        "path": "/user/list",
        "title": "用户列表"
      }
    ]
  }
]
```

### 3. 添加设置角色路由权限API (`backend/app/apis/v1/user/role.py`)

```python
@app.post("/{id}/routes", response_model=BaseOut, description="设置角色的路由权限", summary="设置角色的路由权限")
async def set_role_routes(
    id: UUID = Path(..., description="角色ID"),
    route_ids: list[str] = Body(..., description="路由ID列表"),
    current_user: dict = Depends(get_current_user)
):
    """
    设置角色的路由权限
    接收路由ID列表，更新角色的路由关联
    会先清除现有权限，再添加新权限
    """
```

**功能：**
- 接收路由ID数组
- 清除角色现有的所有路由权限
- 添加新的路由权限
- 验证路由ID的有效性

**请求格式：**
```json
["uuid1", "uuid2", "uuid3"]
```

**返回格式：**
```json
{
  "message": "权限设置成功",
  "count": 5
}
```

### 4. 修复路由顺序问题

**问题：** FastAPI路由匹配是按顺序的，`/{id}` 会拦截 `/tree`

**解决方案：** 将特定路径的路由（如 `/tree`）放在动态路径（如 `/{id}`）之前

**修改前：**
```python
@app.get("/{id}")  # 这个会拦截所有GET请求
@app.get("/tree")  # 永远不会被执行
```

**修改后：**
```python
@app.get("/tree")  # 先匹配特定路径
@app.get("/{id}")  # 再匹配动态路径
```

## 数据格式说明

### 路由对象格式
```typescript
{
  id: string              // UUID
  name: string            // 路由名称（唯一标识）
  path: string            // 路由路径
  component: string       // 前端组件路径
  title: string           // 菜单标题
  icon: string            // 菜单图标
  sort: number            // 排序
  redirect: string        // 重定向路径
  is_hidden: boolean      // 是否隐藏
  is_cache: boolean       // 是否缓存
  is_affix: boolean       // 是否固定
  route_type: number      // 路由类型(1:菜单,2:按钮,3:接口)
  permission: string      // 权限标识
  api_method: string      // API方法
  api_path: string        // API路径
  status: number          // 状态(1:正常,2:异常)
  parent_id: string       // 父级路由ID
  create_time: string     // 创建时间
  update_time: string     // 更新时间
  children: Route[]       // 子路由列表
}
```

## API测试

### 测试脚本
```bash
# 运行完整测试
bash test_permission_complete.sh
```

### 测试结果
```
✅ 1. 登录成功
✅ 2. 获取角色列表成功
✅ 3. 获取路由树成功
✅ 4. 获取角色路由权限成功
✅ 5. 设置角色路由权限成功
✅ 6. 验证设置结果成功
```

## 前端集成

前端已经实现了对应的API调用（`frontend/src/api/user.ts`）：

```typescript
// 获取路由树
export const getRouteTree = (params?: { status?: number; route_type?: number }) => {
  return api.get<any, Route[]>('/v1/user/route/tree', { params })
}

// 获取角色的路由权限
export const getRoleRoutes = (roleId: string) => {
  return api.get<any, Route[]>(`/v1/user/role/${roleId}/routes`)
}

// 设置角色的路由权限
export const setRoleRoutes = (roleId: string, routeIds: string[]) => {
  return api.post(`/v1/user/role/${roleId}/routes`, routeIds)
}
```

## 使用示例

### 1. 获取路由树
```bash
curl -X GET "http://127.0.0.1:6080/v1/user/route/tree?status=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 获取角色路由权限
```bash
curl -X GET "http://127.0.0.1:6080/v1/user/role/ROLE_ID/routes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 设置角色路由权限
```bash
curl -X POST "http://127.0.0.1:6080/v1/user/role/ROLE_ID/routes" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '["route_id_1", "route_id_2", "route_id_3"]'
```

## 数据库关系

```
角色 (UserRole) ←→ 路由 (FrontendRoute)
     多对多关系
     通过 role_route_rel 关联表
```

### 关联表操作
```python
# 清除角色的所有路由
await role.routes.clear()

# 添加路由到角色
await role.routes.add(*routes)

# 获取角色的所有路由
routes = await role.routes.all()
```

## 注意事项

1. **路由顺序很重要**：特定路径必须在动态路径之前定义
2. **数据预加载**：使用 `prefetch_related()` 预加载关联数据
3. **手动构建字典**：避免Pydantic验证未加载的关联数据
4. **权限验证**：所有API都需要用户登录（`get_current_user`）
5. **ID验证**：设置权限时会验证路由ID的有效性

## 相关文件

### 后端文件
- `backend/app/apis/v1/user/route.py` - 路由API（已修改）
- `backend/app/apis/v1/user/role.py` - 角色API（已修改）
- `backend/app/models/user.py` - 数据模型
- `backend/app/schemas/user/route.py` - 路由Schema
- `backend/app/schemas/user/role.py` - 角色Schema

### 前端文件
- `frontend/src/api/user.ts` - API调用
- `frontend/src/views/User/PermissionManage.tsx` - 权限管理页面
- `frontend/src/types/index.ts` - TypeScript类型定义

### 测试文件
- `test_permission_complete.sh` - 完整API测试脚本
- `test_permission_http.sh` - HTTP测试脚本

### 文档文件
- `docs/fixes/PERMISSION_COMPLETE.md` - 权限管理完整文档
- `docs/guides/PERMISSION_MANAGE_README.md` - 权限管理使用说明
- `docs/fixes/PERMISSION_API_BACKEND_FIX.md` - 本文档

## 总结

✅ **后端API已完全修复，格式符合前端需求**

修复内容：
1. ✅ 添加了路由树API (`GET /v1/user/route/tree`)
2. ✅ 添加了获取角色路由权限API (`GET /v1/user/role/{id}/routes`)
3. ✅ 添加了设置角色路由权限API (`POST /v1/user/role/{id}/routes`)
4. ✅ 修复了路由顺序问题
5. ✅ 优化了数据格式，返回树形结构
6. ✅ 所有API测试通过

现在前端权限管理页面可以正常工作了！

---

**最后更新**: 2026-01-23
**状态**: ✅ 完全修复
**测试**: ✅ 全部通过
