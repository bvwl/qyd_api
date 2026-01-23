# RBAC v1 vs v2 对比

## 核心差异

### v1 设计（现有）

```
角色 <-> 路由（FrontendRoute）
- 路由包含：一级菜单、二级菜单、按钮、API
- 通过 route_type 区分类型
- 菜单和权限混在一起
```

### v2 设计（新方案）

```
角色 <-> 菜单（Menu）
角色 <-> 权限（Permission）
- 菜单和权限完全分离
- 职责清晰
- 易于维护和扩展
```

## 详细对比

| 特性 | v1 | v2 |
|------|----|----|
| **表结构** | 1个表（FrontendRoute） | 3个表（Menu + Permission + Role） |
| **职责分离** | ❌ 混在一起 | ✅ 完全分离 |
| **菜单管理** | 通过 route_type=MENU | 独立的 Menu 表 |
| **权限管理** | 通过 route_type=BUTTON/API | 独立的 Permission 表 |
| **权限粒度** | 粗粒度 | 细粒度（功能+数据） |
| **数据权限** | ❌ 不支持 | ✅ 支持多种范围 |
| **扩展性** | 一般 | 优秀 |
| **维护性** | 一般 | 优秀 |
| **性能** | 一般 | 优秀（支持缓存） |
| **学习成本** | 低 | 中 |

## 数据模型对比

### v1 模型

```python
class FrontendRoute(BaseModel):
    """前端路由/菜单配置"""
    name = fields.CharField(max_length=64)
    path = fields.CharField(max_length=128)
    title = fields.CharField(max_length=64)
    icon = fields.CharField(max_length=64, null=True)
    parent = fields.ForeignKeyField("models.FrontendRoute", null=True)
    
    # 混合了菜单和权限
    route_type = fields.IntEnumField(RouteType)  # 1:菜单,2:按钮,3:接口
    permission = fields.CharField(max_length=128, null=True)
    api_method = fields.CharField(max_length=16, null=True)
    api_path = fields.CharField(max_length=255, null=True)
    
    # 多对多
    roles: ManyToManyRelation["UserRole"]
```

**问题：**
- ❌ 菜单和权限混在一起
- ❌ 通过 route_type 区分，不够清晰
- ❌ 权限粒度粗
- ❌ 不支持数据权限

### v2 模型

```python
class Menu(BaseModel):
    """菜单表 - 只负责显示"""
    code = fields.CharField(max_length=64, unique=True)
    title = fields.CharField(max_length=64)
    path = fields.CharField(max_length=128)
    icon = fields.CharField(max_length=64, null=True)
    parent = fields.ForeignKeyField("models.Menu", null=True)
    
    # 只有菜单相关字段
    is_hidden = fields.BooleanField(default=False)
    is_cache = fields.BooleanField(default=True)
    redirect = fields.CharField(max_length=128, null=True)
    
    roles: ManyToManyRelation["Role"]


class Permission(BaseModel):
    """权限表 - 只负责权限"""
    code = fields.CharField(max_length=64, unique=True)  # user:create
    name = fields.CharField(max_length=64)
    resource = fields.CharField(max_length=32)  # user
    action = fields.CharField(max_length=32)    # create
    
    # 权限类型
    permission_type = fields.IntEnumField(PermissionType)
    
    # API 映射（可选）
    api_method = fields.CharField(max_length=16, null=True)
    api_path = fields.CharField(max_length=255, null=True)
    
    roles: ManyToManyRelation["Role"]


class Role(BaseModel):
    """角色表 - 连接菜单和权限"""
    code = fields.CharField(max_length=32, unique=True)
    name = fields.CharField(max_length=32)
    level = fields.IntField(default=0)
    
    # 数据权限范围
    data_scope = fields.IntEnumField(DataScope)
    
    # 多对多
    users: ManyToManyRelation["UserInfo"]
    menus: ManyToManyRelation["Menu"]
    permissions: ManyToManyRelation["Permission"]
```

**优点：**
- ✅ 职责清晰
- ✅ 易于理解
- ✅ 易于扩展
- ✅ 支持数据权限

## 使用对比

### v1 使用方式

```python
# 创建菜单+权限（混在一起）
route = await FrontendRoute.create(
    name="UserList",
    title="用户列表",
    path="/user/list",
    route_type=RouteType.MENU,
    parent_id=user_menu.id
)

# 创建按钮权限
button = await FrontendRoute.create(
    name="UserCreate",
    title="创建用户",
    permission="user:create",
    route_type=RouteType.BUTTON,
    parent_id=route.id
)

# 分配给角色
await role.routes.add(route, button)

# 权限检查
routes = await role.routes.filter(permission="user:create").exists()
```

### v2 使用方式

```python
# 创建菜单（只管显示）
menu = await Menu.create(
    code="user-list",
    title="用户列表",
    path="/user/list",
    parent_id=user_menu.id
)

# 创建权限（只管功能）
permission = await Permission.create(
    code="user:create",
    name="创建用户",
    resource="user",
    action="create"
)

# 分配菜单
await role.menus.add(menu)

# 分配权限
await role.permissions.add(permission)

# 权限检查
has_perm = await check_permission(user_id, "user:create")
```

**v2 更清晰：**
- ✅ 菜单是菜单
- ✅ 权限是权限
- ✅ 各司其职

## 前端集成对比

### v1 前端

```typescript
// 获取路由（菜单+权限混在一起）
const routes = await getUserRoutes()

// 过滤菜单
const menus = routes.filter(r => r.route_type === 1)

// 过滤权限
const permissions = routes
  .filter(r => r.route_type === 2)
  .map(r => r.permission)

// 权限检查
const hasPermission = permissions.includes('user:create')
```

### v2 前端

```typescript
// 获取菜单（纯粹的菜单）
const menus = await getUserMenus()

// 获取权限（纯粹的权限）
const permissions = await getUserPermissions()

// 权限检查
const hasPermission = permissions.includes('user:create')
```

**v2 更简单：**
- ✅ API 更清晰
- ✅ 不需要过滤
- ✅ 职责分明

## 权限管理界面对比

### v1 界面

```
┌─────────────────────────────────────┐
│  角色权限配置                         │
├─────────────────────────────────────┤
│  路由树（菜单+按钮+API混在一起）       │
│  ☑ 用户管理                          │
│    ☑ 用户列表                        │
│      ☑ 创建用户（按钮）               │
│      ☑ 编辑用户（按钮）               │
│      ☑ POST /api/v1/user（API）      │
│      ☑ PUT /api/v1/user/{id}（API）  │
└─────────────────────────────────────┘
```

**问题：**
- ❌ 菜单、按钮、API 混在一起
- ❌ 树形结构复杂
- ❌ 不直观

### v2 界面（双栏布局）

```
┌──────────────────┬──────────────────┐
│  菜单权限         │  功能权限         │
│                  │                  │
│  ☑ 用户管理      │  用户管理         │
│    ☑ 用户列表    │  ☑ user:view     │
│    ☑ 角色管理    │  ☑ user:create   │
│                  │  ☑ user:edit     │
│  ☑ 项目管理      │  ☐ user:delete   │
│    ☑ 项目列表    │                  │
│                  │  项目管理         │
│                  │  ☑ project:view  │
│                  │  ☑ project:create│
│                  │                  │
│                  │  数据权限范围     │
│                  │  ◉ 全部数据      │
│                  │  ○ 本部门数据    │
└──────────────────┴──────────────────┘
```

**优点：**
- ✅ 菜单和权限分开
- ✅ 一目了然
- ✅ 易于操作

## 性能对比

### v1 性能

```python
# 查询用户路由（需要过滤）
routes = await role.routes.all()  # 查询所有路由
menus = [r for r in routes if r.route_type == 1]  # 内存过滤
permissions = [r.permission for r in routes if r.route_type == 2]  # 内存过滤
```

**问题：**
- ❌ 查询所有数据
- ❌ 内存过滤
- ❌ 不支持缓存

### v2 性能

```python
# 查询用户菜单（直接查询）
menus = await role.menus.all()  # 只查询菜单

# 查询用户权限（直接查询）
permissions = await role.permissions.all()  # 只查询权限

# 支持缓存
@cache(ttl=3600)
async def get_user_permissions(user_id):
    return await get_permissions(user_id)
```

**优点：**
- ✅ 精确查询
- ✅ 减少数据量
- ✅ 支持缓存

## 数据权限对比

### v1 数据权限

```python
# 不支持数据权限
# 需要手动实现
if user.role == 'ADMIN':
    projects = await Project.all()
else:
    projects = await Project.filter(user_id=user.id)
```

**问题：**
- ❌ 不支持
- ❌ 需要手动实现
- ❌ 代码重复

### v2 数据权限

```python
# 内置数据权限支持
query = Project.all()
query = await filter_by_data_scope(user_id, 'project', query)
projects = await query

# 支持多种范围
class DataScope(IntEnum):
    ALL = 1              # 全部数据
    DEPT = 2             # 本部门
    DEPT_AND_CHILD = 3   # 本部门及下级
    SELF = 4             # 仅本人
    CUSTOM = 5           # 自定义
```

**优点：**
- ✅ 内置支持
- ✅ 统一处理
- ✅ 灵活配置

## 迁移成本

### 从 v1 迁移到 v2

**步骤：**

1. **创建新表**（不影响现有系统）
   ```bash
   python backend/db/init_rbac_v2.py
   ```

2. **数据迁移**（将 FrontendRoute 拆分）
   ```python
   # 迁移菜单
   routes = await FrontendRoute.filter(route_type=RouteType.MENU).all()
   for route in routes:
       await Menu.create(
           code=route.name,
           title=route.title,
           path=route.path,
           ...
       )
   
   # 迁移权限
   routes = await FrontendRoute.filter(route_type=RouteType.BUTTON).all()
   for route in routes:
       await Permission.create(
           code=route.permission,
           name=route.title,
           ...
       )
   ```

3. **代码迁移**（逐步替换）
   ```python
   # 旧代码
   from app.models.user import FrontendRoute
   routes = await role.routes.all()
   
   # 新代码
   from app.models.rbac_v2 import Menu, Permission
   menus = await role.menus.all()
   permissions = await role.permissions.all()
   ```

4. **测试验证**
   - 测试菜单显示
   - 测试权限检查
   - 测试数据权限

5. **清理旧表**（可选）
   ```sql
   DROP TABLE frontend_routes;
   DROP TABLE role_route_rel;
   ```

**成本评估：**
- 开发时间：2-3天
- 测试时间：1-2天
- 风险：低（新旧系统可以并存）

## 推荐方案

### 新项目

**强烈推荐 v2**
- ✅ 设计更合理
- ✅ 扩展性更好
- ✅ 维护成本低

### 现有项目

**根据情况选择：**

1. **如果权限需求简单**
   - 继续使用 v1
   - 优化现有代码

2. **如果权限需求复杂**
   - 迁移到 v2
   - 支持数据权限
   - 支持细粒度控制

3. **如果有时间重构**
   - 迁移到 v2
   - 一次性解决所有问题

## 总结

| 维度 | v1 | v2 | 推荐 |
|------|----|----|------|
| **设计合理性** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | v2 |
| **易用性** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 平手 |
| **扩展性** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | v2 |
| **维护性** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | v2 |
| **性能** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | v2 |
| **学习成本** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | v1 |
| **迁移成本** | - | ⭐⭐⭐ | - |

**结论：**
- 新项目：使用 v2
- 现有项目：根据需求决定是否迁移
- v2 是更现代化、更企业级的方案

## 快速开始

### 使用 v2

```bash
# 1. 初始化数据
python backend/db/init_rbac_v2.py

# 2. 启动服务
python backend/start.py

# 3. 登录测试
# 邮箱: zhiyu
# 密码: 2201101122@qq.com
```

### 查看文档

- [v2 设计文档](./MODERN_RBAC_DESIGN.md)
- [v2 实现指南](./IMPLEMENTATION_GUIDE_V2.md)
- [API 文档](./API_REFERENCE_V2.md)
