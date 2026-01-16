from fastapi import APIRouter
from .v1 import api_v1_router

apis_router = APIRouter()
apis_router.include_router(api_v1_router, prefix="/v1")
