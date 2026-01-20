from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.utils.time_tool import CN_TZ

if TYPE_CHECKING:
    from .info import Base as UserBase


class RouteLite(BaseModel):
    """
    路由精简模型
    """
    id: UUID = Field(..., description="ID")
    name: str = Field(..., max_length=64, description="路由名称")
    path: str = Field(..., max_length=128, description="路由路径")
    title: str = Field(..., max_length=64, description="菜单标题")
    icon: str | None = Field(None, max_length=64, description="菜单图标")

    class Config:
        from_attributes = True


class Base(BaseModel):
    """
    角色基础信息模型

    字段与数据库模型 UserRole 保持一致
    """
    name: str = Field(..., max_length=32, description="角色名称")
    code: str = Field(..., max_length=32, description="角色标识")
    description: str | None = Field(None, max_length=255, description="角色描述")

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建角色请求模型
    """
    user_ids: List[UUID] | None = Field(None, description="关联用户ID列表")
    route_ids: List[UUID] | None = Field(None, description="关联路由ID列表")


class Update(BaseModel):
    """
    更新角色请求模型，支持部分更新
    """
    name: str | None = Field(None, max_length=32, description="角色名称")
    code: str | None = Field(None, max_length=32, description="角色标识")
    description: str | None = Field(None, max_length=255, description="角色描述")
    user_ids: List[UUID] | None = Field(None, description="关联用户ID列表")
    route_ids: List[UUID] | None = Field(None, description="关联路由ID列表")


class Out(Base):
    """
    角色输出模型
    """
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="ID")

    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    # 关联的用户列表 - 移除以避免循环引用
    # users: List["UserBase"] = Field(default_factory=list, description="用户列表")

    # 关联的路由列表
    routes: List[RouteLite] = Field(default_factory=list, description="路由列表")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    角色列表输出模型
    """
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")
