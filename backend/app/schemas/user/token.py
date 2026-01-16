from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.utils.time_tool import CN_TZ


class Base(BaseModel):
    user_id: UUID = Field(..., description="用户ID")
    access_token: str = Field(..., max_length=255, description="访问令牌")
    refresh_token: str | None = Field(None, max_length=255, description="刷新令牌")
    expired_at: datetime = Field(..., description="过期时间")
    is_revoked: bool = Field(False, description="是否已失效")

    class Config:
        from_attributes = True


class Create(Base):
    pass


class Update(BaseModel):
    access_token: str | None = Field(None, max_length=255, description="访问令牌")
    refresh_token: str | None = Field(None, max_length=255, description="刷新令牌")
    expired_at: datetime | None = Field(None, description="过期时间")
    is_revoked: bool | None = Field(None, description="是否已失效")


class Out(Base):
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="ID")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("create_time", "update_time", "expired_at")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")


