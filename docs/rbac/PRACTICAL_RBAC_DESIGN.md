# 实用的 RBAC 设计方案

## 设计原则

**核心思想：保持简单，逐步优化**

1. **保留现有表结构**：不做大的数据库变更
2. **优化业务逻辑**：只修改代码逻辑
3. **清晰的职责划分**：菜单显示 vs 权限控制
4. **向后兼容**：不影响现有功能

## 核心概念

### 路由类型的明确定义

```python
class RouteType(IntEnum):
    MENU = 1      # 菜单（用于显示）
    BUTTON = 2    # 按钮（功能权限）
    API = 3       # 接口（API权限）
```

### 关键规则

1. **菜单（MENU）**
   - `parent_id = None` 的是一级菜单（分组）
   - `parent_id != None` 的是二级菜单（页面）
   - 用于前端显示，不直接控制权限

2. **按钮（BUTTON）**
   - 页面内的操作按钮
   - 必须有 `permission` 字段
   - 用于控制按钮显示

3. **接口（API）**
   - 后端 API 权限
   - 必须有 `api_method` 和 `api_path`
   - 用于后端权限检查

## 实现方案

### 后端：角色权限管理

**核心逻辑：**
- 保存时：保存用户选中的所有节点（包括父节点）
- 查询时：返回完整的树形结构
- 权限检查：只检查 BUTTON 和 API 类型的权限

```python
# backend/app/apis/v1/user/role.py

@app.post("/{id}/routes")
async def set_role_routes(
    id: UUID,
    route_ids: list[str],
    current_user: dict = Depends(get_current_user)
):
    """
    设置角色的路由权限
    
    策略：保存所有选中的节点（包括父节点）
    - 前端发送什么，就保存什么
    - 不做任何过滤
    """
    role = await UserRole.get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 清除现有路由关联
    await role.routes.clear()
    
    # 添加新的路由关联
    if route_ids:
        routes = await FrontendRoute.filter(id__in=route_ids).all()
        if len(routes) != len(route_ids):
            raise HTTPException(status_code=400, detail="部分路由ID无效")
        
        await role.routes.add(*routes)
    
    return BaseOut(message="权限设置成功", count=len(route_ids))


@app.get("/{id}/routes")
async def get_role_routes(
    id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    获取角色的路由权限
    
    策略：返回完整的树形结构
    """
    role = await UserRole.get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 获取角色的所有路由
    routes = await role.routes.all()
    
    # 构建树形结构
    def build_tree(parent_id=None):
        result = []
        for route in routes:
            if route.parent_id == parent_id:
                route_dict = {
                    'id': str(route.id),
                    'name': route.name,
                    'path': route.path,
                    'title': route.title,
                    'icon': route.icon,
                    'route_type': route.route_type,
                    'permission': route.permission,
                    'parent_id': str(route.parent_id) if route.parent_id else None,
                }
                children = build_tree(route.id)
                if children:
                    route_dict['children'] = children
                result.append(route_dict)
        return result
    
    return build_tree(None)
```

### 前端：权限管理页面

**核心逻辑：**
- 使用 Ant Design Tree 的默认行为
- 不做任何特殊处理
- 直接保存用户选中的节点

```typescript
// frontend/src/views/User/PermissionManage.tsx

const handleSave = async () => {
  if (!selectedRole) {
    message.warning('请先选择角色')
    return
  }

  try {
    setSaving(true)
    
    // 直接保存用户选中的节点
    // Tree 组件会自动处理父子关系
    console.log('保存的权限ID:', checkedKeys)
    
    await setRoleRoutes(selectedRole.id, checkedKeys)
    message.success('权限保存成功')
  } catch (error) {
    message.error('权限保存失败')
  } finally {
    setSaving(false)
  }
}

// 加载角色的路由权限
const loadRoleRoutes = async (roleId: string) => {
  try {
    setTreeLoading(true)
    const routes = await getRoleRoutes(roleId)
    
    // 提取所有路由ID
    const routeIds = extractRouteIds(routes)
    setCheckedKeys(routeIds)
  } catch (error) {
    message.error('加载角色权限失败')
  } finally {
    setTreeLoading(false)
  }
}

// 提取所有路由ID（包括父节点）
const extractRouteIds = (routes: Route[]): string[] => {
  const ids: string[] = []
  const extract = (routeList: Route[]) => {
    routeList.forEach((route) => {
      ids.push(route.id)
      if (route.children && route.children.length > 0) {
        extract(route.children)
      }
    })
  }
  extract(routes)
  return ids
}
```

## 关键点

### 1. Tree 组件的行为

Ant Design Tree 组件的 `checkedKeys` 行为：
- 当父节点的所有子节点都被选中时，`checkedKeys` 包含父节点
- 当父节点的部分子节点被选中时，`checkedKeys` 不包含父节点（半选状态）

### 2. 我们的处理方式

**保存时：**
```
用户选中：['服务器管理', '国家管理', '分组管理']
Tree 返回：['服务器管理', '国家管理', '分组管理']
后端保存：['服务器管理', '国家管理', '分组管理']
```

**取消一个子节点后：**
```
用户选中：['分组管理']（取消了'国家管理'）
Tree 返回：['分组管理']（父节点变成半选，不在 checkedKeys 中）
后端保存：['分组管理']
```

**查询时：**
```
数据库读取：['分组管理']
后端返回：['分组管理']（只返回实际保存的）
前端显示：Tree 组件会自动显示父节点为半选状态
```

### 3. 为什么这样设计？

**优点：**
- ✅ 简单：不需要复杂的逻辑
- ✅ 直观：用户看到什么，就保存什么
- ✅ 灵活：可以精确控制每个节点

**缺点：**
- ❌ 父节点可能丢失：如果所有子节点都被取消，父节点也会消失

**解决方案：**
- 前端在显示时，自动补全父节点（只用于显示）
- 后端在返回菜单时，自动补全父节点

## 完整实现

### 后端：获取用户菜单

```python
# backend/app/apis/v1/user/route.py

@app.get("/user/menus")
async def get_user_menus(
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户的菜单
    
    策略：
    1. 查询用户的所有路由
    2. 只返回 MENU 类型的路由
    3. 自动补全父节点（用于显示）
    """
    user = await UserInfo.get(id=current_user['user_id']).prefetch_related('roles')
    
    # 获取用户的所有路由
    all_routes = []
    for role in user.roles:
        if role.status == 1:
            role_routes = await role.routes.filter(status=1).all()
            all_routes.extend(role_routes)
    
    # 去重
    route_dict = {route.id: route for route in all_routes}
    all_routes = list(route_dict.values())
    
    # 只保留 MENU 类型的路由
    menu_routes = [r for r in all_routes if r.route_type == RouteType.MENU]
    
    # 补全父节点
    parent_ids = {r.parent_id for r in menu_routes if r.parent_id}
    if parent_ids:
        parent_routes = await FrontendRoute.filter(
            id__in=list(parent_ids),
            route_type=RouteType.MENU,
            status=1
        ).all()
        
        # 合并
        for parent in parent_routes:
            if parent.id not in route_dict:
                menu_routes.append(parent)
    
    # 构建树形结构
    def build_tree(parent_id=None):
        result = []
        for route in menu_routes:
            if route.parent_id == parent_id:
                route_dict = {
                    'id': str(route.id),
                    'name': route.name,
                    'path': route.path,
                    'title': route.title,
                    'icon': route.icon,
                    'component': route.component,
                    'redirect': route.redirect,
                    'is_hidden': route.is_hidden,
                    'is_cache': route.is_cache,
                    'is_affix': route.is_affix,
                }
                children = build_tree(route.id)
                if children:
                    route_dict['children'] = children
                result.append(route_dict)
        return sorted(result, key=lambda x: route.sort)
    
    return build_tree(None)
```

### 后端：权限检查

```python
# backend/app/utils/permission.py

async def check_user_permission(user_id: UUID, permission: str) -> bool:
    """
    检查用户是否有指定权限
    
    参数：
        user_id: 用户ID
        permission: 权限标识（如：user:create）
    
    返回：
        True: 有权限
        False: 无权限
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    
    # 检查是否是管理员
    for role in user.roles:
        if role.code == 'ADMIN':
            return True
    
    # 获取用户的所有路由
    all_routes = []
    for role in user.roles:
        if role.status == 1:
            role_routes = await role.routes.filter(status=1).all()
            all_routes.extend(role_routes)
    
    # 检查权限
    for route in all_routes:
        if route.permission == permission:
            return True
    
    return False


def require_permission(permission: str):
    """
    权限检查装饰器
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            has_perm = await check_user_permission(
                current_user['user_id'],
                permission
            )
            
            if not has_perm:
                raise HTTPException(
                    status_code=403,
                    detail=f"缺少权限: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## 使用示例

### 1. 创建路由

```python
# 一级菜单（分组）
server_menu = await FrontendRoute.create(
    name="ServerManagement",
    title="服务器管理",
    path="/server",
    icon="ServerOutlined",
    route_type=RouteType.MENU,
    parent_id=None,
    sort=3
)

# 二级菜单（页面）
country_menu = await FrontendRoute.create(
    name="CountryList",
    title="国家管理",
    path="/server/country",
    component="views/Server/Country",
    route_type=RouteType.MENU,
    parent_id=server_menu.id,
    sort=1
)

# 按钮权限
create_button = await FrontendRoute.create(
    name="CountryCreate",
    title="创建国家",
    permission="country:create",
    route_type=RouteType.BUTTON,
    parent_id=country_menu.id,
    sort=1
)

# API 权限
create_api = await FrontendRoute.create(
    name="CountryCreateAPI",
    title="创建国家API",
    permission="country:create",
    api_method="POST",
    api_path="/api/v1/server/country",
    route_type=RouteType.API,
    parent_id=country_menu.id,
    sort=1
)
```

### 2. 分配权限

```python
# 获取角色
role = await UserRole.get(code="GM")

# 分配路由
routes = await FrontendRoute.filter(
    name__in=["ServerManagement", "CountryList", "CountryCreate"]
).all()

await role.routes.add(*routes)
```

### 3. 使用权限

```python
# 后端 API
@app.post("/server/country")
@require_permission("country:create")
async def create_country(
    data: CountryCreate,
    current_user: dict = Depends(get_current_user)
):
    pass

# 前端组件
<Permission permission="country:create">
  <Button>创建国家</Button>
</Permission>
```

## 总结

这个方案：
- ✅ **简单**：不需要复杂的逻辑
- ✅ **实用**：满足实际需求
- ✅ **兼容**：不影响现有功能
- ✅ **灵活**：可以精确控制权限

**核心思想：**
- 保存时：保存用户选中的所有节点
- 查询时：返回实际保存的节点
- 显示时：Tree 组件自动处理父子关系
- 菜单时：自动补全父节点（用于显示）

这是一个**最小改动、最大效果**的方案！
