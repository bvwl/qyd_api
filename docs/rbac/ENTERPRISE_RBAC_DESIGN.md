# 企业级 RBAC 权限管理系统设计

## 当前问题分析

### 现有设计的问题

1. **菜单和权限混淆**
   - 菜单（Menu）和权限（Permission）存储在同一张表
   - 父子关系用于菜单显示，也用于权限控制
   - 导致逻辑混乱，难以维护

2. **缺少权限点抽象**
   - 没有独立的权限点（Permission）概念
   - 权限直接绑定到路由，不够灵活
   - 无法支持细粒度的权限控制

3. **数据权限缺失**
   - 虽然有 `data_permission.py`，但不够系统化
   - 缺少数据范围（Data Scope）的概念
   - 无法灵活配置数据访问范围

## 标准企业级 RBAC 设计

### 核心概念

```
用户（User）
  ↓ N:M
角色（Role）
  ↓ N:M
权限（Permission）
  ↓ 1:N
资源（Resource）+ 操作（Action）
```

### 五张核心表

```
1. users                    - 用户表
2. roles                    - 角色表
3. permissions              - 权限表
4. user_role_rel            - 用户-角色关联表
5. role_permission_rel      - 角色-权限关联表
```

### 三张辅助表

```
6. menus                    - 菜单表（独立）
7. role_menu_rel            - 角色-菜单关联表
8. data_scopes              - 数据范围表
```

## 详细设计

### 1. 权限表（permissions）

```python
class Permission(BaseModel):
    """
    权限表 - 最细粒度的权限点
    
    权限命名规范：{resource}:{action}
    例如：user:create, user:edit, user:delete, user:view
    """
    code = fields.CharField(max_length=64, unique=True, description="权限标识")
    name = fields.CharField(max_length=64, description="权限名称")
    resource = fields.CharField(max_length=32, description="资源类型")
    action = fields.CharField(max_length=32, description="操作类型")
    description = fields.CharField(max_length=255, null=True, description="权限描述")
    
    # 权限类型
    permission_type = fields.IntEnumField(
        PermissionType,
        default=PermissionType.API,
        description="权限类型(1:API,2:按钮,3:数据)"
    )
    
    # API 权限相关
    api_method = fields.CharField(max_length=16, null=True, description="HTTP方法")
    api_path = fields.CharField(max_length=255, null=True, description="API路径")
    
    # 数据权限相关
    data_scope = fields.IntEnumField(
        DataScope,
        null=True,
        description="数据范围(1:全部,2:本部门,3:本部门及下级,4:仅本人,5:自定义)"
    )
    
    status = fields.IntEnumField(Status, default=Status.OK, description="状态")
    
    class Meta:
        table = "permissions"
        table_description = "权限表"
```

### 2. 菜单表（menus）- 独立

```python
class Menu(BaseModel):
    """
    菜单表 - 只负责前端菜单显示
    与权限完全分离
    """
    name = fields.CharField(max_length=64, description="菜单名称")
    title = fields.CharField(max_length=64, description="菜单标题")
    path = fields.CharField(max_length=128, description="路由路径")
    component = fields.CharField(max_length=128, null=True, description="组件路径")
    icon = fields.CharField(max_length=64, null=True, description="图标")
    
    # 层级关系
    parent = fields.ForeignKeyField(
        "models.Menu",
        related_name="children",
        null=True,
        on_delete=fields.CASCADE
    )
    sort = fields.IntField(default=0, description="排序")
    
    # 菜单配置
    is_hidden = fields.BooleanField(default=False, description="是否隐藏")
    is_cache = fields.BooleanField(default=True, description="是否缓存")
    is_affix = fields.BooleanField(default=False, description="是否固定")
    redirect = fields.CharField(max_length=128, null=True, description="重定向")
    
    # 关联权限（可选）
    # 如果设置了，则需要有对应权限才能看到菜单
    required_permission = fields.CharField(
        max_length=64,
        null=True,
        description="所需权限标识"
    )
    
    status = fields.IntEnumField(Status, default=Status.OK, description="状态")
    
    class Meta:
        table = "menus"
        table_description = "菜单表"
```

### 3. 角色表（roles）- 增强

```python
class Role(BaseModel):
    """
    角色表 - 增强版
    """
    name = fields.CharField(max_length=32, description="角色名称")
    code = fields.CharField(max_length=32, unique=True, description="角色标识")
    description = fields.CharField(max_length=255, null=True, description="角色描述")
    
    # 数据权限范围
    data_scope = fields.IntEnumField(
        DataScope,
        default=DataScope.SELF,
        description="数据范围(1:全部,2:本部门,3:本部门及下级,4:仅本人,5:自定义)"
    )
    
    # 角色级别（用于数据权限判断）
    level = fields.IntField(default=0, description="角色级别")
    
    # 是否系统内置角色（不可删除）
    is_system = fields.BooleanField(default=False, description="是否系统角色")
    
    status = fields.IntEnumField(Status, default=Status.OK, description="状态")
    
    # 关联
    users: ManyToManyRelation["User"]
    permissions: ManyToManyRelation["Permission"]
    menus: ManyToManyRelation["Menu"]
    
    class Meta:
        table = "roles"
        table_description = "角色表"
```

### 4. 数据范围枚举

```python
class DataScope(IntEnum):
    """数据权限范围"""
    ALL = 1              # 全部数据
    DEPT = 2             # 本部门数据
    DEPT_AND_CHILD = 3   # 本部门及下级部门数据
    SELF = 4             # 仅本人数据
    CUSTOM = 5           # 自定义数据范围
```

### 5. 权限类型枚举

```python
class PermissionType(IntEnum):
    """权限类型"""
    API = 1      # API权限
    BUTTON = 2   # 按钮权限
    DATA = 3     # 数据权限
```

## 权限控制流程

### 1. 菜单权限

```python
# 获取用户的菜单
async def get_user_menus(user_id: UUID) -> List[Menu]:
    """
    获取用户可见的菜单
    
    流程：
    1. 查询用户的所有角色
    2. 查询角色关联的所有菜单
    3. 查询用户的所有权限
    4. 过滤需要权限的菜单（检查 required_permission）
    5. 构建树形结构
    """
    user = await User.get(id=user_id).prefetch_related('roles')
    
    # 获取角色关联的菜单
    menus = []
    for role in user.roles:
        role_menus = await role.menus.filter(status=Status.OK).all()
        menus.extend(role_menus)
    
    # 去重
    menu_dict = {menu.id: menu for menu in menus}
    menus = list(menu_dict.values())
    
    # 获取用户的所有权限
    user_permissions = await get_user_permissions(user_id)
    permission_codes = {p.code for p in user_permissions}
    
    # 过滤需要权限的菜单
    filtered_menus = []
    for menu in menus:
        if menu.required_permission:
            if menu.required_permission in permission_codes:
                filtered_menus.append(menu)
        else:
            filtered_menus.append(menu)
    
    # 构建树形结构
    return build_menu_tree(filtered_menus)
```

### 2. API 权限

```python
# 权限装饰器
def require_permission(permission_code: str):
    """
    权限检查装饰器
    
    使用：
    @require_permission("user:create")
    async def create_user(...):
        pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从请求中获取当前用户
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            # 检查权限
            has_perm = await check_user_permission(
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

# 使用示例
@app.post("/users")
@require_permission("user:create")
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    pass
```

### 3. 数据权限

```python
async def filter_by_data_scope(
    query: QuerySet,
    user_id: UUID,
    resource: str
) -> QuerySet:
    """
    根据数据权限过滤查询
    
    参数：
        query: 原始查询
        user_id: 用户ID
        resource: 资源类型（如：project, user）
    
    返回：
        过滤后的查询
    """
    user = await User.get(id=user_id).prefetch_related('roles')
    
    # 获取用户的最大数据范围
    max_scope = DataScope.SELF
    for role in user.roles:
        if role.data_scope > max_scope:
            max_scope = role.data_scope
    
    # 根据数据范围过滤
    if max_scope == DataScope.ALL:
        # 全部数据，不过滤
        return query
    
    elif max_scope == DataScope.DEPT:
        # 本部门数据
        user_dept_id = user.department_id
        return query.filter(department_id=user_dept_id)
    
    elif max_scope == DataScope.DEPT_AND_CHILD:
        # 本部门及下级部门数据
        dept_ids = await get_dept_and_children_ids(user.department_id)
        return query.filter(department_id__in=dept_ids)
    
    elif max_scope == DataScope.SELF:
        # 仅本人数据
        return query.filter(creator_id=user_id)
    
    elif max_scope == DataScope.CUSTOM:
        # 自定义数据范围
        # 查询用户的自定义数据权限
        custom_ids = await get_custom_data_scope(user_id, resource)
        return query.filter(id__in=custom_ids)
    
    return query

# 使用示例
@app.get("/projects")
async def get_projects(
    current_user: dict = Depends(get_current_user)
):
    query = Project.all()
    
    # 应用数据权限过滤
    query = await filter_by_data_scope(
        query,
        current_user['user_id'],
        'project'
    )
    
    projects = await query.all()
    return projects
```

## 数据库迁移

### 1. 创建新表

```sql
-- 权限表
CREATE TABLE permissions (
    id CHAR(36) PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(64) NOT NULL,
    resource VARCHAR(32) NOT NULL,
    action VARCHAR(32) NOT NULL,
    description VARCHAR(255),
    permission_type TINYINT DEFAULT 1,
    api_method VARCHAR(16),
    api_path VARCHAR(255),
    data_scope TINYINT,
    status TINYINT DEFAULT 1,
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL,
    INDEX idx_code (code),
    INDEX idx_resource (resource),
    INDEX idx_type (permission_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 菜单表
CREATE TABLE menus (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    title VARCHAR(64) NOT NULL,
    path VARCHAR(128) NOT NULL,
    component VARCHAR(128),
    icon VARCHAR(64),
    parent_id CHAR(36),
    sort INT DEFAULT 0,
    is_hidden BOOLEAN DEFAULT FALSE,
    is_cache BOOLEAN DEFAULT TRUE,
    is_affix BOOLEAN DEFAULT FALSE,
    redirect VARCHAR(128),
    required_permission VARCHAR(64),
    status TINYINT DEFAULT 1,
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES menus(id) ON DELETE CASCADE,
    INDEX idx_parent (parent_id),
    INDEX idx_sort (sort)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 角色-权限关联表
CREATE TABLE role_permission_rel (
    role_id CHAR(36) NOT NULL,
    permission_id CHAR(36) NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 角色-菜单关联表
CREATE TABLE role_menu_rel (
    role_id CHAR(36) NOT NULL,
    menu_id CHAR(36) NOT NULL,
    PRIMARY KEY (role_id, menu_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (menu_id) REFERENCES menus(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 2. 数据迁移脚本

```python
# backend/db/migrate_to_new_rbac.py

async def migrate_routes_to_menus_and_permissions():
    """
    将现有的 frontend_routes 迁移到新的 menus 和 permissions
    """
    from app.models.user import FrontendRoute, RouteType
    
    routes = await FrontendRoute.all()
    
    for route in routes:
        # 创建菜单
        menu = await Menu.create(
            name=route.name,
            title=route.title,
            path=route.path,
            component=route.component,
            icon=route.icon,
            parent_id=route.parent_id,
            sort=route.sort,
            is_hidden=route.is_hidden,
            is_cache=route.is_cache,
            is_affix=route.is_affix,
            redirect=route.redirect,
            status=route.status
        )
        
        # 如果有权限标识，创建权限
        if route.permission:
            # 解析权限标识：user:create -> resource=user, action=create
            parts = route.permission.split(':')
            resource = parts[0] if len(parts) > 0 else 'unknown'
            action = parts[1] if len(parts) > 1 else 'view'
            
            permission = await Permission.create(
                code=route.permission,
                name=route.title,
                resource=resource,
                action=action,
                permission_type=PermissionType.API if route.route_type == RouteType.API else PermissionType.BUTTON,
                api_method=route.api_method,
                api_path=route.api_path,
                status=route.status
            )
            
            # 菜单关联权限
            menu.required_permission = permission.code
            await menu.save()
    
    print("迁移完成！")
```

## 前端适配

### 1. 权限指令

```typescript
// src/directives/permission.ts

import { useUserStore } from '@/store/useUserStore'

export const permission = {
  mounted(el: HTMLElement, binding: any) {
    const { value } = binding
    const userStore = useUserStore()
    
    if (value) {
      const hasPermission = userStore.hasPermission(value)
      if (!hasPermission) {
        el.parentNode?.removeChild(el)
      }
    }
  }
}

// 使用
<button v-permission="'user:create'">创建用户</button>
```

### 2. 权限组件

```typescript
// src/components/Permission/index.tsx

interface PermissionProps {
  permission: string | string[]
  children: React.ReactNode
}

export default function Permission({ permission, children }: PermissionProps) {
  const { hasPermission } = usePermission()
  
  const permissions = Array.isArray(permission) ? permission : [permission]
  const hasAnyPermission = permissions.some(p => hasPermission(p))
  
  if (!hasAnyPermission) {
    return null
  }
  
  return <>{children}</>
}

// 使用
<Permission permission="user:create">
  <Button>创建用户</Button>
</Permission>
```

### 3. 权限管理页面

```typescript
// src/views/System/Permission/index.tsx

export default function PermissionManage() {
  const [roles, setRoles] = useState<Role[]>([])
  const [selectedRole, setSelectedRole] = useState<Role | null>(null)
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [checkedPermissions, setCheckedPermissions] = useState<string[]>([])
  
  // 加载权限列表（按资源分组）
  const loadPermissions = async () => {
    const data = await getPermissions()
    setPermissions(data)
  }
  
  // 加载角色的权限
  const loadRolePermissions = async (roleId: string) => {
    const data = await getRolePermissions(roleId)
    setCheckedPermissions(data.map(p => p.id))
  }
  
  // 保存权限
  const handleSave = async () => {
    await setRolePermissions(selectedRole!.id, checkedPermissions)
    message.success('保存成功')
  }
  
  return (
    <div>
      <Row gutter={16}>
        <Col span={6}>
          <RoleList
            roles={roles}
            selectedRole={selectedRole}
            onSelect={setSelectedRole}
          />
        </Col>
        <Col span={18}>
          <PermissionTree
            permissions={permissions}
            checkedPermissions={checkedPermissions}
            onChange={setCheckedPermissions}
          />
          <Button onClick={handleSave}>保存</Button>
        </Col>
      </Row>
    </div>
  )
}
```

## 优势

### 1. 清晰的职责分离
- **菜单**：只负责前端显示
- **权限**：只负责权限控制
- **角色**：连接用户和权限

### 2. 灵活的权限控制
- 支持 API 权限
- 支持按钮权限
- 支持数据权限
- 支持自定义权限

### 3. 标准的 RBAC 模型
- 符合企业级标准
- 易于理解和维护
- 支持复杂的权限场景

### 4. 细粒度的权限管理
- 权限点独立管理
- 可以灵活组合
- 支持动态权限

### 5. 完善的数据权限
- 支持多种数据范围
- 支持自定义数据权限
- 支持部门层级

## 实施步骤

1. **第一阶段：数据库迁移**
   - 创建新表
   - 迁移现有数据
   - 保留旧表（备份）

2. **第二阶段：后端重构**
   - 实现新的模型
   - 实现权限检查逻辑
   - 实现数据权限过滤
   - 更新 API

3. **第三阶段：前端适配**
   - 更新权限管理页面
   - 更新权限指令/组件
   - 更新菜单渲染逻辑

4. **第四阶段：测试验证**
   - 单元测试
   - 集成测试
   - 用户验收测试

5. **第五阶段：上线部署**
   - 灰度发布
   - 全量发布
   - 监控和优化

## 总结

这个企业级 RBAC 设计：
- ✅ 职责清晰：菜单和权限完全分离
- ✅ 灵活强大：支持多种权限类型
- ✅ 标准规范：符合企业级标准
- ✅ 易于扩展：可以轻松添加新的权限类型
- ✅ 性能优化：合理的索引和查询优化

这是一个**生产级别**的权限管理系统设计！
