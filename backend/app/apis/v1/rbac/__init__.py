"""
RBAC v2 API 路由
"""
from fastapi import APIRouter

from .menu import app as menu_router
from .user import app as user_router
from .role import app as role_router

router = APIRouter()
router.include_router(menu_router, prefix="/menu", tags=["RBAC-菜单"])
router.include_router(user_router, prefix="/user", tags=["RBAC-用户"])
router.include_router(role_router, prefix="/role", tags=["RBAC-角色"])
