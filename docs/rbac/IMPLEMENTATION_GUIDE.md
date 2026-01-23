# 企业级 RBAC 实施指南

## 实施步骤

### 第一阶段：准备工作（1天）

#### 1. 备份数据库
```bash
# 备份当前数据库
mysqldump -u qyd -p qyd > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 2. 创建新表
```bash
cd backend
python db/migrate_to_rbac.py
```

这个脚本会：
- 创建新的 `permissions`、`menus`、`roles` 表
- 创建关联表 `role_permission_rel`、`role_menu_rel`
- 迁移现有的 `frontend_routes` 数据到新表
- 迁移现有的角色数据
- 初始化默认权限

### 第二阶段：后端实现（2-3天）

#### 1. 更新模型导入

**文件：`backend/app/models/__init__.py`**

```python
# 添加新模型
from .rbac import Permission, Menu, Role, CustomDataScope
```

#### 2. 创建 RBAC API

**文件：`backend/app/apis/v1/system/permission.py`**

```python
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends
from uuid import UUID
from typing import List

from app.models.rbac import Permission, PermissionType
from app.schemas.base import BaseOut
from app.utils.rbac import require_permission
from app.core.verify import get_current_user

app = APIRouter()


@app.get("", description="获取权限列表")
@require_permission("permission:view")
async def get_permissions(
    resource: str | None = Query(None, description="资源类型"),
    permission_type: int | None = Query(None, description="权限类型"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=1000),
    current_user: dict = Depends(get_current_user)
):
    """获取权限列表"""
    query = Permission.filter(status=1)
    
    if resource:
        query = query.filter(resource=resource)
    if permission_type:
        query = query.filter(permission_type=permission_type)
    
    total = await query.count()
    permissions = await query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "items": permissions,
        "total": total,
        "page": page,
        "limit": limit
    }


@app.post("", description="创建权限")
@require_permission("permission:create")
async def create_permission(
    code: str = Body(...),
    name: str = Body(...),
    resource: str = Body(...),
    action: str = Body(...),
    description: str | None = Body(None),
    permission_type: int = Body(1),
    api_method: str | None = Body(None),
    api_path: str | None = Body(None),
    current_user: dict = Depends(get_current_user)
):
    """创建权限"""
    # 检查权限标识是否已存在
    existing = await Permission.get_or_none(code=code)
    if existing:
        raise HTTPException(status_code=400, detail="权限标识已存在")
    
    permission = await Permission.create(
        code=code,
        name=name,
        resource=resource,
        action=action,
        description=description,
        permission_type=permission_type,
        api_method=api_method,
        api_path=api_path
    )
    
    return permission


@app.get("/resources", description="获取资源列表")
@require_permission("permission:view")
async def get_resources(
    current_user: dict = Depends(get_current_user)
):
    """获取所有资源类型"""
    permissions = await Permission.all()
    resources = list(set(p.resource for p in permissions))
    return sorted(resources)


@app.get("/grouped", description="获取分组的权限列表")
@require_permission("permission:view")
async def get_grouped_permissions(
    current_user: dict = Depends(get_current_user)
):
    """按资源分组获取权限"""
    permissions = await Permission.filter(status=1).all()
    
    # 按资源分组
    grouped = {}
    for perm in permissions:
        if perm.resource not in grouped:
            grouped[perm.resource] = []
        grouped[perm.resource].append({
            "id": str(perm.id),
            "code": perm.code,
            "name": perm.name,
            "action": perm.action,
            "permission_type": perm.permission_type
        })
    
    return grouped
```

**文件：`backend/app/apis/v1/system/menu.py`**

```python
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends
from uuid import UUID
from typing import List

from app.models.rbac import Menu
from app.schemas.base import BaseOut
from app.utils.rbac import require_permission, get_user_menus
from app.core.verify import get_current_user

app = APIRouter()


@app.get("/tree", description="获取菜单树")
async def get_menu_tree(
    status: int | None = Query(None, description="状态"),
    current_user: dict = Depends(get_current_user)
):
    """获取菜单树形结构"""
    query = Menu.all()
    if status:
        query = query.filter(status=status)
    
    menus = await query.all()
    return build_tree(menus)


@app.get("/user", description="获取用户菜单")
async def get_user_menu(
    current_user: dict = Depends(get_current_user)
):
    """获取当前用户的菜单"""
    return await get_user_menus(current_user['user_id'])


@app.post("", description="创建菜单")
@require_permission("menu:create")
async def create_menu(
    name: str = Body(...),
    title: str = Body(...),
    path: str = Body(...),
    component: str | None = Body(None),
    icon: str | None = Body(None),
    parent_id: UUID | None = Body(None),
    sort: int = Body(0),
    required_permission: str | None = Body(None),
    current_user: dict = Depends(get_current_user)
):
    """创建菜单"""
    menu = await Menu.create(
        name=name,
        title=title,
        path=path,
        component=component,
        icon=icon,
        parent_id=parent_id,
        sort=sort,
        required_permission=required_permission
    )
    return menu


def build_tree(menus: List[Menu], parent_id: UUID | None = None) -> List[dict]:
    """构建树形结构"""
    result = []
    for menu in menus:
        if menu.parent_id == parent_id:
            menu_dict = {
                "id": str(menu.id),
                "name": menu.name,
                "title": menu.title,
                "path": menu.path,
                "component": menu.component,
                "icon": menu.icon,
                "sort": menu.sort,
                "required_permission": menu.required_permission,
            }
            children = build_tree(menus, menu.id)
            if children:
                menu_dict["children"] = children
            result.append(menu_dict)
    return sorted(result, key=lambda x: x["sort"])
```

**文件：`backend/app/apis/v1/system/role.py`**

```python
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends
from uuid import UUID
from typing import List

from app.models.rbac import Role, Permission, Menu
from app.schemas.base import BaseOut
from app.utils.rbac import require_permission
from app.core.verify import get_current_user

app = APIRouter()


@app.get("/{id}/permissions", description="获取角色的权限")
@require_permission("role:view")
async def get_role_permissions(
    id: UUID = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """获取角色的权限列表"""
    role = await Role.get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    permissions = await role.permissions.all()
    return [
        {
            "id": str(p.id),
            "code": p.code,
            "name": p.name,
            "resource": p.resource,
            "action": p.action
        }
        for p in permissions
    ]


@app.post("/{id}/permissions", description="设置角色的权限")
@require_permission("permission:assign")
async def set_role_permissions(
    id: UUID = Path(...),
    permission_ids: List[str] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """设置角色的权限"""
    role = await Role.get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 清除现有权限
    await role.permissions.clear()
    
    # 添加新权限
    if permission_ids:
        permissions = await Permission.filter(id__in=permission_ids).all()
        await role.permissions.add(*permissions)
    
    return BaseOut(message="权限设置成功", count=len(permission_ids))


@app.get("/{id}/menus", description="获取角色的菜单")
@require_permission("role:view")
async def get_role_menus(
    id: UUID = Path(...),
    current_user: dict = Depends(get_current_user)
):
    """获取角色的菜单列表"""
    role = await Role.get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    menus = await role.menus.all()
    return build_menu_tree(menus)


@app.post("/{id}/menus", description="设置角色的菜单")
@require_permission("permission:assign")
async def set_role_menus(
    id: UUID = Path(...),
    menu_ids: List[str] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """设置角色的菜单"""
    role = await Role.get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 清除现有菜单
    await role.menus.clear()
    
    # 添加新菜单
    if menu_ids:
        menus = await Menu.filter(id__in=menu_ids).all()
        await role.menus.add(*menus)
    
    return BaseOut(message="菜单设置成功", count=len(menu_ids))


def build_menu_tree(menus: List[Menu], parent_id: UUID | None = None) -> List[dict]:
    """构建菜单树"""
    result = []
    for menu in menus:
        if menu.parent_id == parent_id:
            menu_dict = {
                "id": str(menu.id),
                "name": menu.name,
                "title": menu.title,
                "path": menu.path,
            }
            children = build_menu_tree(menus, menu.id)
            if children:
                menu_dict["children"] = children
            result.append(menu_dict)
    return sorted(result, key=lambda x: x.get("sort", 0))
```

#### 3. 注册路由

**文件：`backend/app/apis/v1/__init__.py`**

```python
from fastapi import APIRouter
from .system import permission, menu, role

app = APIRouter()

# 系统管理
app.include_router(permission.app, prefix="/system/permission", tags=["权限管理"])
app.include_router(menu.app, prefix="/system/menu", tags=["菜单管理"])
app.include_router(role.app, prefix="/system/role", tags=["角色管理"])
```

### 第三阶段：前端实现（2-3天）

#### 1. 更新权限管理页面

**文件：`frontend/src/views/System/PermissionManage/index.tsx`**

```typescript
import { useState, useEffect } from 'react'
import { Card, Row, Col, List, Tree, Button, message, Tabs } from 'antd'
import type { DataNode } from 'antd/es/tree'

export default function PermissionManage() {
  const [roles, setRoles] = useState([])
  const [selectedRole, setSelectedRole] = useState(null)
  const [permissions, setPermissions] = useState({})
  const [menus, setMenus] = useState([])
  const [checkedPermissions, setCheckedPermissions] = useState([])
  const [checkedMenus, setCheckedMenus] = useState([])
  
  // 加载权限（按资源分组）
  const loadPermissions = async () => {
    const data = await getGroupedPermissions()
    setPermissions(data)
  }
  
  // 加载菜单树
  const loadMenus = async () => {
    const data = await getMenuTree()
    setMenus(data)
  }
  
  // 加载角色的权限
  const loadRolePermissions = async (roleId) => {
    const data = await getRolePermissions(roleId)
    setCheckedPermissions(data.map(p => p.id))
  }
  
  // 加载角色的菜单
  const loadRoleMenus = async (roleId) => {
    const data = await getRoleMenus(roleId)
    const ids = extractMenuIds(data)
    setCheckedMenus(ids)
  }
  
  // 保存权限
  const handleSavePermissions = async () => {
    await setRolePermissions(selectedRole.id, checkedPermissions)
    message.success('权限保存成功')
  }
  
  // 保存菜单
  const handleSaveMenus = async () => {
    await setRoleMenus(selectedRole.id, checkedMenus)
    message.success('菜单保存成功')
  }
  
  return (
    <Card title="权限管理">
      <Row gutter={16}>
        <Col span={6}>
          <RoleList
            roles={roles}
            selectedRole={selectedRole}
            onSelect={(role) => {
              setSelectedRole(role)
              loadRolePermissions(role.id)
              loadRoleMenus(role.id)
            }}
          />
        </Col>
        <Col span={18}>
          <Tabs>
            <Tabs.TabPane tab="权限配置" key="permissions">
              <PermissionTree
                permissions={permissions}
                checkedPermissions={checkedPermissions}
                onChange={setCheckedPermissions}
              />
              <Button onClick={handleSavePermissions}>保存权限</Button>
            </Tabs.TabPane>
            <Tabs.TabPane tab="菜单配置" key="menus">
              <Tree
                checkable
                treeData={menus}
                checkedKeys={checkedMenus}
                onCheck={setCheckedMenus}
              />
              <Button onClick={handleSaveMenus}>保存菜单</Button>
            </Tabs.TabPane>
          </Tabs>
        </Col>
      </Row>
    </Card>
  )
}
```

### 第四阶段：测试验证（1-2天）

#### 1. 单元测试

```bash
cd backend
pytest app/tests/test_rbac.py
```

#### 2. 集成测试

测试场景：
- ✅ 创建权限
- ✅ 创建菜单
- ✅ 分配权限给角色
- ✅ 分配菜单给角色
- ✅ 用户登录后获取权限和菜单
- ✅ API 权限检查
- ✅ 数据权限过滤

#### 3. 前端测试

- ✅ 权限管理页面
- ✅ 菜单管理页面
- ✅ 权限指令
- ✅ 权限组件

### 第五阶段：上线部署（1天）

#### 1. 灰度发布

```bash
# 1. 部署到测试环境
# 2. 小范围用户测试
# 3. 收集反馈
# 4. 修复问题
```

#### 2. 全量发布

```bash
# 1. 备份数据库
# 2. 部署新版本
# 3. 执行数据迁移
# 4. 验证功能
# 5. 监控日志
```

## 注意事项

### 1. 数据迁移

- ✅ 迁移前备份数据库
- ✅ 在测试环境先验证
- ✅ 保留旧表作为备份
- ✅ 迁移后验证数据完整性

### 2. 兼容性

- ✅ 保留旧的 API 接口（标记为废弃）
- ✅ 新旧系统并行运行一段时间
- ✅ 逐步迁移到新接口

### 3. 性能优化

- ✅ 添加必要的索引
- ✅ 使用缓存（Redis）
- ✅ 优化查询语句
- ✅ 监控慢查询

### 4. 安全性

- ✅ 权限检查要严格
- ✅ 数据权限要完善
- ✅ 日志记录要详细
- ✅ 定期审计权限

## 回滚方案

如果出现问题，可以快速回滚：

```bash
# 1. 停止服务
systemctl stop qyd-backend

# 2. 恢复数据库
mysql -u qyd -p qyd < backup_YYYYMMDD_HHMMSS.sql

# 3. 回滚代码
git checkout <previous-commit>

# 4. 重启服务
systemctl start qyd-backend
```

## 总结

这个企业级 RBAC 实施方案：
- ✅ 分阶段实施，风险可控
- ✅ 保留备份，可以回滚
- ✅ 充分测试，确保质量
- ✅ 文档完善，易于维护

预计总工期：**7-10天**
