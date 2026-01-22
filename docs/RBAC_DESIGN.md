# RBAC权限管理设计方案

## 📋 当前系统分析

### 前端菜单结构

```
仪表盘 (/dashboard)

用户管理 (/user)
├── 用户列表 (/user/list)
├── 角色管理 (/user/role)
├── 路由管理 (/user/route)
├── Token管理 (/user/token)
└── 操作日志 (/user/log)

项目管理 (/project)
├── 项目列表 (/project/list)
├── 项目账号 (/project/account)
└── 项目钱包 (/project/wallet)

服务器管理 (/server)
├── 国家管理 (/server/country)
├── 分组管理 (/server/group)
├── 服务器列表 (/server/list)
└── 服务器账号 (/server/account)

邮箱管理 (/mail)
├── 邮箱列表 (/mail/list)
└── Outlook授权 (/mail/outlook)

API文档 (/api-docs)
├── 用户列表 (/api-docs/user)
├── 创建用户 (/api-docs/user-create)
├── 角色列表 (/api-docs/role)
├── 项目列表 (/api-docs/project)
├── 项目账号 (/api-docs/project-account)
├── 服务器列表 (/api-docs/server)
└── 邮箱列表 (/api-docs/mail)
```

### 后端模型设计

#### 现有模型
1. **UserInfo** - 用户信息
2. **UserRole** - 角色
3. **FrontendRoute** - 前端路由/菜单
4. **UserToken** - API Token
5. **UserLog** - 操作日志

#### 关系设计
- 用户 ↔ 角色：多对多（user_role_rel）
- 角色 ↔ 路由：多对多（role_route_rel）
- 用户 ↔ 项目：多对多（user_project_rel）

## ✅ 模型设计评估

### 优点
1. ✅ **清晰的RBAC结构**：用户-角色-路由三层关系明确
2. ✅ **灵活的权限控制**：通过角色关联路由实现菜单权限
3. ✅ **支持层级菜单**：FrontendRoute支持parent_id实现树形结构
4. ✅ **完善的索引设计**：针对常用查询场景优化
5. ✅ **项目级权限**：用户可以关联特定项目

### 需要改进的地方
1. ⚠️ **缺少操作权限**：只有菜单权限，没有按钮级权限（增删改查）
2. ⚠️ **缺少数据权限**：没有明确的数据范围控制（全部/本人/部门）
3. ⚠️ **路由数据未初始化**：frontend_routes表需要初始化菜单数据

## 🎯 改进方案

### 方案1：完善现有模型（推荐）

#### 1.1 扩展FrontendRoute模型

```python
class FrontendRoute(BaseModel):
    # ... 现有字段 ...
    
    # 新增：权限标识
    permission = fields.CharField(
        max_length=128, 
        null=True, 
        description="权限标识（如：user:list, user:create）"
    )
    
    # 新增：路由类型
    route_type = fields.IntField(
        default=1,
        description="路由类型(1:菜单,2:按钮,3:接口)"
    )
    
    # 新增：请求方法（用于接口权限）
    method = fields.CharField(
        max_length=16,
        null=True,
        description="HTTP方法(GET/POST/PUT/DELETE)"
    )
```

#### 1.2 添加数据权限枚举

```python
class DataScope(IntEnum):
    ALL = 1      # 全部数据
    CUSTOM = 2   # 自定义数据（关联的项目）
    SELF = 3     # 仅本人数据
```

#### 1.3 扩展UserRole模型

```python
class UserRole(BaseModel):
    # ... 现有字段 ...
    
    # 新增：数据权限范围
    data_scope = fields.IntEnumField(
        DataScope,
        default=DataScope.SELF,
        description="数据权限范围"
    )
```

### 方案2：初始化路由数据

创建初始化脚本，将前端菜单结构同步到数据库：

```python
# backend/db/init_routes.py

ROUTES_DATA = [
    {
        "name": "dashboard",
        "path": "/dashboard",
        "title": "仪表盘",
        "icon": "DashboardOutlined",
        "component": "Dashboard",
        "permission": "dashboard:view",
        "route_type": 1,  # 菜单
        "sort": 1,
    },
    {
        "name": "user",
        "path": "/user",
        "title": "用户管理",
        "icon": "UserOutlined",
        "permission": "user:view",
        "route_type": 1,
        "sort": 2,
        "children": [
            {
                "name": "user-list",
                "path": "/user/list",
                "title": "用户列表",
                "component": "UserList",
                "permission": "user:list",
                "route_type": 1,
                "sort": 1,
            },
            {
                "name": "user-create",
                "path": "/user/create",
                "title": "创建用户",
                "permission": "user:create",
                "route_type": 2,  # 按钮
                "is_hidden": True,
            },
            # ... 更多子路由
        ]
    },
    # ... 更多路由
]
```

## 🔧 实施步骤

### 步骤1：数据库迁移

```bash
# 1. 修改模型
# backend/app/models/user.py

# 2. 生成迁移文件
aerich migrate --name "add_route_permissions"

# 3. 应用迁移
aerich upgrade
```

### 步骤2：初始化路由数据

```bash
# 运行初始化脚本
python backend/db/init_routes.py
```

### 步骤3：初始化角色权限

```python
# backend/db/init_role_permissions.py

ROLE_PERMISSIONS = {
    "ADMIN": {
        "name": "超级管理员",
        "data_scope": DataScope.ALL,
        "routes": ["*"],  # 所有路由
    },
    "GM": {
        "name": "项目管理员",
        "data_scope": DataScope.ALL,
        "routes": [
            "dashboard:view",
            "project:*",  # 项目管理所有权限
            "server:*",   # 服务器管理所有权限
            "mail:*",     # 邮箱管理所有权限
        ],
    },
    "IT": {
        "name": "技术人员",
        "data_scope": DataScope.CUSTOM,
        "routes": [
            "dashboard:view",
            "project:view",
            "project:list",
            "server:view",
            "server:list",
        ],
    },
    "MANUAL": {
        "name": "手动操作员",
        "data_scope": DataScope.CUSTOM,
        "routes": [
            "dashboard:view",
            "project:view",
            "project:list",
        ],
    },
}
```

### 步骤4：前端权限控制

#### 4.1 创建权限Hook

```typescript
// frontend/src/hooks/usePermission.ts

import { useUserStore } from '@/store/useUserStore'

export function usePermission() {
  const userInfo = useUserStore((state) => state.userInfo)
  
  const hasPermission = (permission: string): boolean => {
    if (!userInfo?.roles) return false
    
    // 超级管理员拥有所有权限
    if (userInfo.roles.some(role => role.code === 'ADMIN')) {
      return true
    }
    
    // 检查用户角色是否有该权限
    return userInfo.roles.some(role => 
      role.permissions?.includes(permission) ||
      role.permissions?.includes(permission.split(':')[0] + ':*')
    )
  }
  
  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(permission => hasPermission(permission))
  }
  
  const hasAllPermissions = (permissions: string[]): boolean => {
    return permissions.every(permission => hasPermission(permission))
  }
  
  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  }
}
```

#### 4.2 创建权限组件

```typescript
// frontend/src/components/Permission/index.tsx

import { ReactNode } from 'react'
import { usePermission } from '@/hooks/usePermission'

interface PermissionProps {
  permission: string | string[]
  children: ReactNode
  fallback?: ReactNode
}

export default function Permission({ permission, children, fallback = null }: PermissionProps) {
  const { hasPermission, hasAnyPermission } = usePermission()
  
  const hasAccess = Array.isArray(permission)
    ? hasAnyPermission(permission)
    : hasPermission(permission)
  
  return hasAccess ? <>{children}</> : <>{fallback}</>
}
```

#### 4.3 使用权限控制

```typescript
// 在组件中使用
import Permission from '@/components/Permission'

<Permission permission="user:create">
  <Button type="primary" onClick={handleCreate}>
    创建用户
  </Button>
</Permission>

<Permission permission={['user:edit', 'user:delete']}>
  <Button onClick={handleEdit}>编辑</Button>
</Permission>
```

#### 4.4 动态菜单渲染

```typescript
// frontend/src/components/Layout/index.tsx

const filterMenuByPermission = (
  menuItems: MenuProps['items'],
  hasPermission: (permission: string) => boolean
): MenuProps['items'] => {
  return menuItems?.filter(item => {
    if (!item) return false
    
    // 检查权限
    const permission = (item as any).permission
    if (permission && !hasPermission(permission)) {
      return false
    }
    
    // 递归过滤子菜单
    if ('children' in item && item.children) {
      item.children = filterMenuByPermission(item.children, hasPermission)
      // 如果子菜单全部被过滤，则隐藏父菜单
      if (item.children.length === 0) {
        return false
      }
    }
    
    return true
  })
}

// 在Layout组件中使用
const { hasPermission } = usePermission()
const filteredMenuItems = filterMenuByPermission(menuItems, hasPermission)
```

### 步骤5：后端权限验证

#### 5.1 创建权限装饰器

```python
# backend/app/utils/permissions.py

from functools import wraps
from fastapi import HTTPException, Depends
from app.core.verify import verify_jwt_token

def require_permission(permission: str):
    """
    权限验证装饰器
    
    Args:
        permission: 权限标识，如 "user:create"
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从依赖注入获取当前用户
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            # 检查权限
            has_permission = await check_user_permission(current_user.id, permission)
            if not has_permission:
                raise HTTPException(status_code=403, detail="没有权限")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def check_user_permission(user_id: str, permission: str) -> bool:
    """
    检查用户是否有指定权限
    """
    from app.models.user import UserInfo
    
    user = await UserInfo.get(id=user_id).prefetch_related('roles__routes')
    
    # 超级管理员拥有所有权限
    if any(role.code == 'ADMIN' for role in user.roles):
        return True
    
    # 检查角色关联的路由权限
    for role in user.roles:
        for route in role.routes:
            if route.permission == permission or route.permission == permission.split(':')[0] + ':*':
                return True
    
    return False
```

#### 5.2 在API中使用

```python
# backend/app/apis/v1/user/user.py

from app.utils.permissions import require_permission
from app.core.verify import get_current_user

@app.post("/", dependencies=[Depends(verify_jwt_token)])
@require_permission("user:create")
async def create_user(
    item: UserCreate,
    current_user = Depends(get_current_user)
):
    # 创建用户逻辑
    pass
```

## 📊 权限矩阵

### 角色权限对照表

| 功能模块 | 功能 | ADMIN | GM | IT | MANUAL |
|---------|------|-------|----|----|--------|
| **仪表盘** | 查看 | ✅ | ✅ | ✅ | ✅ |
| **用户管理** | 查看列表 | ✅ | ❌ | ❌ | ❌ |
| | 创建用户 | ✅ | ❌ | ❌ | ❌ |
| | 编辑用户 | ✅ | ❌ | ❌ | ❌ |
| | 删除用户 | ✅ | ❌ | ❌ | ❌ |
| | 角色管理 | ✅ | ❌ | ❌ | ❌ |
| | 路由管理 | ✅ | ❌ | ❌ | ❌ |
| **项目管理** | 查看列表 | ✅ | ✅ | ✅(关联) | ✅(关联) |
| | 创建项目 | ✅ | ✅ | ❌ | ❌ |
| | 编辑项目 | ✅ | ✅ | ❌ | ❌ |
| | 删除项目 | ✅ | ✅ | ❌ | ❌ |
| | 项目账号 | ✅ | ✅ | ✅(关联) | ✅(关联) |
| | 项目钱包 | ✅ | ✅ | ✅(关联) | ❌ |
| **服务器管理** | 查看列表 | ✅ | ✅ | ✅ | ❌ |
| | 创建服务器 | ✅ | ✅ | ❌ | ❌ |
| | 编辑服务器 | ✅ | ✅ | ❌ | ❌ |
| | 删除服务器 | ✅ | ✅ | ❌ | ❌ |
| **邮箱管理** | 查看列表 | ✅ | ✅ | ❌ | ❌ |
| | 创建邮箱 | ✅ | ✅ | ❌ | ❌ |
| | Outlook授权 | ✅ | ✅ | ❌ | ❌ |
| **API文档** | 查看 | ✅ | ✅ | ✅ | ❌ |

### 数据权限范围

| 角色 | 数据范围 | 说明 |
|------|---------|------|
| ADMIN | 全部数据 | 可以查看和操作所有数据 |
| GM | 全部数据 | 可以查看和操作所有项目数据 |
| IT | 关联项目 | 只能查看和操作分配给自己的项目 |
| MANUAL | 关联项目 | 只能查看分配给自己的项目，操作受限 |

## 🚀 实施优先级

### P0（必须）
1. ✅ 初始化路由数据到数据库
2. ✅ 实现基础的菜单权限控制
3. ✅ 前端根据角色动态显示菜单

### P1（重要）
1. ⭐ 实现按钮级权限控制
2. ⭐ 后端API权限验证
3. ⭐ 数据权限范围控制

### P2（优化）
1. 🔄 权限管理界面（可视化配置）
2. 🔄 权限缓存优化
3. 🔄 操作日志记录

## 📝 总结

### 当前模型设计评分：8/10

**优点**：
- 清晰的RBAC结构
- 支持灵活的角色权限配置
- 良好的数据库设计和索引

**改进建议**：
1. 扩展FrontendRoute模型，支持按钮和接口权限
2. 添加数据权限范围控制
3. 初始化路由数据
4. 实现前后端权限验证

**实施建议**：
- 先实现P0优先级功能，确保基础权限控制可用
- 逐步完善P1功能，提升系统安全性
- 最后优化P2功能，提升用户体验

