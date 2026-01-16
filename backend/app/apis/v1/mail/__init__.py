from fastapi import APIRouter
from .info import app as info_app
from .auth import app as auth_app
from .outlook import app as outlook_app

router = APIRouter()
router.include_router(info_app, prefix="/info", tags=["邮箱信息"])
router.include_router(auth_app, prefix="/auth", tags=["邮箱授权"])
router.include_router(outlook_app, prefix="/outlook", tags=["Outlook操作"])
