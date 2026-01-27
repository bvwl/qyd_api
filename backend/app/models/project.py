from enum import IntEnum

from tortoise import fields
from tortoise.fields import ManyToManyRelation
from .base import BaseModel
from .user import UserInfo


class Status(IntEnum):
    OK = 1  # 正常
    NOT = 2  # 异常


class ProjectStatus(IntEnum):
    NORMAL = 1  # 正常
    NOT_WRITTEN = 2  # 未编写
    WRITING = 3  # 编写中
    ENDED = 4  # 项目结束
    RUNAWAY = 5  # 项目跑路
    MAINTENANCE = 6  # 项目维护
    UNASSIGNED = 7  # 未分配
    ACCOUNT_NOT_SUPPORT = 8  # 账号不支持
    IP_NOT_SUPPORT = 9  # IP不支持


class AccountType(IntEnum):
    EMAIL = 1  # 邮箱
    WALLET = 2  # 钱包
    X = 3  # x
    OTHER1 = 4  # 其他1
    OTHER2 = 5  # 其他2


# 项目信息模型
class ProjectInfo(BaseModel):
    """
    项目信息
    """
    name = fields.CharField(max_length=100, index=True, description="项目名称")
    status = fields.IntEnumField(
        ProjectStatus,
        default=ProjectStatus.NORMAL,
        description="状态(1:正常,2:未编写,3:编写中,4:项目结束,5:项目跑路,6:项目维护,7:未分配,8:账号不支持,9:ip不支持)",
    )
    content = fields.CharField(
        max_length=255,
        null=True,
        description="项目内容文件路径或存储key",
    )
    users: ManyToManyRelation["UserInfo"] = fields.ManyToManyField(
        "models.UserInfo",
        related_name="projects",
        through="project_user_rel",
        description="项目与用户关联",
    )

    class Meta:
        table = "project_info"
        table_description = "项目信息"
        ordering = ["-create_time"]
        indexes = [
            ("status", "create_time"),  # 按状态和时间查询（最常用）
            # name 已有 index=True，无需重复声明
        ]

    def __repr__(self):
        return f"<ProjectInfo(id={self.id}, name={self.name})>"

    __str__ = __repr__


# 项目钱包模型
class ProjectWallet(BaseModel):
    """
    项目钱包
    """
    private_key = fields.TextField(description="私钥（AES加密）")
    public_key = fields.TextField(description="公钥")
    mnemonic = fields.TextField(null=True, description="助记词（AES加密）")
    chain = fields.CharField(max_length=255, description="链")
    remark = fields.CharField(max_length=255, null=True, description="备注")

    # 和项目信息关联
    project = fields.ForeignKeyField("models.ProjectInfo", null=True, related_name="wallets", description="所属项目")

    class Meta:
        table = "project_wallet"
        table_description = "项目钱包"
        ordering = ["-create_time"]
        indexes = [
            ("chain", "create_time"),  # 按链和时间查询
            ("create_time",),  # 时间范围查询
        ]

    def __repr__(self):
        return f"<ProjectWallet(id={self.id})>"

    __str__ = __repr__


# 项目账号模型
class ProjectAccount(BaseModel):
    """
    项目账号
    """
    account = fields.CharField(max_length=255, index=True, description="账号")
    password = fields.TextField(null=True, description="密码（明文存储）")
    status = fields.IntEnumField(Status, default=Status.OK, description="状态(1:正常,2:异常)")
    account_type = fields.IntEnumField(
        AccountType,
        default=AccountType.EMAIL,
        description="账号类型(1:邮箱,2:钱包,3:x,4:其他1,5:其他2)",
    )
    data = fields.JSONField(null=True, description="扩展数据")
    
    # 余额相关字段（支持虚拟币精度，最多18位小数）
    balance = fields.DecimalField(max_digits=38, decimal_places=18, default=0, description="余额")
    variable = fields.DecimalField(max_digits=38, decimal_places=18, default=0, description="变动余额")
    balance_history = fields.JSONField(null=True, description="历史余额（可根据需要拆分为独立流水表）")

    project = fields.ForeignKeyField("models.ProjectInfo", related_name="accounts", description="所属项目")
    server = fields.ForeignKeyField("models.ServerInfo", related_name="project_accounts", null=True,
                                    description="关联服务器信息")

    class Meta:
        table = "project_account"
        table_description = "项目账号"
        ordering = ["-create_time"]
        indexes = [
            ("project_id", "status", "account_type"),  # 按项目、状态和类型查询
            ("status", "account_type", "create_time"),  # 按状态和类型查询
            ("server_id", "status"),  # 按服务器和状态查询
            ("balance",),  # 按余额查询
            # account 已有 index=True，无需重复声明
        ]

    def __repr__(self):
        return f"<ProjectAccount(id={self.id}, account={self.account})>"

    __str__ = __repr__


# 项目提现模型
class ProjectWithdrawal(BaseModel):
    """
    项目提现记录
    每次更新都会记录完整的历史，使用时间戳作为key，所有记录永久保存
    支持虚拟币精度（18位小数）
    """
    # 平台币相关（支持虚拟币精度）
    platform_coin = fields.DecimalField(
        max_digits=38, 
        decimal_places=18, 
        null=True, 
        description="平台币当前余额"
    )
    platform_coin_change = fields.DecimalField(
        max_digits=38, 
        decimal_places=18, 
        default=0, 
        description="平台币最近一次变动"
    )
    platform_coin_history = fields.JSONField(
        null=True, 
        description="平台币历史记录（所有记录，格式：{'2026-01-25 14:30:45': '100.500000000000000000'}）"
    )
    
    # 稳定币相关（支持虚拟币精度）
    stable_coin = fields.DecimalField(
        max_digits=38, 
        decimal_places=18, 
        null=True, 
        description="稳定币当前余额"
    )
    stable_coin_change = fields.DecimalField(
        max_digits=38, 
        decimal_places=18, 
        default=0, 
        description="稳定币最近一次变动"
    )
    stable_coin_history = fields.JSONField(
        null=True, 
        description="稳定币历史记录（所有记录，格式：{'2026-01-25 14:30:45': '100.500000000000000000'}）"
    )
    
    # 人民币相关（保持2位小数）
    rmb = fields.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        null=True, 
        description="人民币当前余额"
    )
    rmb_change = fields.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        default=0, 
        description="人民币最近一次变动"
    )
    rmb_history = fields.JSONField(
        null=True, 
        description="人民币历史记录（所有记录，格式：{'2026-01-25 14:30:45': '100.50'}）"
    )
    
    # 关联项目
    project = fields.ForeignKeyField(
        "models.ProjectInfo", 
        related_name="withdrawals", 
        description="所属项目",
        index=True
    )
    
    # 备注
    remark = fields.CharField(
        max_length=500, 
        null=True, 
        description="备注"
    )

    class Meta:
        table = "project_withdrawal"
        table_description = "项目提现记录"
        ordering = ["-create_time"]
        indexes = [
            ("project_id", "create_time"),  # 按项目和时间查询（最常用）
            ("create_time",),  # 时间范围查询
        ]
        unique_together = [("project_id",)]  # 每个项目只有一条记录

    def __repr__(self):
        return f"<ProjectWithdrawal(id={self.id}, project_id={self.project_id})>"

    __str__ = __repr__
