from fastapi import APIRouter

from .auth import app as auth_app
from .user import app as user_app


router = APIRouter()
router.include_router(auth_app, prefix="/auth", tags=["用户认证"])
router.include_router(user_app, prefix="/user", tags=["用户管理"])

