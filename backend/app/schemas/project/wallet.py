from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_serializer

from app.utils.time_tool import CN_TZ


class Base(BaseModel):
    """
    项目钱包基础模型

    字段与数据库模型 ProjectWallet 保持一致（不包含关联对象）
    """
    private_key: str = Field(..., description="私钥（AES加密）")
    public_key: str = Field(..., description="公钥")
    mnemonic: str = Field(..., description="助记词（AES加密）")
    chain: str = Field(..., description="链")
    remark: str | None = Field(None, description="备注")

    class Config:
        from_attributes = True


class Create(Base):
    """
    创建项目钱包请求模型
    """
    pass


class Update(BaseModel):
    """
    更新项目钱包请求模型，支持部分更新
    """
    private_key: str | None = Field(None, description="私钥（AES加密）")
    public_key: str | None = Field(None, description="公钥")
    mnemonic: str | None = Field(None, description="助记词（AES加密）")
    chain: str | None = Field(None, description="链")
    remark: str | None = Field(None, description="备注")


class Out(Base):
    """
    项目钱包输出模型
    """
    message: str = Field("成功", description="提示信息")
    id: UUID = Field(..., description="钱包ID")

    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_datetime(self, dt: datetime) -> str:
        return dt.astimezone(CN_TZ).strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """
    项目钱包列表输出模型
    """
    message: str = Field("成功", description="提示信息")
    count: int = Field(0, description="总数")
    num: int = Field(0, description="当前数量")
    items: List[Out] = Field([], description="列表数据")

