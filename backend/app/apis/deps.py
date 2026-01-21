"""
API依赖项
提供通用的依赖注入函数，如认证、权限验证等
"""
from fastapi import Depends, Header, HTTPException
from typing import Optional
from app.utils.jwt_tool import JwtToken
from app.models.user import UserToken
from uuid import UUID


async def get_current_user_or_token(
    authorization: Optional[str] = Header(None),
    api_token: Optional[str] = Header(None, alias="API-TOKEN")
):
    """
    支持两种认证方式：
    1. JWT Token (Authorization: Bearer xxx)
    2. API Token (API-TOKEN: xxx)
    
    优先使用 JWT，如果没有则尝试 API Token
    """
    # 1. 尝试 JWT 认证
    if authorization and authorization.startswith("Bearer "):
        try:
            token = authorization.replace("Bearer ", "")
            payload = JwtToken.verify_token(token)  # verify_token 不是 async 方法
            # JWT payload 包含: id, email, roles
            # 转换为统一格式: user_id, email, nickname
            return {
                "user_id": payload.get("id"),
                "email": payload.get("email"),
                "nickname": payload.get("email"),  # JWT中没有nickname，使用email
                "roles": payload.get("roles", [])
            }
        except Exception as e:
            # JWT 验证失败，继续尝试 API Token
            pass
    
    # 2. 尝试 API Token 认证
    if api_token:
        try:
            # 验证 API Token
            token_obj = await UserToken.filter(token=api_token, status=1).first()
            if not token_obj:
                raise HTTPException(status_code=401, detail="Invalid API Token")
            
            # 获取用户信息
            user = await token_obj.user
            if not user or user.status != 1:
                raise HTTPException(status_code=401, detail="User not found or inactive")
            
            # 返回用户信息（格式与 JWT 一致）
            return {
                "user_id": str(user.id),
                "email": user.email,
                "nickname": user.nickname,
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"API Token verification failed: {str(e)}")
    
    # 3. 两种认证都失败
    raise HTTPException(status_code=401, detail="Authentication required")


# 基础认证：验证JWT token（保持向后兼容）
async def get_current_user(user_info: dict = Depends(get_current_user_or_token)):
    """获取当前登录用户信息（支持 JWT 和 API Token）"""
    return user_info


# 管理员权限验证
async def get_admin_user(user_info: dict = Depends(get_current_user_or_token)):
    """验证管理员权限"""
    # 获取用户完整信息以检查角色
    try:
        from app.models.user import User
        user_id = UUID(user_info["user_id"])
        user = await User.filter(id=user_id).prefetch_related("roles").first()
        
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
async def get_gm_user(user_info: dict = Depends(get_current_user_or_token)):
    """验证GM权限"""
    try:
        from app.models.user import User
        user_id = UUID(user_info["user_id"])
        user = await User.filter(id=user_id).prefetch_related("roles").first()
        
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

