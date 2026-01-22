from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.models.project import ProjectStatus
from app.utils.time_tool import CN_TZ


class UserBase(BaseModel):
    """
    用户基础信息模型（包含ID）
    用于在项目信息中显示关联的用户
    """
    id: UUID = Field(..., description="用户ID")
    email: str = Field(..., description="邮箱")
    nickname: str = Field(..., description="昵称")
    avatar: str | None = Field(None, description="头像")
    status: int = Field(..., description="用户状态")

    class Config:
        from_attributes = True


class Base(BaseModel):
    """
    项目信息基础模型

    字段与数据库模型 ProjectInfo 保持一致（不包含关联字段）
    """
    name: str = Field(..., description="项目名称")
    status: ProjectStatus = Field(
        ProjectStatus.NORMAL,
        description="项目状态(1:正常,2:未编写,3:编写中,4:项目结束,5:项目跑路,6:项目维护,7:未分配,8:账号不支持,9:ip不支持)",
    )
    content: str | None = Field(
        None,
        description="项目内容文件路径或存储key",
    )

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建项目请求模型
    """
    user_ids: List[UUID] | None = Field(None, description="关联的用户ID列表")


class Update(BaseModel):
    """
    更新项目请求模型，支持部分更新
    """
    name: str | None = Field(None, description="项目名称")
    status: ProjectStatus | None = Field(
        None,
        description="项目状态(1:正常,2:未编写,3:编写中,4:项目结束,5:项目跑路,6:项目维护,7:未分配,8:账号不支持,9:ip不支持)",
    )
    content: str | None = Field(
        None,
        description="项目内容文件路径或存储key",
    )
    user_ids: List[UUID] | None = Field(None, description="关联的用户ID列表")


class Out(Base):
    """
    项目信息输出模型
    """
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="项目ID")

    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    # 关联的用户列表（通过多对多关系获取）
    users: List[UserBase] = Field(default_factory=list, description="关联用户列表")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        # 统一格式化时间为东八区字符串
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    项目列表输出模型
    """
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")

