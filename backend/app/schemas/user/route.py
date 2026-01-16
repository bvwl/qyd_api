from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.utils.time_tool import CN_TZ


class Base(BaseModel):
    name: str = Field(..., max_length=64, description="路由名称")
    path: str = Field(..., max_length=128, description="路由路径")
    component: str = Field(..., max_length=128, description="前端组件路径")
    status: int = Field(1, description="状态 1正常 2停用 3异常 4封禁")

    class Config:
        from_attributes = True


class Create(Base):
    pass


class Update(BaseModel):
    name: str | None = Field(None, max_length=64, description="路由名称")
    path: str | None = Field(None, max_length=128, description="路由路径")
    component: str | None = Field(None, max_length=128, description="前端组件路径")
    status: int | None = Field(None, description="状态 1正常 2停用 3异常 4封禁")


class Out(Base):
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="ID")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")


