"""
XUI 服务器 Schema
"""
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from uuid import UUID

from app.utils.time_tool import CN_TZ


class XuiServerBase(BaseModel):
    """XUI 服务器基础 Schema"""
    name: str = Field(..., description='服务器名称', max_length=50)
    host: str = Field(..., description='服务器地址（IP）', max_length=50)
    domain: Optional[str] = Field(None, description='域名（用于 HTTPS 访问）', max_length=100)
    port: int = Field(10010, description='XUI 面板端口', ge=1, le=65535)
    username: str = Field(..., description='XUI 登录用户名', max_length=50)
    is_ssl: bool = Field(False, description='是否使用 HTTPS')
    web_path: str = Field('/web3', description='Web 路径前缀', max_length=50)
    status: int = Field(1, description='状态(1:正常,2:停用,3:异常)')
    cert_file: Optional[str] = Field(None, description='SSL 证书文件路径', max_length=255)
    key_file: Optional[str] = Field(None, description='SSL 私钥文件路径', max_length=255)
    remark: Optional[str] = Field(None, description='备注')


class XuiServerCreate(XuiServerBase):
    """创建 XUI 服务器"""
    password: str = Field(..., description='XUI 登录密码')


class XuiServerUpdate(BaseModel):
    """更新 XUI 服务器"""
    name: Optional[str] = Field(None, description='服务器名称', max_length=50)
    host: Optional[str] = Field(None, description='服务器地址（IP）', max_length=50)
    domain: Optional[str] = Field(None, description='域名（用于 HTTPS 访问）', max_length=100)
    port: Optional[int] = Field(None, description='XUI 面板端口', ge=1, le=65535)
    username: Optional[str] = Field(None, description='XUI 登录用户名', max_length=50)
    password: Optional[str] = Field(None, description='XUI 登录密码')
    is_ssl: Optional[bool] = Field(None, description='是否使用 HTTPS')
    web_path: Optional[str] = Field(None, description='Web 路径前缀', max_length=50)
    status: Optional[int] = Field(None, description='状态(1:正常,2:停用,3:异常)')
    cert_file: Optional[str] = Field(None, description='SSL 证书文件路径', max_length=255)
    key_file: Optional[str] = Field(None, description='SSL 私钥文件路径', max_length=255)
    remark: Optional[str] = Field(None, description='备注')


class XuiServerOut(XuiServerBase):
    """XUI 服务器输出"""
    id: UUID = Field(..., description='ID')
    password: Optional[str] = Field(None, description='密码（仅管理员可见）')
    create_time: datetime = Field(..., description='创建时间')
    update_time: datetime = Field(..., description='更新时间')

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        # 统一格式化时间为东八区字符串
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class XuiServerOutList(BaseModel):
    """XUI 服务器列表输出"""
    message: str = Field('成功', description='消息')
    count: int = Field(-1, description='总数')
    num: int = Field(0, description='当前数量')
    items: list[XuiServerOut] = Field([], description='数据列表')
