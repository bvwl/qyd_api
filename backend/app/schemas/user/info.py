from datetime import datetime
from typing import List, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.models.user import UserStatus
from app.utils.time_tool import CN_TZ
from .role import Base as RoleBase

if TYPE_CHECKING:
    from app.schemas.project.info import Base as ProjectInfoBase


class Base(BaseModel):
    """
    用户基础信息模型

    字段与数据库模型 UserInfo 保持一致（不包含密码哈希）
    """
    email: str = Field(..., max_length=128, description="邮箱")
    nickname: str = Field(..., max_length=64, description="昵称")
    avatar: str | None = Field(None, max_length=255, description="头像")
    status: UserStatus = Field(UserStatus.NORMAL, description="用户状态(1:正常,2:停用,3:锁定,4:封禁)")

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建用户请求模型
    """
    password: str = Field(..., description="密码加密")
    role_ids: List[UUID] | None = Field(None, description="角色ID列表")


class Update(BaseModel):
    """
    更新用户请求模型，支持部分更新
    """
    email: str | None = Field(None, max_length=128, description="邮箱")
    password: str | None = Field(None, description="密码加密")
    nickname: str | None = Field(None, max_length=64, description="昵称")
    avatar: str | None = Field(None, max_length=255, description="头像")
    status: UserStatus | None = Field(None, description="用户状态(1:正常,2:停用,3:锁定,4:封禁)")
    role_ids: List[UUID] | None = Field(None, description="角色ID列表")


class Out(Base):
    """
    用户输出模型
    """
    id: UUID = Field(..., description="ID")

    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    # 关联的角色列表
    roles: List[RoleBase] = Field(default_factory=list, description="角色列表")
    
    # 关联的项目列表 - 移除以避免循环引用
    # projects: List["ProjectInfoBase"] = Field(default_factory=list, description="项目列表")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    用户列表输出模型
    """
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")
