from datetime import datetime
from pydantic import BaseModel, Field, field_serializer, computed_field
from typing import List
from enum import Enum
from uuid import UUID
from app.utils.time_tool import CN_TZ
from app.schemas.server.info import Base as ServerInfoBase


class EmailType(str, Enum):
    """
    邮件类型枚举
    """
    IP_OK = 'ip_ok'
    IP_NOT = 'ip_not'
    TOKEN_OK = 'token_ok'
    TOKEN_NOT = 'token_not'
    IP_OK_TOKEN_OK = 'ip_ok_token_ok'
    IP_OK_TOKEN_NOT = 'ip_ok_token_not'
    IP_NOT_TOKEN_OK = 'ip_not_token_ok'
    IP_NOT_TOKEN_NOT = 'ip_not_token_not'


class Base(BaseModel):
    """
    基础信息模型

    字段与数据库模型 EmailInfo 保持一致
    """
    email: str = Field(..., max_length=50, description='邮箱号')
    password: str = Field(..., max_length=50, description='密码')
    auxiliary_email: str = Field(..., max_length=50, description='辅助邮箱')
    auxiliary_email_password: str = Field(...,
                                          max_length=50, description='辅助邮箱密码')
    client_id: str | None = Field(None, max_length=50, description='客户端id')
    access_token: str | None = Field(None, description='access_token')
    refresh_token: str | None = Field(None, description='refresh_token')
    status: int = Field(1, description='状态(1:正常,2:异常)')

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建请求模型
    """
    server_info_id: UUID | None = Field(None, description='代理信息ID')


class Update(BaseModel):
    """
    更新请求模型，支持部分更新
    """
    email: str | None = Field(None, max_length=50, description='邮箱号')
    password: str | None = Field(None, max_length=50, description='密码')
    auxiliary_email: str | None = Field(
        None, max_length=50, description='辅助邮箱')
    auxiliary_email_password: str | None = Field(
        None, max_length=50, description='辅助邮箱密码')
    client_id: str | None = Field(None, max_length=50, description='客户端id')
    access_token: str | None = Field(None, description='access_token')
    refresh_token: str | None = Field(None, description='refresh_token')
    status: int | None = Field(None, description='状态(1:正常,2:异常)')
    server_info_id: UUID | None = Field(None, description='代理信息ID')


class Out(Base):
    """
    输出模型
    """
    message: str = Field('成功', description='提示信息')
    id: UUID = Field(..., description='ID')

    create_time: datetime = Field(..., description='创建时间')
    update_time: datetime = Field(..., description='更新时间')
    server_info_id: UUID | None = Field(None, description='代理信息ID')
    server_info: ServerInfoBase | None = Field(None, description='代理信息')

    @computed_field
    @property
    def proxy_type(self) -> str:
        server = self.server_info
        if not server or server.port is None:
            return "unknown"
        if 20000 <= server.port < 30000:
            return "http"
        if 30000 <= server.port < 40000:
            return "socks5"
        return "unknown"

    @computed_field
    @property
    def proxy_url(self) -> str:
        server = self.server_info

        if not server or server.port is None:
            return ""
        host = server.domain or server.host
        if self.proxy_type == "http":
            return f"http://username:password@{host}:{server.port}"
        if self.proxy_type == "socks5":
            return f"socks5://username:password@{host}:{server.port}"
        return ""

    @field_serializer('create_time', 'update_time')
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime('%Y-%m-%d %H:%M:%S')

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    列表输出模型
    """
    message: str = Field('成功', description='提示信息')
    count: int = Field(0, description='总数')
    num: int = Field(0, description='当前数量')
    items: List[Out] = Field([], description='列表数据')
