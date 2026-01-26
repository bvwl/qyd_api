from datetime import datetime
from pydantic import BaseModel, Field, field_serializer
from typing import List
from uuid import UUID

from app.utils.time_tool import CN_TZ
from app.schemas.user.info import Base as UserBase


class Base(BaseModel):
    """
    基础信息模型

    字段与数据库模型 ServerAccount 保持一致
    """
    username: str = Field(..., description='用户名')
    password: str = Field(..., description='密码（加密存储）')

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建请求模型
    """
    user_id: UUID | None = Field(None, description='关联用户ID')


class Update(BaseModel):
    """
    更新请求模型，支持部分更新
    """
    username: str | None = Field(None, description='用户名')
    password: str | None = Field(None, description='密码（加密存储）')
    user_id: UUID | None = Field(None, description='关联用户ID')


class Out(Base):
    """
    输出模型
    """
    message: str = Field('成功', description='提示信息')
    id: UUID = Field(..., description='ID')

    create_time: datetime = Field(..., description='创建时间')
    update_time: datetime = Field(..., description='更新时间')

    user_id: UUID | None = Field(None, description='关联用户ID')
    
    # XUI 入站状态
    is_all_inbound_added: bool = Field(False, description='是否已添加到所有入站')
    
    # 代理类型（根据端口判断）
    proxy_type: str | None = Field(None, description='代理类型（HTTP/SOCKS5，根据端口自动判断）')

    # 关联的用户信息
    user: UserBase | None = Field(None, description='关联用户信息')

    @field_serializer('create_time', 'update_time')
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime('%Y-%m-%d %H:%M:%S')

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    列表输出模型
    """
    message: str = Field('成功', description='提示信息')
    count: int = Field(0, description='总数')
    num: int = Field(0, description='当前数量')
    items: List[Out] = Field([], description='列表数据')
