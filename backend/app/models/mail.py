from enum import IntEnum
from tortoise import fields
from .base import BaseModel

"""
- 邮箱信息 - 邮箱号 密码 生日 辅助邮箱 辅助邮箱密码 客户端id access_token refresh_token 代理信息 状态
"""


class Status(IntEnum):
    OK = 1  # 正常
    NOT = 2  # 异常


# 邮箱信息模型
class EmailInfo(BaseModel):
    """
    邮箱信息
    """
    email = fields.CharField(max_length=50, index=True, unique=True, description='邮箱号')
    password = fields.TextField(description='密码')
    auxiliary_email = fields.CharField(max_length=50, description='辅助邮箱')
    auxiliary_email_password = fields.TextField(description='辅助邮箱密码')
    client_id = fields.CharField(max_length=50, null=True, description='客户端id')
    access_token = fields.TextField(null=True, description='access_token')
    refresh_token = fields.TextField(null=True, description='refresh_token')
    status = fields.IntEnumField(Status, default=Status.OK, description='状态(1:正常,2:异常)')

    # 代理信息关联ServerProxy
    server = fields.ForeignKeyField(
        "models.ServerInfo",
        related_name="email_infos",
        description='代理信息',
        null=True,
    )

    class Meta:
        table = "email_info"
        table_description = "邮箱信息"
        ordering = ["-create_time"]
        indexes = [
            ("status", "server_id", "create_time"),  # 按状态、服务器和时间查询（EmailType 过滤常用）
            ("status", "create_time"),  # 按状态和时间查询
            ("server_id", "status"),  # 按服务器和状态查询
            # email 已有 index=True 和 unique=True，无需重复声明
            ("update_time",),  # 更新时间查询（自动检查邮箱状态时使用）
        ]

    def __repr__(self):
        return f"<Info(id={self.id}, email={self.email})>"

    __str__ = __repr__
