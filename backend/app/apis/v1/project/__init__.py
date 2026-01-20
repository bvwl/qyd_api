from fastapi import APIRouter

from .info import app as info_app
from .account import app as account_app
from .wallet import app as wallet_app
from .balance import app as balance_app


router = APIRouter()
router.include_router(info_app, prefix="/info", tags=["项目信息"])
router.include_router(account_app, prefix="/account", tags=["项目账号"])
router.include_router(wallet_app, prefix="/wallet", tags=["项目钱包"])
router.include_router(balance_app, prefix="/balance", tags=["项目余额"])

