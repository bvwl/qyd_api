from fastapi import APIRouter

from .info import app as info_app
from .account import app as account_app
from .wallet import app as wallet_app
from .withdrawal import app as withdrawal_app
from .stats import app as stats_app
from .file import app as file_app


router = APIRouter()
router.include_router(info_app, prefix="/info", tags=["项目信息"])
router.include_router(account_app, prefix="/account", tags=["项目账号"])
router.include_router(wallet_app, prefix="/wallet", tags=["项目钱包"])
router.include_router(withdrawal_app, prefix="/withdrawal", tags=["项目提现"])
router.include_router(stats_app, prefix="/stats", tags=["项目统计"])
router.include_router(file_app, prefix="/file", tags=["项目文件"])

