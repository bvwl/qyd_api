"""
项目统计相关的Schema
"""
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import date


class ProjectDailyStats(BaseModel):
    """单个项目的每日统计"""
    project_id: str = Field(..., description="项目ID")
    project_name: str = Field(..., description="项目名称")
    date: str = Field(..., description="日期 YYYY-MM-DD")
    update_count: int = Field(..., description="当天更新的账号数量")


class ProjectStatsTimeSeries(BaseModel):
    """项目统计时间序列数据（用于曲线图）"""
    project_id: str = Field(..., description="项目ID")
    project_name: str = Field(..., description="项目名称")
    dates: List[str] = Field(..., description="日期列表")
    counts: List[int] = Field(..., description="对应日期的更新数量")


class DashboardStatsOut(BaseModel):
    """仪表盘统计输出"""
    code: int = Field(1, description="状态码")
    message: str = Field("成功", description="消息")
    data: List[ProjectStatsTimeSeries] = Field(..., description="项目统计数据列表")


class ProjectDailyStatsQuery(BaseModel):
    """项目每日统计查询参数"""
    days: int = Field(7, ge=1, le=90, description="查询最近N天的数据")
    project_ids: List[str] | None = Field(None, description="指定项目ID列表（可选）")
