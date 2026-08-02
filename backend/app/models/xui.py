"""
XUI 面板相关数据模型
"""
from enum import IntEnum
from tortoise import fields
from .base import BaseModel


class XuiStatus(IntEnum):
    """XUI 状态"""
    ACTIVE = 1  # 正常
    INACTIVE = 2  # 停用
    ERROR = 3  # 异常


class XuiProtocol(IntEnum):
    """代理协议"""
    HTTP = 1  # HTTP
    SOCKS = 2  # SOCKS5


class XuiServer(BaseModel):
    """
    XUI 服务器配置
    """
    name = fields.CharField(max_length=50, description='服务器名称')
    host = fields.CharField(max_length=50, index=True, description='服务器地址（IP）')
    domain = fields.CharField(max_length=100, index=True, null=True, description='域名（用于 HTTPS 访问）')
    port = fields.IntField(default=10010, description='XUI 面板端口')
    username = fields.CharField(max_length=50, description='XUI 登录用户名')
    password = fields.TextField(description='XUI 登录密码（加密存储）')
    is_ssl = fields.BooleanField(default=False, description='是否使用 HTTPS')
    web_path = fields.CharField(max_length=50, default='/web3', description='Web 路径前缀')
    status = fields.IntEnumField(XuiStatus, default=XuiStatus.ACTIVE, description='状态')
    
    # SSL 证书配置
    cert_file = fields.CharField(max_length=255, null=True, description='SSL 证书文件路径')
    key_file = fields.CharField(max_length=255, null=True, description='SSL 私钥文件路径')
    
    # 备注
    remark = fields.TextField(null=True, description='备注')

    class Meta:
        table = "xui_server"
        table_description = "XUI 服务器配置"
        ordering = ["-create_time"]
        indexes = [
            ("status", "create_time"),
            ("host",),
            ("domain",),
        ]

    def __repr__(self):
        return f"<XuiServer(id={self.id}, name={self.name}, host={self.host})>"

    __str__ = __repr__


class XuiInbound(BaseModel):
    """
    XUI 入站配置
    """
    server = fields.ForeignKeyField(
        "models.XuiServer",
        related_name="inbounds",
        description='关联的 XUI 服务器'
    )
    
    inbound_id = fields.IntField(description='XUI 面板中的入站 ID')
    listen_host = fields.CharField(max_length=50, description='监听地址')
    listen_port = fields.IntField(index=True, description='监听端口')
    protocol = fields.IntEnumField(XuiProtocol, description='协议类型')
    remark = fields.CharField(max_length=100, null=True, description='备注')
    status = fields.IntEnumField(XuiStatus, default=XuiStatus.ACTIVE, description='状态')
    
    # 认证信息（默认账号：cqrxy / Zpaily88）
    default_username = fields.CharField(max_length=50, default='cqrxy', description='默认用户名')
    default_password = fields.TextField(null=True, description='默认密码（加密存储）')
    
    # 多对多关系：入站可以有多个服务器账号
    accounts = fields.ManyToManyField(
        "models.ServerAccount",
        related_name="xui_inbounds",
        through="xuiinbound_accounts",
        description='关联的服务器账号'
    )

    class Meta:
        table = "xui_inbound"
        table_description = "XUI 入站配置"
        ordering = ["-create_time"]
        indexes = [
            ("server_id", "status"),
            ("listen_port",),
            ("server_id", "listen_host", "listen_port"),
        ]
        unique_together = [("server_id", "listen_host", "listen_port")]

    def __repr__(self):
        return f"<XuiInbound(id={self.id}, host={self.listen_host}, port={self.listen_port})>"

    __str__ = __repr__
