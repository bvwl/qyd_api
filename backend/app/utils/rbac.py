"""
RBAC 权限检查工具
"""
from uuid import UUID
from typing import List, Optional, Set
from functools import wraps
from fastapi import HTTPException
from tortoise.queryset import QuerySet

from app.models.rbac import Permission, Menu, Role, DataScope, CustomDataScope
from app.models.user import UserInfo


# =======================
# 权限检查
# =======================

async def get_user_permissions(user_id: UUID) -> List[Permission]:
    """
    获取用户的所有权限
    
    流程：
    1. 查询用户的所有角色
    2. 查询角色关联的所有权限
    3. 去重并返回
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    
    permissions = []
    for role in user.roles:
        if role.status == 1:  # 只获取启用的角色
            role_permissions = await role.permissions.filter(status=1).all()
            permissions.extend(role_permissions)
    
    # 去重
    permission_dict = {p.id: p for p in permissions}
    return list(permission_dict.values())


async def get_user_permission_codes(user_id: UUID) -> Set[str]:
    """
    获取用户的所有权限标识
    
    返回：
        权限标识集合，如：{'user:create', 'user:edit', 'project:view'}
    """
    permissions = await get_user_permissions(user_id)
    return {p.code for p in permissions}


async def check_user_permission(user_id: UUID, permission_code: str) -> bool:
    """
    检查用户是否有指定权限
    
    参数：
        user_id: 用户ID
        permission_code: 权限标识，如：'user:create'
    
    返回：
        True: 有权限
        False: 无权限
    """
    # 检查是否是超级管理员
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    for role in user.roles:
        if role.code == 'ADMIN':
            return True
    
    # 检查权限
    permission_codes = await get_user_permission_codes(user_id)
    return permission_code in permission_codes


async def check_user_permissions(user_id: UUID, permission_codes: List[str], require_all: bool = True) -> bool:
    """
    检查用户是否有多个权限
    
    参数：
        user_id: 用户ID
        permission_codes: 权限标识列表
        require_all: True=需要全部权限, False=只需要任意一个权限
    
    返回：
        True: 有权限
        False: 无权限
    """
    user_permissions = await get_user_permission_codes(user_id)
    
    if require_all:
        # 需要全部权限
        return all(code in user_permissions for code in permission_codes)
    else:
        # 只需要任意一个权限
        return any(code in user_permissions for code in permission_codes)


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
            # 从参数中获取当前用户
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


def require_any_permission(*permission_codes: str):
    """
    权限检查装饰器（任意一个权限即可）
    
    使用：
        @require_any_permission("user:create", "user:edit")
        async def manage_user(...):
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="未登录")
            
            has_perm = await check_user_permissions(
                current_user['user_id'],
                list(permission_codes),
                require_all=False
            )
            
            if not has_perm:
                raise HTTPException(
                    status_code=403,
                    detail=f"缺少权限: {' 或 '.join(permission_codes)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# =======================
# 菜单权限
# =======================

async def get_user_menus(user_id: UUID) -> List[dict]:
    """
    获取用户可见的菜单
    
    流程：
    1. 查询用户的所有角色
    2. 查询角色关联的所有菜单
    3. 查询用户的所有权限
    4. 过滤需要权限的菜单（检查 required_permission）
    5. 构建树形结构
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    
    # 获取角色关联的菜单
    menus = []
    for role in user.roles:
        if role.status == 1:
            role_menus = await role.menus.filter(status=1).all()
            menus.extend(role_menus)
    
    # 去重
    menu_dict = {menu.id: menu for menu in menus}
    menus = list(menu_dict.values())
    
    # 获取用户的所有权限
    permission_codes = await get_user_permission_codes(user_id)
    
    # 过滤需要权限的菜单
    filtered_menus = []
    for menu in menus:
        if menu.required_permission:
            if menu.required_permission in permission_codes:
                filtered_menus.append(menu)
        else:
            # 没有权限要求的菜单，直接显示
            filtered_menus.append(menu)
    
    # 构建树形结构
    return build_menu_tree(filtered_menus)


def build_menu_tree(menus: List[Menu], parent_id: Optional[UUID] = None) -> List[dict]:
    """
    构建菜单树形结构
    
    参数：
        menus: 菜单列表
        parent_id: 父级菜单ID
    
    返回：
        树形结构的菜单列表
    """
    result = []
    
    for menu in menus:
        if menu.parent_id == parent_id:
            menu_dict = {
                'id': str(menu.id),
                'name': menu.name,
                'title': menu.title,
                'path': menu.path,
                'component': menu.component,
                'icon': menu.icon,
                'sort': menu.sort,
                'is_hidden': menu.is_hidden,
                'is_cache': menu.is_cache,
                'is_affix': menu.is_affix,
                'redirect': menu.redirect,
                'required_permission': menu.required_permission,
            }
            
            # 递归查找子菜单
            children = build_menu_tree(menus, menu.id)
            if children:
                menu_dict['children'] = children
            
            result.append(menu_dict)
    
    # 按 sort 排序
    result.sort(key=lambda x: x['sort'])
    return result


# =======================
# 数据权限
# =======================

async def get_user_data_scope(user_id: UUID) -> DataScope:
    """
    获取用户的数据权限范围
    
    返回用户所有角色中最大的数据范围
    """
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    
    max_scope = DataScope.SELF
    for role in user.roles:
        if role.status == 1 and role.data_scope > max_scope:
            max_scope = role.data_scope
    
    return max_scope


async def filter_by_data_scope(
    query: QuerySet,
    user_id: UUID,
    resource: str,
    creator_field: str = 'creator_id',
    dept_field: str = 'department_id'
) -> QuerySet:
    """
    根据数据权限过滤查询
    
    参数：
        query: 原始查询
        user_id: 用户ID
        resource: 资源类型（如：project, user）
        creator_field: 创建者字段名
        dept_field: 部门字段名
    
    返回：
        过滤后的查询
    """
    # 检查是否是超级管理员
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    for role in user.roles:
        if role.code == 'ADMIN':
            return query  # 超级管理员可以看到所有数据
    
    # 获取用户的数据范围
    data_scope = await get_user_data_scope(user_id)
    
    if data_scope == DataScope.ALL:
        # 全部数据，不过滤
        return query
    
    elif data_scope == DataScope.DEPT:
        # 本部门数据
        user_dept_id = getattr(user, dept_field.replace('_id', ''), None)
        if user_dept_id:
            return query.filter(**{dept_field: user_dept_id})
        else:
            # 没有部门，只能看自己的
            return query.filter(**{creator_field: user_id})
    
    elif data_scope == DataScope.DEPT_AND_CHILD:
        # 本部门及下级部门数据
        user_dept_id = getattr(user, dept_field.replace('_id', ''), None)
        if user_dept_id:
            # 获取部门及下级部门ID列表
            dept_ids = await get_dept_and_children_ids(user_dept_id)
            return query.filter(**{f'{dept_field}__in': dept_ids})
        else:
            return query.filter(**{creator_field: user_id})
    
    elif data_scope == DataScope.SELF:
        # 仅本人数据
        return query.filter(**{creator_field: user_id})
    
    elif data_scope == DataScope.CUSTOM:
        # 自定义数据范围
        custom_ids = await get_custom_data_scope_ids(user_id, resource)
        if custom_ids:
            return query.filter(id__in=custom_ids)
        else:
            # 没有自定义范围，只能看自己的
            return query.filter(**{creator_field: user_id})
    
    return query


async def get_dept_and_children_ids(dept_id: UUID) -> List[UUID]:
    """
    获取部门及其所有下级部门的ID列表
    
    TODO: 需要实现部门表和递归查询
    """
    # 这里需要根据实际的部门表结构实现
    # 暂时返回当前部门ID
    return [dept_id]


async def get_custom_data_scope_ids(user_id: UUID, resource: str) -> List[UUID]:
    """
    获取用户的自定义数据权限范围
    
    参数：
        user_id: 用户ID
        resource: 资源类型
    
    返回：
        资源ID列表
    """
    # 查询用户的自定义数据权限
    user_scopes = await CustomDataScope.filter(
        user_id=user_id,
        resource=resource
    ).all()
    
    # 查询用户角色的自定义数据权限
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    role_ids = [role.id for role in user.roles if role.status == 1]
    
    role_scopes = await CustomDataScope.filter(
        role_id__in=role_ids,
        resource=resource
    ).all()
    
    # 合并并去重
    all_scopes = user_scopes + role_scopes
    resource_ids = list(set(scope.resource_id for scope in all_scopes))
    
    return resource_ids


# =======================
# 权限组合检查
# =======================

async def check_resource_permission(
    user_id: UUID,
    resource: str,
    action: str
) -> bool:
    """
    检查用户是否有资源的操作权限
    
    参数：
        user_id: 用户ID
        resource: 资源类型（如：user, project）
        action: 操作类型（如：create, edit, delete, view）
    
    返回：
        True: 有权限
        False: 无权限
    """
    permission_code = f"{resource}:{action}"
    return await check_user_permission(user_id, permission_code)


async def check_data_access(
    user_id: UUID,
    resource_id: UUID,
    resource_type: str,
    creator_id: Optional[UUID] = None,
    dept_id: Optional[UUID] = None
) -> bool:
    """
    检查用户是否可以访问指定的数据
    
    参数：
        user_id: 用户ID
        resource_id: 资源ID
        resource_type: 资源类型
        creator_id: 资源创建者ID
        dept_id: 资源所属部门ID
    
    返回：
        True: 可以访问
        False: 不可以访问
    """
    # 检查是否是超级管理员
    user = await UserInfo.get(id=user_id).prefetch_related('roles')
    for role in user.roles:
        if role.code == 'ADMIN':
            return True
    
    # 获取用户的数据范围
    data_scope = await get_user_data_scope(user_id)
    
    if data_scope == DataScope.ALL:
        return True
    
    elif data_scope == DataScope.DEPT:
        # 检查是否同部门
        if dept_id:
            user_dept_id = getattr(user, 'department_id', None)
            return dept_id == user_dept_id
        return False
    
    elif data_scope == DataScope.DEPT_AND_CHILD:
        # 检查是否本部门或下级部门
        if dept_id:
            user_dept_id = getattr(user, 'department_id', None)
            if user_dept_id:
                dept_ids = await get_dept_and_children_ids(user_dept_id)
                return dept_id in dept_ids
        return False
    
    elif data_scope == DataScope.SELF:
        # 检查是否本人创建
        return creator_id == user_id
    
    elif data_scope == DataScope.CUSTOM:
        # 检查自定义范围
        custom_ids = await get_custom_data_scope_ids(user_id, resource_type)
        return resource_id in custom_ids
    
    return False
