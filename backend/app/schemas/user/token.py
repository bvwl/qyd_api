from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.models.user import Status
from app.utils.time_tool import CN_TZ
from .info import Base as UserBase


class Base(BaseModel):
    """
    Token 基础模型

    字段与数据库模型 UserToken 保持一致
    """
    token: str = Field(..., description="访问令牌")  # 移除max_length限制，支持长JWT Token
    status: Status = Field(Status.OK, description="是否已失效(1:正常,2:异常)")

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建 Token 请求模型
    """
    user_id: UUID = Field(..., description="用户ID")


class Update(BaseModel):
    """
    更新 Token 请求模型，支持部分更新
    """
    token: str | None = Field(None, description="访问令牌")  # 移除max_length限制
    status: Status | None = Field(None, description="是否已失效(1:正常,2:异常)")


class Out(Base):
    """
    Token 输出模型
    """
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="ID")

    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    user_id: UUID = Field(..., description="用户ID")

    # 关联的用户信息
    user: UserBase = Field(..., description="用户信息")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    Token 列表输出模型
    """
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")


