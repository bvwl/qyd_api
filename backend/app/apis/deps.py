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


def _get_authorization_token(authorization: Optional[str]) -> Optional[str]:
    """兼容 Authorization: Bearer/Token/ApiKey xxx 以及直接放 Token。"""
    if not authorization:
        return None

    value = authorization.strip()
    if not value:
        return None

    scheme_and_token = value.split(None, 1)
    if len(scheme_and_token) == 1:
        return scheme_and_token[0]
    if scheme_and_token[0].lower() in {"bearer", "token", "apikey", "api-key"}:
        return scheme_and_token[1].strip() or None
    return None


async def get_current_user_or_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    api_token: Optional[str] = Header(None, alias="API-TOKEN"),
):
    """
    同时支持：
    1. JWT Token（Authorization: Bearer xxx）
    2. 用户生成的 API Token（Authorization: Bearer xxx）
    3. 兼容 API-TOKEN: xxx 和 Authorization: xxx

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

    token_candidates = []
    if api_token and api_token.strip():
        token_candidates.append(api_token.strip())
    authorization_token = _get_authorization_token(authorization)
    if authorization_token and authorization_token not in token_candidates:
        token_candidates.append(authorization_token)

    token_obj = None
    for token_candidate in token_candidates:
        token_obj = await (
            UserToken.filter(token=token_candidate, status=Status.OK)
            .select_related("user")
            .first()
        )
        if token_obj:
            break

    if token_candidates:
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

    if credentials or authorization:
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
