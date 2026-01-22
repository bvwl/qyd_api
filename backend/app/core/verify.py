from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
from app.utils.jwt_tool import JwtToken
from app.models.user import UserToken, UserInfo


class Verify:
    def __init__(self):
        pass

    # 检测是否为管理员
    def is_admin(self, roles, raise_exception=True):
        """检测是否为管理员
        
        Args:
            roles: 角色列表或单个角色字符串
            raise_exception: 是否抛出异常，默认True
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if "ADMIN" not in roles:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否操作自己的数据
    def is_owner(self, pk: UUID, user_id: UUID, raise_exception=True):
        if pk != user_id:
            if raise_exception:
                raise HTTPException(status_code=403, detail="无法操作他人数据")
            else:
                return False
        return True

    # 检测是否为GM
    def is_gm(self, roles, raise_exception=True):
        """检测是否为GM
        
        Args:
            roles: 角色列表或单个角色字符串
            raise_exception: 是否抛出异常，默认True
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if "GM" not in roles:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否为GM或自己
    def is_gm_or_owner(self, roles, pk: UUID, user_id: UUID, raise_exception=True):
        """检测是否为GM或自己
        
        Args:
            roles: 角色列表或单个角色字符串
            pk: 目标资源ID
            user_id: 当前用户ID
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if "GM" not in roles and pk != user_id:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否为管理员或GM
    def is_admin_or_gm(self, roles, raise_exception=True):
        """检测是否为管理员或GM

        Args:
            roles: 角色列表或单个角色字符串
            raise_exception: 是否抛出异常，默认True
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if not any(role in roles for role in ['ADMIN', 'GM']):
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否管理员或自己操作自己的数据
    def is_admin_or_owner(self, roles, pk: UUID, user_id: UUID, raise_exception=True):
        """检测是否管理员或自己操作自己的数据
        
        Args:
            roles: 角色列表或单个角色字符串
            raise_exception: 是否抛出异常，默认True
            pk: 目标资源ID
            user_id: 当前用户ID
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        if not any(role in roles for role in ['ADMIN', 'GM']) and pk != user_id:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True

    # 检测是否管理员或gm或自己操作自己的数据
    def is_admin_or_gm_or_owner(self, roles: list, _user_id: UUID, user_id: UUID, raise_exception=True):
        """检测是否管理员或质检或gm或自己操作自己的数据

        Args:
            roles: 角色列表或单个角色字符串
            _user_id: 检查目标用户ID
            user_id: 当前用户ID
            raise_exception: 是否抛出异常，默认True
        """
        # 兼容旧版本的单个角色字符串
        if isinstance(roles, str):
            roles = [roles]

        _roles = ['ADMIN', 'GM']
        if not any(role in roles for role in _roles) and _user_id != user_id:
            if raise_exception:
                raise HTTPException(status_code=403, detail="权限不足")
            else:
                return False
        return True


verify = Verify()


# FastAPI Security Scheme - 这会在文档中显示锁的图标
security = HTTPBearer(
    scheme_name="JWT Bearer",
    description="JWT认证，格式: Bearer <token>",
    auto_error=False
)


async def get_current_user_or_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    api_token: Optional[str] = Header(None, alias="API-TOKEN")
):
    """
    支持两种认证方式：
    1. JWT Token (Authorization: Bearer xxx)
    2. API Token (API-TOKEN: xxx)
    
    优先使用 JWT，如果没有则尝试 API Token
    """
    # 1. 尝试 JWT 认证
    if credentials:
        try:
            token = credentials.credentials
            payload = JwtToken.verify_token(token)
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


# 基础认证：验证JWT token或API Token
async def get_current_user(user_info: dict = Depends(get_current_user_or_token)):
    """获取当前登录用户信息（支持 JWT 和 API Token）"""
    return user_info


# 管理员权限验证
async def get_admin_user(user_info: dict = Depends(get_current_user_or_token)):
    """验证管理员权限"""
    # 获取用户完整信息以检查角色
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


# 数据权限：检查用户是否有查看所有数据的权限
async def check_data_permission(current_user: dict = Depends(get_current_user)) -> Optional[UUID]:
    """
    检查用户的数据权限
    
    返回值：
    - None: 用户有查看所有数据的权限（ADMIN或GM）
    - UUID: 用户只能查看自己关联的数据，返回用户ID用于过滤
    
    使用示例：
        user_filter = await check_data_permission(current_user)
        # 如果user_filter不为None，则在查询时添加用户过滤条件
        if user_filter:
            query = query.filter(users__id=user_filter)
    """
    try:
        user_id = UUID(current_user["user_id"])
        user = await UserInfo.filter(id=user_id).prefetch_related("roles").first()
        
        if not user:
            raise HTTPException(status_code=403, detail="User not found")
        
        # 获取用户角色
        user_roles = [role.code for role in user.roles]
        
        # ADMIN和GM可以查看所有数据
        if any(role in ["ADMIN", "GM"] for role in user_roles):
            return None
        
        # 其他角色只能查看自己关联的数据
        return user_id
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Permission check failed: {str(e)}")


# 数据权限：检查用户是否可以访问指定项目
async def check_project_access(project_id: UUID, current_user: dict = Depends(get_current_user)) -> bool:
    """
    检查用户是否有权限访问指定项目
    
    Args:
        project_id: 项目ID
        current_user: 当前用户信息
    
    Returns:
        bool: True表示有权限，False表示无权限
    
    Raises:
        HTTPException: 如果无权限且raise_exception=True
    """
    try:
        from app.models.project import ProjectInfo
        
        user_id = UUID(current_user["user_id"])
        user = await UserInfo.filter(id=user_id).prefetch_related("roles").first()
        
        if not user:
            raise HTTPException(status_code=403, detail="User not found")
        
        # 获取用户角色
        user_roles = [role.code for role in user.roles]
        
        # ADMIN和GM可以访问所有项目
        if any(role in ["ADMIN", "GM"] for role in user_roles):
            return True
        
        # 检查用户是否关联到该项目
        project = await ProjectInfo.filter(id=project_id, users__id=user_id).first()
        if not project:
            raise HTTPException(status_code=403, detail="无权访问该项目")
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Permission check failed: {str(e)}")
