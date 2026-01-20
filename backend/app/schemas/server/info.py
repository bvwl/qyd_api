from datetime import datetime
from pydantic import BaseModel, Field, field_serializer, computed_field
from typing import List
from uuid import UUID

from app.models.server import Status, IsSale
from app.utils.time_tool import CN_TZ
from .group import Base as GroupBase


class Base(BaseModel):
    """
    基础信息模型

    字段与数据库模型 ServerInfo 保持一致
    """
    host: str = Field(..., description='服务器地址')
    ssh_port: int | None = Field(None, description='ssh端口')
    password: str | None = Field(None, description='服务器密码')
    status: Status = Field(Status.OK, description='状态(1:正常,2:异常)')
    domain: str | None = Field(None, description='域名')
    is_sale: IsSale = Field(IsSale.YES, description='是否销售(1:是,2:否)')
    port: int | None = Field(None, description='代理端口')

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建请求模型
    """
    group_id: UUID | None = Field(None, description='分组ID')


class Update(BaseModel):
    """
    更新请求模型，支持部分更新
    """
    host: str | None = Field(None, description='服务器地址')
    ssh_port: int | None = Field(None, description='ssh端口')
    password: str | None = Field(None, description='服务器密码')
    status: Status | None = Field(None, description='状态(1:正常,2:异常)')
    domain: str | None = Field(None, description='域名')
    is_sale: IsSale | None = Field(None, description='是否销售(1:是,2:否)')
    port: int | None = Field(None, description='代理端口')
    group_id: UUID | None = Field(None, description='分组ID')


class Out(Base):
    """
    输出模型
    """
    message: str = Field('成功', description='提示信息')
    id: UUID = Field(..., description='ID')

    create_time: datetime = Field(..., description='创建时间')
    update_time: datetime = Field(..., description='更新时间')
    group_id: UUID = Field(..., description='分组ID')
    group: GroupBase = Field(..., description='分组信息')


    @computed_field
    @property
    def proxy_type(self) -> str:
        if self.port is None:
            return "unknown"
        if 20000 <= self.port < 30000:
            return "http"
        elif 30000 <= self.port < 40000:
            return "socks5"
        return "unknown"

    @computed_field
    @property
    def proxy_url(self) -> str:
        if self.port is None:
            return ""
        if self.domain:
            return f"socks5://username:password@{self.domain}:{self.port}"
        return f"socks5://username:password@{self.host}:{self.port}"

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
