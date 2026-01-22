from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer
from app.models.project import Status, AccountType
from app.utils.time_tool import CN_TZ
from app.schemas.server.info import Base as ServerInfoBase
from .info import Base as ProjectInfoBase


class Base(BaseModel):
    """
    项目账号基础模型

    字段与数据库模型 ProjectAccount 保持一致（不包含关联对象）
    """
    account: str = Field(..., description="账号")
    password: str | None = Field(None, description="密码（加密存储）")
    status: Status = Field(Status.OK, description="账号状态(1:正常,2:异常)")
    account_type: AccountType = Field(
        AccountType.EMAIL,
        description="账号类型(1:邮箱,2:钱包,3:x,4:其他1,5:其他2)",
    )
    data: dict | None = Field(None, description="扩展数据")
    
    # 余额相关字段
    balance: Decimal = Field(0, description="余额")
    variable: Decimal = Field(0, description="变动余额")
    balance_history: dict | None = Field(None, description="历史余额")

    class Config:
        from_attributes = True


class Create(BaseModel):
    """
    创建项目账号请求模型
    """
    account: str = Field(..., description="账号")
    password: str | None = Field(None, description="密码（加密存储）")
    status: Status = Field(Status.OK, description="账号状态(1:正常,2:异常)")
    account_type: AccountType = Field(
        AccountType.EMAIL,
        description="账号类型(1:邮箱,2:钱包,3:x,4:其他1,5:其他2)",
    )
    data: dict | None = Field(None, description="扩展数据")
    balance: Decimal | None = Field(None, description="余额（可选，默认0）")
    variable: Decimal | None = Field(None, description="变动余额（可选，默认0）")
    balance_history: dict | None = Field(None, description="历史余额")
    project_id: UUID = Field(..., description="所属项目ID")
    server_id: UUID | None = Field(None, description="关联服务器信息ID")


class Update(BaseModel):
    """
    更新项目账号请求模型，支持部分更新
    """
    account: str | None = Field(None, description="账号")
    password: str | None = Field(None, description="密码（加密存储）")
    status: Status | None = Field(None, description="账号状态(1:正常,2:异常)")
    account_type: AccountType | None = Field(
        None,
        description="账号类型(1:邮箱,2:钱包,3:x,4:其他1,5:其他2)",
    )
    data: dict | None = Field(None, description="扩展数据")
    balance: Decimal | None = Field(None, description="余额")
    variable: Decimal | None = Field(None, description="变动余额")
    balance_history: dict | None = Field(None, description="历史余额")
    project_id: UUID | None = Field(None, description="所属项目ID")
    server_id: UUID | None = Field(None, description="关联服务器信息ID")


class Out(Base):
    """
    项目账号输出模型
    """
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="账号ID")

    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    project_id: UUID = Field(..., description="所属项目ID")
    server_id: UUID | None = Field(None, description="关联服务器信息ID")

    # 关联的项目和服务器基础信息
    project: ProjectInfoBase = Field(..., description="项目信息")
    server: ServerInfoBase | None = Field(None, description="服务器信息")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    项目账号列表输出模型
    """
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")
