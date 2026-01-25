"""
XUI 入站 Schema
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from uuid import UUID

from app.utils.time_tool import CN_TZ


class XuiInboundBase(BaseModel):
    """XUI 入站基础 Schema"""
    listen_host: str = Field(..., description='监听地址', max_length=50)
    listen_port: int = Field(..., description='监听端口', ge=20000, le=33000)
    protocol: int = Field(..., description='协议类型(1:HTTP,2:SOCKS)')
    remark: Optional[str] = Field(None, description='备注', max_length=100)
    status: int = Field(1, description='状态(1:正常,2:停用,3:异常)')
    default_username: Optional[str] = Field('cqrxy', description='默认用户名', max_length=50)
    default_password: Optional[str] = Field('Zpaily88', description='默认密码')


class XuiInboundCreate(XuiInboundBase):
    """创建 XUI 入站"""
    server_id: UUID = Field(..., description='XUI 服务器 ID')


class XuiInboundUpdate(BaseModel):
    """更新 XUI 入站"""
    listen_host: Optional[str] = Field(None, description='监听地址', max_length=50)
    listen_port: Optional[int] = Field(None, description='监听端口', ge=20000, le=33000)
    protocol: Optional[int] = Field(None, description='协议类型(1:HTTP,2:SOCKS)')
    remark: Optional[str] = Field(None, description='备注', max_length=100)
    status: Optional[int] = Field(None, description='状态(1:正常,2:停用,3:异常)')
    default_username: Optional[str] = Field(None, description='默认用户名', max_length=50)
    default_password: Optional[str] = Field(None, description='默认密码')


class XuiInboundOut(XuiInboundBase):
    """XUI 入站输出"""
    id: UUID = Field(..., description='ID')
    server_id: UUID = Field(..., description='XUI 服务器 ID')
    inbound_id: int = Field(..., description='XUI 面板中的入站 ID')
    create_time: datetime = Field(..., description='创建时间')
    update_time: datetime = Field(..., description='更新时间')

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        # 统一格式化时间为东八区字符串
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class XuiInboundOutList(BaseModel):
    """XUI 入站列表输出"""
    message: str = Field('成功', description='消息')
    count: int = Field(-1, description='总数')
    num: int = Field(0, description='当前数量')
    items: list[XuiInboundOut] = Field([], description='数据列表')


class XuiInboundBatchCreate(BaseModel):
    """批量创建 XUI 入站"""
    server_id: UUID = Field(..., description='XUI 服务器 ID')
    inbounds: list[XuiInboundBase] = Field(..., description='入站配置列表')
