from fastapi import APIRouter
from .auth import app as auth_app


router = APIRouter()
router.include_router(auth_app, prefix="/auth", tags=["用户认证"])

