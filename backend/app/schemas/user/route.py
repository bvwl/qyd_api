from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.models.user import Status, RouteType
from app.utils.time_tool import CN_TZ
from .role import Base as RoleBase


class Base(BaseModel):
    """
    前端路由基础模型

    字段与数据库模型 FrontendRoute 保持一致
    """
    name: str = Field(..., max_length=64, description="路由名称（唯一标识）")
    path: str = Field(..., max_length=128, description="路由路径")
    component: str | None = Field(None, max_length=128, description="前端组件路径")
    title: str = Field(..., max_length=64, description="菜单标题")
    icon: str | None = Field(None, max_length=64, description="菜单图标")
    sort: int = Field(0, description="排序（数字越小越靠前）")
    redirect: str | None = Field(None, max_length=128, description="重定向路径")
    is_hidden: bool = Field(False, description="是否隐藏菜单")
    is_cache: bool = Field(True, description="是否缓存页面")
    is_affix: bool = Field(False, description="是否固定在标签页")
    route_type: RouteType = Field(RouteType.MENU, description="路由类型(1:菜单,2:按钮,3:接口)")
    permission: str | None = Field(None, max_length=128, description="权限标识")
    api_method: str | None = Field(None, max_length=16, description="API方法")
    api_path: str | None = Field(None, max_length=255, description="API路径")
    status: Status = Field(Status.OK, description="状态(1:正常,2:异常)")

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建前端路由请求模型
    """
    parent_id: UUID | None = Field(None, description="父级路由ID")
    role_ids: List[UUID] | None = Field(None, description="关联角色ID列表")


class Update(BaseModel):
    """
    更新前端路由请求模型，支持部分更新
    """
    name: str | None = Field(None, max_length=64, description="路由名称")
    path: str | None = Field(None, max_length=128, description="路由路径")
    component: str | None = Field(None, max_length=128, description="前端组件路径")
    title: str | None = Field(None, max_length=64, description="菜单标题")
    icon: str | None = Field(None, max_length=64, description="菜单图标")
    sort: int | None = Field(None, description="排序")
    redirect: str | None = Field(None, max_length=128, description="重定向路径")
    is_hidden: bool | None = Field(None, description="是否隐藏菜单")
    is_cache: bool | None = Field(None, description="是否缓存页面")
    is_affix: bool | None = Field(None, description="是否固定在标签页")
    route_type: RouteType | None = Field(None, description="路由类型(1:菜单,2:按钮,3:接口)")
    permission: str | None = Field(None, max_length=128, description="权限标识")
    api_method: str | None = Field(None, max_length=16, description="API方法")
    api_path: str | None = Field(None, max_length=255, description="API路径")
    status: Status | None = Field(None, description="状态(1:正常,2:异常)")
    parent_id: UUID | None = Field(None, description="父级路由ID")
    role_ids: List[UUID] | None = Field(None, description="关联角色ID列表")


class Out(Base):
    """
    前端路由输出模型
    """
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="ID")

    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    parent_id: UUID | None = Field(None, description="父级路由ID")

    # 子路由列表
    children: List["Out"] = Field(default_factory=list, description="子路由列表")

    # 关联的角色列表（简化版，只包含基本信息）
    roles: List[RoleBase] = Field(default_factory=list, description="角色列表")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True
        # 忽略额外的字段，避免未加载的关联数据导致验证失败
        extra = 'ignore'


class OutList(BaseModel):
    """
    前端路由列表输出模型
    """
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")


