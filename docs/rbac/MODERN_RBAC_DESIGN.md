# 现代化 RBAC 权限设计方案

## 设计理念

### 核心原则

1. **职责分离**：菜单显示 ≠ 功能权限 ≠ 数据权限
2. **简单直观**：层级清晰，易于理解和维护
3. **灵活扩展**：支持未来业务增长
4. **性能优先**：减少查询次数，支持缓存

## 数据模型设计

### 1. 菜单表（Menu）

**职责**：只负责前端菜单的显示和路由

```python
class Menu(BaseModel):
    """菜单表 - 纯粹的前端菜单配置"""
    
    # 基础信息
    code = fields.CharField(max_length=64, unique=True, description="菜单编码")
    title = fields.CharField(max_length=64, description="菜单标题")
    
    # 路由信息
    path = fields.CharField(max_length=128, description="路由路径")
    component = fields.CharField(max_length=128, null=True, description="组件路径")
    
    # 显示配置
    icon = fields.CharField(max_length=64, null=True, description="图标")
    sort = fields.IntField(default=0, description="排序")
    
    # 层级关系
    parent = fields.ForeignKeyField(
        "models.Menu",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE
    )
    
    # 菜单配置
    is_hidden = fields.BooleanField(default=False, description="是否隐藏")
    is_cache = fields.BooleanField(default=True, description="是否缓存")
    redirect = fields.CharField(max_length=128, null=True, description="重定向")
    
    # 状态
    status = fields.IntEnumField(Status, default=Status.OK)
    
    # 关联
    roles: ManyToManyRelation["Role"]
```

**特点**：
- ✅ 只关注菜单显示
- ✅ 支持无限层级（通过 parent_id）
- ✅ 不包含权限逻辑

### 2. 权限表（Permission）

**职责**：定义系统中所有的功能权限点

```python
class Permission(BaseModel):
    """权限表 - 功能权限的最小单元"""
    
    # 权限标识（唯一）
    code = fields.CharField(
        max_length=64,
        unique=True,
        description="权限编码（如：user:create）"
    )
    name = fields.CharField(max_length=64, description="权限名称")
    description = fields.CharField(max_length=255, null=True)
    
    # 权限分类
    resource = fields.CharField(
        max_length=32,
        description="资源类型（user/project/server）"
    )
    action = fields.CharField(
        max_length=32,
        description="操作类型（create/edit/delete/view/export）"
    )
    
    # 权限类型
    permission_type = fields.IntEnumField(
        PermissionType,
        default=PermissionType.FUNCTION,
        description="权限类型"
    )
    
    # API 映射（可选）
    api_method = fields.CharField(max_length=16, null=True)
    api_path = fields.CharField(max_length=255, null=True)
    
    # 状态
    status = fields.IntEnumField(Status, default=Status.OK)
    
    # 关联
    roles: ManyToManyRelation["Role"]


class PermissionType(IntEnum):
    """权限类型"""
    FUNCTION = 1  # 功能权限（按钮、操作）
    API = 2       # API 权限
    DATA = 3      # 数据权限
```

**特点**：
- ✅ 权限命名规范：`{resource}:{action}`
- ✅ 支持多种权限类型
- ✅ 可选的 API 映射

### 3. 角色表（Role）

**职责**：用户组，关联菜单和权限

```python
class Role(BaseModel):
    """角色表 - 连接用户、菜单、权限的桥梁"""
    
    # 基础信息
    code = fields.CharField(max_length=32, unique=True, description="角色编码")
    name = fields.CharField(max_length=32, description="角色名称")
    description = fields.CharField(max_length=255, null=True)
    
    # 角色级别（用于数据权限）
    level = fields.IntField(default=0, description="角色级别")
    
    # 数据权限范围
    data_scope = fields.IntEnumField(
        DataScope,
        default=DataScope.SELF,
        description="数据权限范围"
    )
    
    # 系统角色标识
    is_system = fields.BooleanField(default=False, description="系统内置角色")
    
    # 状态
    status = fields.IntEnumField(Status, default=Status.OK)
    
    # 多对多关联
    users: ManyToManyRelation["UserInfo"] = fields.ManyToManyField(
        "models.UserInfo",
        related_name="roles",
        through="user_role_rel"
    )
    
    menus: ManyToManyRelation["Menu"] = fields.ManyToManyField(
        "models.Menu",
        related_name="roles",
        through="role_menu_rel"
    )
    
    permissions: ManyToManyRelation["Permission"] = fields.ManyToManyField(
        "models.Permission",
        related_name="roles",
        through="role_permission_rel"
    )


class DataScope(IntEnum):
    """数据权限范围"""
    ALL = 1              # 全部数据
    DEPT = 2             # 本部门
    DEPT_AND_CHILD = 3   # 本部门及下级
    SELF = 4             # 仅本人
    CUSTOM = 5           # 自定义
```

**特点**：
- ✅ 同时关联菜单和权限
- ✅ 支持数据权限范围
- ✅ 角色级别用于层级控制

### 4. 用户表（UserInfo）

```python
class UserInfo(BaseModel):
    """用户表"""
    
    email = fields.CharField(max_length=128, unique=True)
    password = fields.TextField()
    nickname = fields.CharField(max_length=64)
    avatar = fields.CharField(max_length=255, null=True)
    status = fields.IntEnumField(UserStatus, default=UserStatus.NORMAL)
    
    # 反向关联
    roles: ManyToManyRelation["Role"]
```

## 关系图

```
┌─────────────┐
│   UserInfo  │
│   (用户)     │
└──────┬──────┘
       │ M:N
       │
┌──────▼──────┐
│    Role     │
│   (角色)     │
└──┬────────┬─┘
   │ M:N    │ M:N
   │        │
   │   ┌────▼────────┐
   │   │ Permission  │
   │   │  (权限)      │
   │   └─────────────┘
   │
┌──▼──────┐
│  Menu   │
│ (菜单)   │
└─────────┘
```

## 核心逻辑

### 1. 菜单显示逻辑

```python
async def get_user_menus(user_id: UUID) -> list[dict]:
    """
    获取用户的菜单树
    
    逻辑：
    1. 查询用户的所有角色
    2. 查询角色关联的所有菜单
    3. 自动补全父级菜单（用于显示完整路径）
    4. 构建树形结构
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    
    # 获取所有菜单
    menu_set = set()
    for role in user.roles:
        if role.status == Status.OK:
            menus = await role.menus.filter(status=Status.OK).all()
            menu_set.update(menus)
    
    # 补全父级菜单
    all_menus = list(menu_set)
    parent_ids = {m.parent_id for m in all_menus if m.parent_id}
    
    while parent_ids:
        parents = await Menu.filter(
            id__in=list(parent_ids),
            status=Status.OK
        ).all()
        
        new_parents = []
        for parent in parents:
            if parent not in menu_set:
                menu_set.add(parent)
                all_menus.append(parent)
                if parent.parent_id:
                    new_parents.append(parent.parent_id)
        
        parent_ids = set(new_parents)
    
    # 构建树形结构
    return build_menu_tree(all_menus)


def build_menu_tree(menus: list[Menu], parent_id=None) -> list[dict]:
    """构建菜单树"""
    result = []
    for menu in menus:
        if menu.parent_id == parent_id:
            menu_dict = {
                'id': str(menu.id),
                'code': menu.code,
                'title': menu.title,
                'path': menu.path,
                'component': menu.component,
                'icon': menu.icon,
                'is_hidden': menu.is_hidden,
                'is_cache': menu.is_cache,
                'redirect': menu.redirect,
            }
            
            children = build_menu_tree(menus, menu.id)
            if children:
                menu_dict['children'] = children
            
            result.append(menu_dict)
    
    return sorted(result, key=lambda x: menu.sort)
```

### 2. 权限检查逻辑

```python
async def check_permission(user_id: UUID, permission_code: str) -> bool:
    """
    检查用户是否有指定权限
    
    逻辑：
    1. 查询用户的所有角色
    2. 检查是否是 ADMIN（超级管理员）
    3. 查询角色关联的所有权限
    4. 检查是否包含指定权限
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    
    # 管理员拥有所有权限
    for role in user.roles:
        if role.code == 'ADMIN' and role.status == Status.OK:
            return True
    
    # 查询权限
    for role in user.roles:
        if role.status == Status.OK:
            permissions = await role.permissions.filter(
                code=permission_code,
                status=Status.OK
            ).exists()
            
            if permissions:
                return True
    
    return False


def require_permission(permission_code: str):
    """权限检查装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            has_perm = await check_permission(
                current_user['user_id'],
                permission_code
            )
            
            if not has_perm:
                raise HTTPException(
                    status_code=403,
                    detail=f"缺少权限: {permission_code}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. 数据权限过滤

```python
async def filter_by_data_scope(
    user_id: UUID,
    resource: str,
    query: QuerySet
) -> QuerySet:
    """
    根据数据权限范围过滤查询
    
    参数：
        user_id: 用户ID
        resource: 资源类型（project/user/server）
        query: 原始查询
    
    返回：
        过滤后的查询
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    
    # 获取最大的数据权限范围
    max_scope = DataScope.SELF
    for role in user.roles:
        if role.status == Status.OK:
            if role.data_scope == DataScope.ALL:
                return query  # 全部数据，不过滤
            if role.data_scope > max_scope:
                max_scope = role.data_scope
    
    # 根据范围过滤
    if max_scope == DataScope.SELF:
        # 只能看自己的数据
        return query.filter(user_id=user_id)
    
    elif max_scope == DataScope.DEPT:
        # 本部门数据（需要部门表支持）
        user_dept = await get_user_dept(user_id)
        return query.filter(dept_id=user_dept.id)
    
    elif max_scope == DataScope.DEPT_AND_CHILD:
        # 本部门及下级部门
        dept_ids = await get_dept_and_children(user_id)
        return query.filter(dept_id__in=dept_ids)
    
    elif max_scope == DataScope.CUSTOM:
        # 自定义范围
        allowed_ids = await get_custom_data_scope(user_id, resource)
        return query.filter(id__in=allowed_ids)
    
    return query.filter(user_id=user_id)
```

## API 设计

### 1. 菜单管理 API

```python
# 获取所有菜单（树形）
GET /api/v1/menu/tree

# 创建菜单
POST /api/v1/menu
{
  "code": "user-management",
  "title": "用户管理",
  "path": "/user",
  "icon": "UserOutlined",
  "parent_id": null,
  "sort": 1
}

# 更新菜单
PUT /api/v1/menu/{id}

# 删除菜单
DELETE /api/v1/menu/{id}
```

### 2. 权限管理 API

```python
# 获取所有权限（分组）
GET /api/v1/permission/grouped

# 创建权限
POST /api/v1/permission
{
  "code": "user:create",
  "name": "创建用户",
  "resource": "user",
  "action": "create",
  "permission_type": 1
}

# 批量创建权限
POST /api/v1/permission/batch
{
  "resource": "user",
  "actions": ["create", "edit", "delete", "view", "export"]
}
```

### 3. 角色管理 API

```python
# 获取角色列表
GET /api/v1/role

# 创建角色
POST /api/v1/role
{
  "code": "PROJECT_MANAGER",
  "name": "项目经理",
  "description": "管理项目相关数据",
  "level": 5,
  "data_scope": 3
}

# 设置角色菜单
POST /api/v1/role/{id}/menus
{
  "menu_ids": ["uuid1", "uuid2", "uuid3"]
}

# 设置角色权限
POST /api/v1/role/{id}/permissions
{
  "permission_ids": ["uuid1", "uuid2", "uuid3"]
}

# 获取角色的菜单
GET /api/v1/role/{id}/menus

# 获取角色的权限
GET /api/v1/role/{id}/permissions
```

### 4. 用户权限 API

```python
# 获取当前用户的菜单
GET /api/v1/user/menus

# 获取当前用户的权限列表
GET /api/v1/user/permissions

# 检查当前用户是否有某个权限
GET /api/v1/user/has-permission?code=user:create
```

## 前端集成

### 1. 权限组件

```typescript
// Permission.tsx
interface PermissionProps {
  permission: string | string[]
  children: React.ReactNode
  fallback?: React.ReactNode
}

export default function Permission({ 
  permission, 
  children, 
  fallback = null 
}: PermissionProps) {
  const { hasPermission } = usePermission()
  
  const permissions = Array.isArray(permission) ? permission : [permission]
  const hasAnyPermission = permissions.some(p => hasPermission(p))
  
  return hasAnyPermission ? <>{children}</> : <>{fallback}</>
}

// 使用
<Permission permission="user:create">
  <Button>创建用户</Button>
</Permission>

<Permission permission={["user:edit", "user:delete"]}>
  <Button>操作</Button>
</Permission>
```

### 2. 权限 Hook

```typescript
// usePermission.ts
export function usePermission() {
  const { userInfo, permissions } = useUserStore()
  
  const hasPermission = (permission: string | string[]) => {
    // 管理员拥有所有权限
    if (userInfo?.roles?.some(r => r.code === 'ADMIN')) {
      return true
    }
    
    const perms = Array.isArray(permission) ? permission : [permission]
    return perms.some(p => permissions.includes(p))
  }
  
  const hasAllPermissions = (permissions: string[]) => {
    if (userInfo?.roles?.some(r => r.code === 'ADMIN')) {
      return true
    }
    return permissions.every(p => hasPermission(p))
  }
  
  return { hasPermission, hasAllPermissions }
}
```

### 3. 路由守卫

```typescript
// ProtectedRoute.tsx
export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token, loadUserInfo } = useUserStore()
  const location = useLocation()
  
  useEffect(() => {
    if (token) {
      loadUserInfo()
    }
  }, [token])
  
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  
  return <>{children}</>
}
```

## 权限管理界面

### 1. 角色管理页面

```
┌─────────────────────────────────────────────────────┐
│  角色管理                                             │
├─────────────────────────────────────────────────────┤
│  [+ 新建角色]  [刷新]                                 │
├─────────────────────────────────────────────────────┤
│  角色列表                                             │
│  ┌───────────────────────────────────────────────┐  │
│  │ □ ADMIN      - 系统管理员  [编辑] [权限] [删除] │  │
│  │ □ GM         - 项目经理    [编辑] [权限] [删除] │  │
│  │ □ IT         - 技术人员    [编辑] [权限] [删除] │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2. 权限配置页面（双栏布局）

```
┌─────────────────────────────────────────────────────┐
│  角色权限配置 - GM (项目经理)                          │
├──────────────────┬──────────────────────────────────┤
│  菜单权限         │  功能权限                          │
│                  │                                  │
│  ☑ 用户管理      │  用户管理                          │
│    ☑ 用户列表    │  ☑ user:view    - 查看用户        │
│    ☑ 角色管理    │  ☑ user:create  - 创建用户        │
│                  │  ☑ user:edit    - 编辑用户        │
│  ☑ 项目管理      │  ☐ user:delete  - 删除用户        │
│    ☑ 项目列表    │  ☐ user:export  - 导出用户        │
│    ☑ 账号管理    │                                  │
│    ☐ 钱包管理    │  项目管理                          │
│                  │  ☑ project:view    - 查看项目     │
│  ☐ 服务器管理    │  ☑ project:create  - 创建项目     │
│    ☐ 国家管理    │  ☑ project:edit    - 编辑项目     │
│    ☐ 分组管理    │  ☐ project:delete  - 删除项目     │
│                  │                                  │
│                  │  数据权限范围                      │
│                  │  ◉ 全部数据                       │
│                  │  ○ 本部门数据                     │
│                  │  ○ 本部门及下级                   │
│                  │  ○ 仅本人数据                     │
│                  │  ○ 自定义范围                     │
│                  │                                  │
├──────────────────┴──────────────────────────────────┤
│                    [取消]  [保存]                     │
└─────────────────────────────────────────────────────┘
```

## 初始化数据

### 1. 创建菜单

```python
# 一级菜单
user_menu = await Menu.create(
    code="user-management",
    title="用户管理",
    path="/user",
    icon="UserOutlined",
    sort=1
)

# 二级菜单
user_list = await Menu.create(
    code="user-list",
    title="用户列表",
    path="/user/list",
    component="views/User/List",
    parent_id=user_menu.id,
    sort=1
)

role_list = await Menu.create(
    code="role-list",
    title="角色管理",
    path="/user/role",
    component="views/User/Role",
    parent_id=user_menu.id,
    sort=2
)
```

### 2. 创建权限

```python
# 用户相关权限
permissions = [
    ("user:view", "查看用户", "user", "view"),
    ("user:create", "创建用户", "user", "create"),
    ("user:edit", "编辑用户", "user", "edit"),
    ("user:delete", "删除用户", "user", "delete"),
    ("user:export", "导出用户", "user", "export"),
]

for code, name, resource, action in permissions:
    await Permission.create(
        code=code,
        name=name,
        resource=resource,
        action=action,
        permission_type=PermissionType.FUNCTION
    )
```

### 3. 创建角色并分配权限

```python
# 创建 ADMIN 角色
admin_role = await Role.create(
    code="ADMIN",
    name="系统管理员",
    description="拥有所有权限",
    level=100,
    data_scope=DataScope.ALL,
    is_system=True
)

# 创建 GM 角色
gm_role = await Role.create(
    code="GM",
    name="项目经理",
    description="管理项目相关数据",
    level=50,
    data_scope=DataScope.DEPT_AND_CHILD
)

# 分配菜单
menus = await Menu.filter(code__in=["user-management", "user-list"]).all()
await gm_role.menus.add(*menus)

# 分配权限
permissions = await Permission.filter(
    code__in=["user:view", "user:create", "user:edit"]
).all()
await gm_role.permissions.add(*permissions)
```

## 优势总结

### 1. 清晰的职责分离

- **菜单表**：只管显示
- **权限表**：只管功能
- **角色表**：连接两者

### 2. 灵活的权限控制

- 菜单和权限独立配置
- 支持细粒度的功能权限
- 支持数据权限范围

### 3. 易于维护

- 表结构简单清晰
- 关系明确
- 易于扩展

### 4. 性能优化

- 支持权限缓存
- 减少查询次数
- 预加载关联数据

### 5. 用户体验好

- 双栏配置界面
- 树形结构展示
- 实时权限检查

## 对比现有方案

| 特性 | 现有方案 | 新方案 |
|------|---------|--------|
| 菜单和权限 | 混在一起（FrontendRoute） | 完全分离（Menu + Permission） |
| 层级结构 | 通过 route_type 区分 | 独立的表结构 |
| 权限粒度 | 粗粒度 | 细粒度（功能权限 + 数据权限） |
| 扩展性 | 一般 | 优秀 |
| 维护性 | 一般 | 优秀 |
| 性能 | 一般 | 优秀（支持缓存） |

## 迁移建议

如果要从现有系统迁移：

1. **创建新表**：Menu, Permission, Role（新版）
2. **数据迁移**：将 FrontendRoute 数据拆分到 Menu 和 Permission
3. **代码迁移**：逐步替换权限检查逻辑
4. **测试验证**：确保功能正常
5. **清理旧表**：删除 FrontendRoute（可选）

这个设计方案是**现代化、企业级**的 RBAC 实现，适合长期维护和扩展！
