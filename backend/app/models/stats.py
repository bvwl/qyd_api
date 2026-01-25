"""
统计数据模型
"""
from tortoise import fields
from .base import BaseModel


class ProjectDailyStats(BaseModel):
    """
    项目每日统计
    记录每个项目每天的账号更新数量
    """
    date = fields.DateField(description="统计日期", index=True)
    update_count = fields.IntField(default=0, description="当天更新的账号数量")
    
    # 关联项目
    project = fields.ForeignKeyField(
        "models.ProjectInfo",
        related_name="daily_stats",
        description="所属项目",
        index=True
    )

    class Meta:
        table = "project_daily_stats"
        table_description = "项目每日统计"
        ordering = ["-date"]
        indexes = [
            ("project_id", "date"),  # 按项目和日期查询（最常用）
            ("date",),  # 按日期查询
        ]
        unique_together = [("project_id", "date")]  # 每个项目每天只有一条记录

    def __repr__(self):
        return f"<ProjectDailyStats(id={self.id}, project_id={self.project_id}, date={self.date})>"

    __str__ = __repr__
