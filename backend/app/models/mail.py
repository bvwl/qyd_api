from tortoise import fields
from .base import BaseModel

"""
- 邮箱信息 - 邮箱号 密码 生日 辅助邮箱 辅助邮箱密码 客户端id access_token refresh_token 代理信息 状态
- 邮箱授权 - 邮箱号 授权地址 响应地址
"""


# 邮箱信息模型
class EmailInfo(BaseModel):
    """
    邮箱信息
    """
    email = fields.CharField(max_length=50, index=True, unique=True, description='邮箱号')
    password = fields.CharField(max_length=50, description='密码')
    auxiliary_email = fields.CharField(max_length=50, description='辅助邮箱')
    auxiliary_email_password = fields.CharField(max_length=50, description='辅助邮箱密码')
    client_id = fields.CharField(max_length=50, null=True, description='客户端id')
    access_token = fields.TextField(null=True, description='access_token')
    refresh_token = fields.TextField(null=True, description='refresh_token')
    status = fields.SmallIntField(default=1, index=True, description='状态(1:正常,2:异常)')

    # 代理信息关联ServerProxy
    server_info = fields.ForeignKeyField("models.ServerInfo", related_name="email_infos", description='代理信息',
                                         null=True)

    class Meta:
        table = "email_info"
        table_description = "邮箱信息"
        ordering = ["-create_time"]
        indexes = [
            ("email", "status"),
            ("status", "create_time"),
        ]

    def __repr__(self):
        return f"<Info(id={self.id}, email={self.email})>"

    __str__ = __repr__


# 邮箱授权模型
class EmailAuth(BaseModel):
    """
    邮箱授权
    """
    email = fields.CharField(max_length=50, index=True, description='邮箱号')
    auth_group = fields.SmallIntField(description='授权组')
    authorization_address = fields.TextField(description='授权地址')
    status = fields.SmallIntField(default=1, index=True,
                                  description='状态(1:待授权, 2:授权成功, 3:授权中, 4:授权失败)')
    back_code = fields.CharField(max_length=50, description='回调code')

    class Meta:
        table = "email_auth"
        table_description = "邮箱授权"
        ordering = ["-create_time"]
        indexes = [
            ("email", "create_time"),
        ]

    def __repr__(self):
        return f"<Info(id={self.id}, email={self.email})>"

    __str__ = __repr__
