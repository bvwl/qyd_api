from datetime import datetime
from pydantic import BaseModel, Field, field_serializer
from typing import List
from uuid import UUID

from app.models.server import Status
from app.utils.time_tool import CN_TZ
from .country import Base as ServerCountryBase


class Base(BaseModel):
    """
    基础信息模型

    字段与数据库模型 ServerGroup 保持一致
    """
    name: str = Field(..., description='分组名称')
    status: Status = Field(Status.OK, description='状态(1:正常,2:异常)')

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建请求模型
    """
    country_id: UUID = Field(..., description='国家ID')


class Update(BaseModel):
    """
    更新请求模型，支持部分更新
    """
    name: str | None = Field(None, description='分组名称')
    country_id: UUID | None = Field(None, description='国家ID')
    status: Status | None = Field(None, description='状态(1:正常,2:异常)')


class Out(Base):
    """
    输出模型
    """
    message: str = Field('成功', description='提示信息')
    id: UUID = Field(..., description='ID')

    create_time: datetime = Field(..., description='创建时间')
    update_time: datetime = Field(..., description='更新时间')
    country_id: UUID = Field(..., description='国家ID')
    country: ServerCountryBase | None = Field(None, description='国家')

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
