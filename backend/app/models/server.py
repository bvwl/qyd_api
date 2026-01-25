from enum import IntEnum
from tortoise import fields
from .base import BaseModel


class Status(IntEnum):
    OK = 1  # 正常
    NOT = 2  # 异常


class IsSale(IntEnum):
    YES = 1  # 是
    NO = 2  # 否


# 服务器国家类
class ServerCountry(BaseModel):
    """
    国家信息
    """
    # 简称
    short_name = fields.CharField(max_length=2, index=True, unique=True, description='国家简称')
    name = fields.CharField(max_length=20, description='国家名称')
    status = fields.IntEnumField(Status, default=Status.OK, description='状态(1:正常,2:异常)')

    class Meta:
        table = "server_country"
        table_description = "国家信息"
        ordering = ["-create_time"]
        indexes = [
            ("status", "create_time"),  # 按状态和时间查询
            # short_name 已有 index=True 和 unique=True，无需重复声明
        ]

    def __repr__(self):
        return f"<Info(id={self.id},name={self.name},short_name={self.short_name})>"

    __str__ = __repr__


# 分组类
class ServerGroup(BaseModel):
    """
    分组信息
    """
    name = fields.CharField(max_length=20, index=True, unique=True, description='分组名称')
    status = fields.IntEnumField(Status, default=Status.OK, description='状态(1:正常,2:异常)')

    # 外键关联国家类
    country = fields.ForeignKeyField(
        "models.ServerCountry",
        related_name="server_groups",
        description='国家'
    )

    class Meta:
        table = "server_group"
        table_description = "分组信息"
        ordering = ["-create_time"]
        indexes = [
            ("country_id", "status", "create_time"),  # 按国家、状态和时间查询
            ("status", "create_time"),  # 按状态和时间查询
            # name 已有 index=True 和 unique=True，无需重复声明
        ]

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
    password = fields.TextField(null=True, description='服务器密码（加密存储）')
    status = fields.IntEnumField(Status, default=Status.OK, description='状态(1:正常,2:异常)')
    domain = fields.CharField(max_length=50, index=True, null=True, description='域名')
    is_sale = fields.IntEnumField(IsSale, default=IsSale.YES, description='是否销售(1:是,2:否)')
    port = fields.IntField(null=True, description='代理端口')

    # 外键关联分组类
    group = fields.ForeignKeyField(
        "models.ServerGroup",
        null=True,
        related_name="server_infos",
        description='分组'
    )

    class Meta:
        table = "server_info"
        table_description = "服务器信息"
        ordering = ["-create_time"]
        indexes = [
            ("status", "is_sale", "create_time"),  # 按状态、销售状态和时间查询
            ("group_id", "status"),  # 按分组和状态查询
            # host 和 domain 已有 index=True，无需重复声明
        ]

    def __repr__(self):
        return (
            f"<Info(id={self.id}, host={self.host}, port={self.port}, status={self.status})>")

    __str__ = __repr__


# 服务器账号类
class ServerAccount(BaseModel):
    """
    服务器账号
    """
    username = fields.CharField(max_length=36, index=True, description='用户名')
    password = fields.TextField(description='密码（加密存储）')
    is_all_inbound_added = fields.BooleanField(
        default=False, 
        index=True, 
        description='是否已添加到所有入站(用于XUI管理)'
    )

    # 外键关联用户信息类（一对一，可选）
    user = fields.OneToOneField(
        "models.UserInfo",
        related_name="server_account",
        null=True,
        description='关联用户信息',
    )

    class Meta:
        table = "proxy_account"
        table_description = "服务器账号"
        ordering = ["-create_time"]
        indexes = [
            ("user_id", "create_time"),  # 按用户和时间查询
            ("is_all_inbound_added",),  # 按是否添加到入站查询
            # username 已有 index=True，无需重复声明
        ]

    def __repr__(self):
        return f"<Info(id={self.id},username={self.username})>"

    __str__ = __repr__
