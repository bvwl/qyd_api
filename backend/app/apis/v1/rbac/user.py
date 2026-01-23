"""
用户菜单和权限 API
"""
from fastapi import APIRouter, Depends

from app.apis.deps import get_current_user
from app.schemas.base import BaseOut
from app.utils.rbac_v2 import get_user_menus, get_user_permissions

app = APIRouter()


@app.get("/menus", summary="获取当前用户的菜单")
async def get_current_user_menus(
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户的菜单树
    
    返回：
        菜单树列表
    """
    user_id = current_user['user_id']
    menus = await get_user_menus(user_id)
    
    return BaseOut(data=menus, count=len(menus))


@app.get("/permissions", summary="获取当前用户的权限")
async def get_current_user_permissions(
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前用户的所有权限编码列表
    
    返回：
        权限编码列表（如：['user:view', 'user:create']）
    """
    user_id = current_user['user_id']
    permissions = await get_user_permissions(user_id)
    
    return BaseOut(data=permissions, count=len(permissions))


@app.get("/has-permission", summary="检查是否有指定权限")
async def check_user_permission(
    code: str,
    current_user: dict = Depends(get_current_user)
):
    """
    检查当前用户是否有指定权限
    
    参数：
        code: 权限编码（如：user:create）
    
    返回：
        has_permission: True/False
    """
    from app.utils.rbac_v2 import check_permission
    
    user_id = current_user['user_id']
    has_perm = await check_permission(user_id, code)
    
    return BaseOut(data={'has_permission': has_perm})
