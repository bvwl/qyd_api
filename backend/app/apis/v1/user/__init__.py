from fastapi import APIRouter

from .auth import app as auth_app
from .user import app as user_app
from .role import app as role_app
from .route import app as route_app
from .token import app as token_app
from .log import app as log_app
from .user_role import app as user_role_app


router = APIRouter()
router.include_router(auth_app, prefix="/auth", tags=["用户认证"])
router.include_router(user_app, prefix="/user", tags=["用户管理"])
router.include_router(user_role_app, prefix="", tags=["用户角色管理"])  # No prefix, routes already have /user/{user_id}/roles
router.include_router(role_app, prefix="/role", tags=["角色管理"])
router.include_router(route_app, prefix="/route", tags=["路由管理"])
router.include_router(token_app, prefix="/token", tags=["Token管理"])
router.include_router(log_app, prefix="/log", tags=["日志管理"])

