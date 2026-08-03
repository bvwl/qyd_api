"""
API依赖项
提供通用的依赖注入函数，如认证、权限验证等
"""
from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.utils.jwt_tool import JwtToken
from app.models.user import Status, UserInfo, UserStatus, UserToken
from uuid import UUID


# FastAPI Security Scheme - 这会在Swagger文档中显示锁的图标
security = HTTPBearer(
    scheme_name="JWT Bearer",
    description="JWT认证，格式: Bearer <token>",
    auto_error=False
)


def _set_request_user(request: Request, user_id: str, auth_type: str) -> None:
    """将鉴权结果传给日志中间件，避免再次查询或解析 Token。"""
    request.state.user_id = user_id
    request.state.auth_type = auth_type


async def get_current_user_or_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    api_token: Optional[str] = Header(None, alias="API-TOKEN"),
):
    """
    同时支持：
    1. JWT Token（Authorization: Bearer xxx）
    2. 用户生成的 API Token（API-TOKEN: xxx）

    API Token 必须仍存在于数据库、状态有效，且所属用户未被停用。
    """
    if credentials:
        try:
            payload = JwtToken.verify_token(credentials.credentials)
            user_id = payload.get("id")
            if not user_id:
                raise ValueError("missing user id")

            user_info = {
                "user_id": str(user_id),
                "email": payload.get("email"),
                "nickname": payload.get("email"),
                "roles": payload.get("roles", []),
            }
            _set_request_user(request, user_info["user_id"], "jwt")
            return user_info
        except Exception:
            # 同时提供 API-TOKEN 时允许回退；否则在下方统一返回 401。
            pass

    if api_token and api_token.strip():
        token_obj = await (
            UserToken.filter(token=api_token.strip(), status=Status.OK)
            .select_related("user")
            .first()
        )
        if not token_obj:
            raise HTTPException(status_code=401, detail="Invalid API Token")

        user = token_obj.user
        if not user or user.status != UserStatus.NORMAL:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        await user.fetch_related("roles")
        user_info = {
            "user_id": str(user.id),
            "email": user.email,
            "nickname": user.nickname,
            "roles": [role.code for role in user.roles],
        }
        _set_request_user(request, user_info["user_id"], "api_token")
        return user_info

    if credentials:
        raise HTTPException(status_code=401, detail="Invalid token")
    raise HTTPException(status_code=401, detail="Authentication required")


# 基础认证：验证 JWT Token 或 API Token
async def get_current_user(user_info: dict = Depends(get_current_user_or_token)):
    """获取当前登录用户信息（支持 JWT 和 API Token）"""
    return user_info


# 管理员权限验证
async def get_admin_user(user_info: dict = Depends(get_current_user_or_token)):
    """验证管理员权限"""
    try:
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
async def get_gm_user(user_info: dict = Depends(get_current_user_or_token)):
    """验证GM权限"""
    try:
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
