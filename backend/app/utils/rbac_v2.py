"""
RBAC v2 权限工具类
"""
from uuid import UUID
from typing import Optional, List, Set
from functools import wraps
from fastapi import HTTPException
from tortoise.queryset import QuerySet

from app.models.rbac_v2 import (
    Menu, Permission, Role, CustomDataScope, Department,
    Status, DataScope, PermissionType
)
from app.models.user import UserInfo


# =======================
# 菜单相关
# =======================

async def get_user_menus(user_id: UUID) -> list[dict]:
    """
    获取用户的菜单树
    
    逻辑：
    1. 查询用户的所有角色
    2. 查询角色关联的所有菜单
    3. 自动补全父级菜单（用于显示完整路径）
    4. 构建树形结构
    
    参数：
        user_id: 用户ID
    
    返回：
        菜单树列表
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles_v2')
    
    # 获取所有菜单
    menu_set: Set[Menu] = set()
    for role in user.roles_v2:
        if role.status == Status.OK:
            menus = await role.menus.filter(status=Status.OK).all()
            menu_set.update(menus)
    
    # 补全父级菜单
    all_menus = list(menu_set)
    parent_ids = {m.parent_id for m in all_menus if m.parent_id}
    
    # 递归查找所有父级菜单
    while parent_ids:
        parents = await Menu.filter(
            id__in=list(parent_ids),
            status=Status.OK
        ).all()
        
        new_parent_ids = []
        for parent in parents:
            if parent not in menu_set:
                menu_set.add(parent)
                all_menus.append(parent)
                if parent.parent_id:
                    new_parent_ids.append(parent.parent_id)
        
        parent_ids = set(new_parent_ids)
    
    # 构建树形结构
    return build_menu_tree(all_menus)


def build_menu_tree(menus: List[Menu], parent_id: Optional[UUID] = None) -> list[dict]:
    """
    构建菜单树
    
    参数：
        menus: 菜单列表
        parent_id: 父级菜单ID
    
    返回：
        树形结构的菜单列表
    """
    result = []
    
    # 按 sort 排序
    sorted_menus = sorted(menus, key=lambda x: x.sort)
    
    for menu in sorted_menus:
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
                'is_affix': menu.is_affix,
                'redirect': menu.redirect,
                'sort': menu.sort,
            }
            
            # 递归构建子菜单
            children = build_menu_tree(menus, menu.id)
            if children:
                menu_dict['children'] = children
            
            result.append(menu_dict)
    
    return result


# =======================
# 权限相关
# =======================

async def get_user_permissions(user_id: UUID) -> List[str]:
    """
    获取用户的所有权限编码列表
    
    参数：
        user_id: 用户ID
    
    返回：
        权限编码列表（如：['user:view', 'user:create']）
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles_v2')
    
    # 检查是否是管理员
    for role in user.roles_v2:
        if role.code == 'ADMIN' and role.status == Status.OK:
            # 管理员拥有所有权限
            all_permissions = await Permission.filter(status=Status.OK).all()
            return [p.code for p in all_permissions]
    
    # 获取所有权限
    permission_set: Set[str] = set()
    for role in user.roles_v2:
        if role.status == Status.OK:
            permissions = await role.permissions.filter(status=Status.OK).all()
            permission_set.update(p.code for p in permissions)
    
    return list(permission_set)


async def check_permission(user_id: UUID, permission_code: str) -> bool:
    """
    检查用户是否有指定权限
    
    参数：
        user_id: 用户ID
        permission_code: 权限编码（如：user:create）
    
    返回：
        True: 有权限
        False: 无权限
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles_v2')
    
    # 检查是否是管理员
    for role in user.roles_v2:
        if role.code == 'ADMIN' and role.status == Status.OK:
            return True
    
    # 查询权限
    for role in user.roles_v2:
        if role.status == Status.OK:
            has_permission = await role.permissions.filter(
                code=permission_code,
                status=Status.OK
            ).exists()
            
            if has_permission:
                return True
    
    return False


async def check_any_permission(user_id: UUID, permission_codes: List[str]) -> bool:
    """
    检查用户是否有任意一个权限
    
    参数：
        user_id: 用户ID
        permission_codes: 权限编码列表
    
    返回：
        True: 有任意一个权限
        False: 没有任何权限
    """
    for code in permission_codes:
        if await check_permission(user_id, code):
            return True
    return False


async def check_all_permissions(user_id: UUID, permission_codes: List[str]) -> bool:
    """
    检查用户是否有所有权限
    
    参数：
        user_id: 用户ID
        permission_codes: 权限编码列表
    
    返回：
        True: 有所有权限
        False: 缺少某些权限
    """
    for code in permission_codes:
        if not await check_permission(user_id, code):
            return False
    return True


def require_permission(permission_code: str):
    """
    权限检查装饰器
    
    用法：
        @require_permission("user:create")
        async def create_user(...):
            pass
    """
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


def require_any_permission(*permission_codes: str):
    """
    任意权限检查装饰器
    
    用法：
        @require_any_permission("user:edit", "user:delete")
        async def update_user(...):
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            has_perm = await check_any_permission(
                current_user['user_id'],
                list(permission_codes)
            )
            
            if not has_perm:
                raise HTTPException(
                    status_code=403,
                    detail=f"缺少权限: {' 或 '.join(permission_codes)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(*permission_codes: str):
    """
    所有权限检查装饰器
    
    用法：
        @require_all_permissions("user:view", "user:edit")
        async def update_user(...):
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            has_perm = await check_all_permissions(
                current_user['user_id'],
                list(permission_codes)
            )
            
            if not has_perm:
                raise HTTPException(
                    status_code=403,
                    detail=f"缺少权限: {' 和 '.join(permission_codes)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =======================
# 数据权限相关
# =======================

async def get_user_data_scope(user_id: UUID, resource: str) -> DataScope:
    """
    获取用户对指定资源的数据权限范围
    
    参数：
        user_id: 用户ID
        resource: 资源类型（project/user/server）
    
    返回：
        数据权限范围
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles_v2')
    
    # 获取最大的数据权限范围
    max_scope = DataScope.SELF
    
    for role in user.roles_v2:
        if role.status == Status.OK:
            # ADMIN 拥有全部数据权限
            if role.code == 'ADMIN':
                return DataScope.ALL
            
            # 取最大的权限范围
            if role.data_scope > max_scope:
                max_scope = role.data_scope
    
    return max_scope


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
    data_scope = await get_user_data_scope(user_id, resource)
    
    # 全部数据，不过滤
    if data_scope == DataScope.ALL:
        return query
    
    # 仅本人数据
    if data_scope == DataScope.SELF:
        return query.filter(user_id=user_id)
    
    # 本部门数据
    if data_scope == DataScope.DEPT:
        user = await UserInfo.get(id=user_id).prefetch_related('department')
        if hasattr(user, 'department') and user.department:
            return query.filter(dept_id=user.department.id)
        return query.filter(user_id=user_id)
    
    # 本部门及下级部门
    if data_scope == DataScope.DEPT_AND_CHILD:
        dept_ids = await get_dept_and_children(user_id)
        if dept_ids:
            return query.filter(dept_id__in=dept_ids)
        return query.filter(user_id=user_id)
    
    # 自定义范围
    if data_scope == DataScope.CUSTOM:
        allowed_ids = await get_custom_data_scope(user_id, resource)
        if allowed_ids:
            return query.filter(id__in=allowed_ids)
        return query.filter(user_id=user_id)
    
    # 默认只能看自己的
    return query.filter(user_id=user_id)


async def get_dept_and_children(user_id: UUID) -> List[UUID]:
    """
    获取用户所在部门及所有下级部门的ID列表
    
    参数：
        user_id: 用户ID
    
    返回：
        部门ID列表
    """
    user = await UserInfo.get(id=user_id).prefetch_related('department')
    
    if not hasattr(user, 'department') or not user.department:
        return []
    
    dept_ids = [user.department.id]
    
    # 递归查找所有子部门
    async def get_children(dept_id: UUID):
        children = await Department.filter(
            parent_id=dept_id,
            status=Status.OK
        ).all()
        
        for child in children:
            dept_ids.append(child.id)
            await get_children(child.id)
    
    await get_children(user.department.id)
    
    return dept_ids


async def get_custom_data_scope(user_id: UUID, resource: str) -> List[UUID]:
    """
    获取用户的自定义数据权限范围
    
    参数：
        user_id: 用户ID
        resource: 资源类型
    
    返回：
        资源ID列表
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles_v2')
    
    resource_ids = []
    
    # 用户级别的自定义权限
    user_scopes = await CustomDataScope.filter(
        user_id=user_id,
        resource=resource
    ).all()
    resource_ids.extend([scope.resource_id for scope in user_scopes])
    
    # 角色级别的自定义权限
    for role in user.roles_v2:
        if role.status == Status.OK:
            role_scopes = await CustomDataScope.filter(
                role_id=role.id,
                resource=resource
            ).all()
            resource_ids.extend([scope.resource_id for scope in role_scopes])
    
    return list(set(resource_ids))


# =======================
# 权限分组相关
# =======================

async def get_permissions_grouped() -> dict:
    """
    获取分组的权限列表
    
    返回：
        {
            "user": [
                {"code": "user:view", "name": "查看用户"},
                {"code": "user:create", "name": "创建用户"},
            ],
            "project": [...]
        }
    """
    permissions = await Permission.filter(status=Status.OK).all()
    
    grouped = {}
    for perm in permissions:
        if perm.resource not in grouped:
            grouped[perm.resource] = []
        
        grouped[perm.resource].append({
            'id': str(perm.id),
            'code': perm.code,
            'name': perm.name,
            'description': perm.description,
            'action': perm.action,
            'permission_type': perm.permission_type,
        })
    
    return grouped


# =======================
# 批量创建权限
# =======================

async def create_permissions_batch(
    resource: str,
    actions: List[str],
    group: Optional[str] = None
) -> List[Permission]:
    """
    批量创建权限
    
    参数：
        resource: 资源类型（如：user）
        actions: 操作列表（如：['view', 'create', 'edit', 'delete']）
        group: 权限分组
    
    返回：
        创建的权限列表
    """
    action_names = {
        'view': '查看',
        'create': '创建',
        'edit': '编辑',
        'delete': '删除',
        'export': '导出',
        'import': '导入',
    }
    
    resource_names = {
        'user': '用户',
        'role': '角色',
        'menu': '菜单',
        'permission': '权限',
        'project': '项目',
        'server': '服务器',
        'mail': '邮件',
    }
    
    permissions = []
    
    for action in actions:
        code = f"{resource}:{action}"
        name = f"{action_names.get(action, action)}{resource_names.get(resource, resource)}"
        
        # 检查是否已存在
        existing = await Permission.filter(code=code).first()
        if existing:
            permissions.append(existing)
            continue
        
        # 创建新权限
        perm = await Permission.create(
            code=code,
            name=name,
            resource=resource,
            action=action,
            permission_type=PermissionType.FUNCTION,
            group=group or resource
        )
        permissions.append(perm)
    
    return permissions
