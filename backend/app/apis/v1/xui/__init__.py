"""
XUI API 路由
"""
from fastapi import APIRouter
from .server import app as server_app
from .inbound import app as inbound_app
from .user import app as account_app
from .operation import app as operation_app

app = APIRouter()

# 注册子路由
app.include_router(server_app, prefix='/server', tags=['XUI-服务器'])
app.include_router(inbound_app, prefix='/inbound', tags=['XUI-入站'])
app.include_router(account_app, prefix='/account', tags=['XUI-账号管理'])
app.include_router(operation_app, prefix='/operation', tags=['XUI-操作'])
