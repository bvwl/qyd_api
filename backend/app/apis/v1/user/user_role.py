"""
用户角色管理API
管理员可以为用户分配或移除角色
"""
from uuid import UUID
from typing import List

from fastapi import APIRouter, Body, HTTPException, Path, Depends
from pydantic import BaseModel, Field

from app.models.user import UserInfo, UserRole
from app.apis.deps import get_admin_user
from app.schemas.user.info import Out as UserOut

app = APIRouter()


class AssignRolesRequest(BaseModel):
    """分配角色请求"""
    role_codes: List[str] = Field(..., description="角色代码列表", example=["ADMIN", "GM"])


class RoleInfo(BaseModel):
    """角色信息"""
    id: str
    name: str
    code: str
    description: str | None = None


@app.get("/{user_id}/roles", response_model=List[RoleInfo], description="获取用户角色", summary="获取用户角色")
async def get_user_roles(
    user_id: UUID = Path(..., description="用户ID"),
    current_user: dict = Depends(get_admin_user)
):
    """
    获取指定用户的所有角色
    需要管理员权限
    """
    try:
        user = await UserInfo.get_or_none(id=user_id).prefetch_related('roles')
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        roles = []
        for role in user.roles:
            roles.append(RoleInfo(
                id=str(role.id),
                name=role.name,
                code=role.code,
                description=role.description
            ))
        
        return roles
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{user_id}/roles", response_model=UserOut, description="设置用户角色", summary="设置用户角色")
async def assign_user_roles(
    user_id: UUID = Path(..., description="用户ID"),
    item: AssignRolesRequest = Body(..., description="角色代码列表"),
    current_user: dict = Depends(get_admin_user)
):
    """
    设置用户的角色（会覆盖原有角色）
    需要管理员权限
    """
    try:
        # 获取用户
        user = await UserInfo.get_or_none(id=user_id).prefetch_related('roles')
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取要分配的角色
        roles = []
        for code in item.role_codes:
            role = await UserRole.get_or_none(code=code)
            if not role:
                raise HTTPException(status_code=400, detail=f"角色 {code} 不存在")
            roles.append(role)
        
        # 清除现有角色
        await user.roles.clear()
        
        # 添加新角色
        for role in roles:
            await user.roles.add(role)
        
        # 重新获取用户信息
        from app.crud.user.user import user_crud
        user_out = await user_crud.get(user_id)
        
        return user_out
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/{user_id}/roles/{role_code}", response_model=UserOut, description="添加用户角色", summary="添加用户角色")
async def add_user_role(
    user_id: UUID = Path(..., description="用户ID"),
    role_code: str = Path(..., description="角色代码"),
    current_user: dict = Depends(get_admin_user)
):
    """
    为用户添加一个角色（不影响其他角色）
    需要管理员权限
    """
    try:
        # 获取用户
        user = await UserInfo.get_or_none(id=user_id).prefetch_related('roles')
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取角色
        role = await UserRole.get_or_none(code=role_code)
        if not role:
            raise HTTPException(status_code=404, detail=f"角色 {role_code} 不存在")
        
        # 检查是否已有该角色
        if role in user.roles:
            raise HTTPException(status_code=400, detail="用户已拥有该角色")
        
        # 添加角色
        await user.roles.add(role)
        
        # 重新获取用户信息
        from app.crud.user.user import user_crud
        user_out = await user_crud.get(user_id)
        
        return user_out
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{user_id}/roles/{role_code}", response_model=UserOut, description="移除用户角色", summary="移除用户角色")
async def remove_user_role(
    user_id: UUID = Path(..., description="用户ID"),
    role_code: str = Path(..., description="角色代码"),
    current_user: dict = Depends(get_admin_user)
):
    """
    移除用户的一个角色
    需要管理员权限
    """
    try:
        # 获取用户
        user = await UserInfo.get_or_none(id=user_id).prefetch_related('roles')
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取角色
        role = await UserRole.get_or_none(code=role_code)
        if not role:
            raise HTTPException(status_code=404, detail=f"角色 {role_code} 不存在")
        
        # 检查是否有该角色
        if role not in user.roles:
            raise HTTPException(status_code=400, detail="用户没有该角色")
        
        # 移除角色
        await user.roles.remove(role)
        
        # 重新获取用户信息
        from app.crud.user.user import user_crud
        user_out = await user_crud.get(user_id)
        
        return user_out
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
