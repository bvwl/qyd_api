from fastapi import APIRouter

from .server import router as server_router
from .mail import router as mail_router
from .user import router as user_router
from .project import router as project_router


api_v1_router = APIRouter()
api_v1_router.include_router(server_router, prefix="/server")
api_v1_router.include_router(mail_router, prefix="/mail")
api_v1_router.include_router(user_router, prefix="/user")
api_v1_router.include_router(project_router, prefix="/project")
