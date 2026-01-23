"""
API依赖项
提供通用的依赖注入函数，如认证、权限验证等
"""
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.utils.jwt_tool import JwtToken
from uuid import UUID


# FastAPI Security Scheme - 这会在Swagger文档中显示锁的图标
security = HTTPBearer(
    scheme_name="JWT Bearer",
    description="JWT认证，格式: Bearer <token>",
    auto_error=False
)


async def get_current_user_from_jwt(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    JWT Token 认证 (Authorization: Bearer xxx)
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        token = credentials.credentials
        payload = JwtToken.verify_token(token)
        
        # JWT payload 包含: id, email, roles
        return {
            "user_id": payload.get("id"),
            "email": payload.get("email"),
            "nickname": payload.get("email"),  # JWT中没有nickname，使用email
            "roles": payload.get("roles", [])
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# 基础认证：验证JWT token
async def get_current_user(user_info: dict = Depends(get_current_user_from_jwt)):
    """获取当前登录用户信息（JWT认证）"""
    return user_info


# 管理员权限验证
async def get_admin_user(user_info: dict = Depends(get_current_user_from_jwt)):
    """验证管理员权限"""
    try:
        from app.models.user import UserInfo
        user_id = UUID(user_info["user_id"])
        user = await UserInfo.filter(id=user_id).prefetch_related("roles").first()
        
        if not user:
            raise HTTPException(status_code=403, detail="User not found")
        
        # 检查是否有 ADMIN 角色
        has_admin = any(role.code == "ADMIN" for role in user.roles)
        if not has_admin:
            raise HTTPException(status_code=403, detail="Admin permission required")
        
        return user_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Permission check failed: {str(e)}")


# GM权限验证
async def get_gm_user(user_info: dict = Depends(get_current_user_from_jwt)):
    """验证GM权限"""
    try:
        from app.models.user import UserInfo
        user_id = UUID(user_info["user_id"])
        user = await UserInfo.filter(id=user_id).prefetch_related("roles").first()
        
        if not user:
            raise HTTPException(status_code=403, detail="User not found")
        
        # 检查是否有 ADMIN 或 GM 角色
        has_permission = any(role.code in ["ADMIN", "GM"] for role in user.roles)
        if not has_permission:
            raise HTTPException(status_code=403, detail="GM permission required")
        
        return user_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Permission check failed: {str(e)}")

