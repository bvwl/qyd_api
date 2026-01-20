from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.utils.time_tool import CN_TZ
from .account import Base as ProjectAccountBase


class Base(BaseModel):
    """
    项目余额基础模型

    字段与数据库模型 ProjectBalance 保持一致（不包含关联对象）
    """
    balance: Decimal = Field(..., description="当前余额")
    variable: Decimal = Field(..., description="变动余额")
    history: dict | None = Field(
        None,
        description="历史余额（可根据需要拆分为独立流水表）",
    )

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建项目余额请求模型
    """
    account_id: UUID = Field(..., description="关联账号ID")


class Update(BaseModel):
    """
    更新项目余额请求模型，支持部分更新
    """
    balance: Decimal | None = Field(None, description="当前余额")
    variable: Decimal | None = Field(None, description="变动余额")
    history: dict | None = Field(
        None,
        description="历史余额（可根据需要拆分为独立流水表）",
    )
    account_id: UUID | None = Field(None, description="关联账号ID")


class Out(Base):
    """
    项目余额输出模型
    """
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="余额记录ID")

    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    account_id: UUID = Field(..., description="关联账号ID")
    
    # 关联的账号信息
    account: ProjectAccountBase = Field(..., description="关联账号信息")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    项目余额列表输出模型
    """
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")

