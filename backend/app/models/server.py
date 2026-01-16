import uuid
from tortoise import fields
from tortoise.models import Model
from .base import BaseModel


# 服务器国家类
class ServerCountry(BaseModel):
    """
    国家信息
    """
    # 简称
    short_name = fields.CharField(max_length=2, index=True, unique=True, description='国家简称')
    name = fields.CharField(max_length=20, description='国家名称')
    status = fields.SmallIntField(default=1, index=True, description='状态(1:正常,2:异常)')

    class Meta:
        table = "server_country"
        table_description = "国家信息"
        ordering = ["-create_time"]
        indexes = [
            ("short_name", "name"),
        ]

    def __repr__(self):
        return f"<Info(id={self.id},name={self.name},short_name={self.short_name})>"

    __str__ = __repr__


# 分组类
class ServerGroup(BaseModel):
    """
    分组信息
    """
    name = fields.CharField(max_length=20, unique=True, description='分组名称')
    status = fields.SmallIntField(default=1, index=True, description='状态(1:正常,2:异常)')

    # 外键关联国家类
    country = fields.ForeignKeyField("models.ServerCountry", related_name="server_groups", description='国家')

    class Meta:
        table = "server_group"
        table_description = "分组信息"
        ordering = ["-create_time"]

    def __repr__(self):
        return f"<Info(id={self.id},name={self.name})>"

    __str__ = __repr__


# 服务器信息类
class ServerInfo(BaseModel):
    """
    服务器信息
    """
    # 服务器相关
    host = fields.CharField(max_length=20, index=True, description='服务器地址')
    ssh_port = fields.IntField(null=True, description='ssh端口')
    password = fields.CharField(max_length=128, null=True, description='服务器密码')
    status = fields.SmallIntField(default=1, index=True, description='状态(1:正常,4:异常)')
    domain = fields.CharField(max_length=50, index=True, null=True, description='域名')
    is_sale = fields.SmallIntField(default=1, index=True, description='是否销售(1:是,2:否)')
    port = fields.IntField(null=True, description='代理端口')

    # 外键关联分组类
    group = fields.ForeignKeyField("models.ServerGroup", null=True, related_name="server_infos", description='分组')

    class Meta:
        table = "server_info"
        table_description = "服务器信息"
        ordering = ["-create_time"]
        indexes = [
            ("host", "status"),
            ("status", "create_time"),
        ]

    def __repr__(self):
        return (
            f"<Info(id={self.id}, host={self.host}, port={self.port}, status={self.status})>")

    __str__ = __repr__


# 代理账号类
class ProxyAccount(BaseModel):
    """
    代理账号
    """
    username = fields.CharField(max_length=36, index=True, description='用户名')
    password = fields.CharField(max_length=36, description='密码')

    # 外键关联用户信息类

    class Meta:
        table = "proxy_account"
        table_description = "代理账号"
        ordering = ["-create_time"]
        indexes = [
            ("username", "create_time"),
        ]

    def __repr__(self):
        return f"<Info(id={self.id},username={self.username},password={self.password})>"

    __str__ = __repr__
