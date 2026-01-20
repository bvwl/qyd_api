from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.utils.time_tool import CN_TZ

from .info import Base as InfoBase


class Base(BaseModel):
    """
    用户日志基础模型

    字段与数据库模型 UserLog 保持一致
    """
    action: int = Field(..., description="操作类型(枚举)")
    description: str = Field(..., description="操作描述")
    ip: str | None = Field(None, max_length=64, description="IP 地址")
    user_agent: str | None = Field(None, max_length=255, description="User-Agent")

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建用户日志请求模型
    """
    user_id: UUID = Field(..., description="用户ID")


class Update(BaseModel):
    """
    更新用户日志请求模型，支持部分更新
    """
    action: int | None = Field(None, description="操作类型(枚举)")
    description: str | None = Field(None, description="操作描述")
    ip: str | None = Field(None, max_length=64, description="IP 地址")
    user_agent: str | None = Field(None, max_length=255, description="User-Agent")


class Out(Base):
    """
    用户日志输出模型
    """
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="ID")

    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    user_id: UUID = Field(..., description="用户ID")

    # 关联的用户信息
    user: InfoBase = Field(None, description="用户信息")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    用户日志列表输出模型
    """
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")
