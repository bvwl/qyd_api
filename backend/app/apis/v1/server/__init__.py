from fastapi import APIRouter
from .account import app as account_app
from .country import app as country_app
from .group import app as group_app
from .info import app as info_app

router = APIRouter()
router.include_router(account_app, prefix="/account", tags=["代理账号"])
router.include_router(country_app, prefix="/country", tags=["国家信息"])
router.include_router(group_app, prefix="/group", tags=["分组信息"])
router.include_router(info_app, prefix="/info", tags=["服务器信息"])
