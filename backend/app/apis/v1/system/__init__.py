from fastapi import APIRouter
from .database import router as database_router

router = APIRouter()
router.include_router(database_router, prefix="/database", tags=["系统-数据库"])
