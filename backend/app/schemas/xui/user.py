"""
XUI 入站账号管理 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class XuiInboundAccountAdd(BaseModel):
    """添加账号到入站"""
    inbound_id: UUID = Field(..., description='入站 ID')
    account_id: UUID = Field(..., description='服务器账号 ID')


class XuiInboundAccountRemove(BaseModel):
    """从入站移除账号"""
    inbound_id: UUID = Field(..., description='入站 ID')
    account_id: UUID = Field(..., description='服务器账号 ID')


class XuiInboundAccountBatchAdd(BaseModel):
    """批量添加账号到入站"""
    inbound_id: UUID = Field(..., description='入站 ID')
    account_ids: List[UUID] = Field(..., description='服务器账号 ID 列表')


class XuiInboundAccountOut(BaseModel):
    """入站账号输出"""
    inbound_id: UUID = Field(..., description='入站 ID')
    account_id: UUID = Field(..., description='账号 ID')
    username: str = Field(..., description='用户名')
    user_id: Optional[UUID] = Field(None, description='关联的系统用户 ID')

    class Config:
        from_attributes = True


class XuiInboundAccountOutList(BaseModel):
    """入站账号列表输出"""
    message: str = Field('成功', description='消息')
    count: int = Field(-1, description='总数')
    num: int = Field(0, description='当前数量')
    items: List[XuiInboundAccountOut] = Field([], description='数据列表')


class XuiInitializeRequest(BaseModel):
    """XUI 面板初始化请求"""
    server_id: UUID = Field(..., description='XUI 服务器 ID')
    inbounds: list = Field(..., description='入站配置列表')
    configure_cert: bool = Field(False, description='是否配置 SSL 证书')


class XuiOperationResponse(BaseModel):
    """XUI 操作响应"""
    success: bool = Field(..., description='是否成功')
    message: str = Field(..., description='消息')
    data: Optional[dict] = Field(None, description='返回数据')
