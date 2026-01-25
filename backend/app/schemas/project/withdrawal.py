"""
项目提现 Schema
"""
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class WithdrawalBase(BaseModel):
    """提现基础模型"""
    platform_coin: Optional[Decimal] = Field(None, description="平台币余额")
    stable_coin: Optional[Decimal] = Field(None, description="稳定币余额")
    rmb: Optional[Decimal] = Field(None, description="人民币余额")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class Create(WithdrawalBase):
    """创建提现记录"""
    project_id: UUID = Field(..., description="项目ID")


class Update(BaseModel):
    """更新提现记录（部分更新）"""
    platform_coin: Optional[Decimal] = Field(None, description="平台币余额")
    stable_coin: Optional[Decimal] = Field(None, description="稳定币余额")
    rmb: Optional[Decimal] = Field(None, description="人民币余额")
    remark: Optional[str] = Field(None, max_length=500, description="备注")


class Out(BaseModel):
    """提现记录输出"""
    id: UUID
    project_id: UUID
    
    # 平台币
    platform_coin: Optional[Decimal] = None
    platform_coin_change: Decimal = Decimal(0)
    platform_coin_history: Optional[dict] = None
    
    # 稳定币
    stable_coin: Optional[Decimal] = None
    stable_coin_change: Decimal = Decimal(0)
    stable_coin_history: Optional[dict] = None
    
    # 人民币
    rmb: Optional[Decimal] = None
    rmb_change: Decimal = Decimal(0)
    rmb_history: Optional[dict] = None
    
    remark: Optional[str] = None
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class OutList(BaseModel):
    """提现记录列表输出"""
    message: str = "成功"
    count: int = -1
    num: int = 0
    items: list[Out] = []


class StatsOut(BaseModel):
    """统计输出"""
    code: int = 1
    message: str = "成功"
    data: dict
