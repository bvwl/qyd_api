"""
系统管理API模块
"""
from fastapi import APIRouter
from .database import app as database_router
from .proxy import app as proxy_router

router = APIRouter()
router.include_router(database_router, prefix="/database", tags=["系统-数据库"])
router.include_router(proxy_router, prefix="/proxy", tags=["系统-代理检测"])
