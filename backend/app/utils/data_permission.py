"""
数据权限工具模块
提供统一的数据权限检查和过滤功能
"""
from typing import Optional, List
from uuid import UUID


async def get_user_data_scope(user_id: str) -> dict:
    """
    获取用户的数据权限范围
    
    Args:
        user_id: 用户ID
        
    Returns:
        dict: {
            'has_global_access': bool,  # 是否有全局访问权限
            'project_ids': List[str],   # 用户关联的项目ID列表
            'roles': List[str],          # 用户的角色列表
        }
    """
    from app.models.user import UserInfo
    
    # 获取用户及其角色和项目
    user = await UserInfo.get(id=user_id).prefetch_related('roles', 'projects')
    
    # 获取用户角色
    user_roles = [role.code for role in user.roles]
    
    # 判断是否有全局访问权限（ADMIN或GM）
    has_global_access = any(role in ['ADMIN', 'GM'] for role in user_roles)
    
    # 获取用户关联的项目ID列表
    project_ids = [str(project.id) for project in user.projects]
    
    return {
        'has_global_access': has_global_access,
        'project_ids': project_ids,
        'roles': user_roles,
    }


async def filter_by_user_projects(
    user_id: str,
    project_ids: Optional[List[str]] = None
) -> Optional[List[str]]:
    """
    根据用户权限过滤项目ID列表
    
    Args:
        user_id: 用户ID
        project_ids: 要过滤的项目ID列表（可选）
        
    Returns:
        Optional[List[str]]: 
            - None: 用户有全局访问权限，不需要过滤
            - []: 用户没有关联任何项目
            - [id1, id2]: 用户关联的项目ID列表
    """
    scope = await get_user_data_scope(user_id)
    
    # 如果有全局访问权限，不需要过滤
    if scope['has_global_access']:
        return None
    
    # 如果指定了project_ids，取交集
    if project_ids is not None:
        user_project_ids = set(scope['project_ids'])
        filtered_ids = [pid for pid in project_ids if pid in user_project_ids]
        return filtered_ids
    
    # 返回用户关联的所有项目ID
    return scope['project_ids']


def has_resource_access(user_roles: List[str], resource_type: str) -> bool:
    """
    检查用户是否有访问特定资源的权限
    
    Args:
        user_roles: 用户角色列表
        resource_type: 资源类型 ('server', 'mail', 'project', 'user')
        
    Returns:
        bool: 是否有访问权限
    """
    # 管理员有所有权限
    if 'ADMIN' in user_roles:
        return True
    
    # 根据资源类型判断权限
    resource_permissions = {
        'server': ['ADMIN', 'GM', 'IT'],      # 服务器：管理员、GM、IT
        'mail': ['ADMIN', 'GM', 'IT'],        # 邮箱：管理员、GM、IT
        'project': ['ADMIN', 'GM', 'IT', 'MANUAL'],  # 项目：所有角色（但有数据范围限制）
        'user': ['ADMIN'],                     # 用户管理：仅管理员
    }
    
    allowed_roles = resource_permissions.get(resource_type, ['ADMIN'])
    return any(role in allowed_roles for role in user_roles)
