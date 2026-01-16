from tortoise import fields
from enum import IntEnum
from .base import BaseModel

"""
- 用户角色模型 - 角色名 描述 创建时间 更新时间
- 权限表- 权限名 描述 创建时间 更新时间
- 角色权限表- 角色ID 权限ID
- 用户信息模型 - 邮箱 密码 昵称 头像 状态(1:正常 2:暂停 3:异常 4:封禁) 创建时间 更新时间 角色(关联)
- 用户日志模型 - 描述 创建时间 更新时间 用户(关联)
- token模型 - token 创建时间 更新时间 用户(关联)
- 前端路由模型 - 路由名 描述 创建时间 更新时间 状态(1:正常 2:暂停 3:异常 4:封禁) 角色(关联)
"""


# =======================
# 用户状态枚举
# =======================

class UserStatus(IntEnum):
    NORMAL = 1  # 正常
    DISABLED = 2  # 停用
    LOCKED = 3  # 锁定
    BANNED = 4  # 封禁


# =======================
# 角色模型
# =======================


class Role(BaseModel):
    name = fields.CharField(max_length=32, description="角色名称")
    code = fields.CharField(max_length=32, unique=True, description="角色标识")
    description = fields.CharField(max_length=255, null=True, description="角色描述")

    # 角色权限关联
    permissions: fields.ManyToManyRelation["Permission"]
    # 角色用户关联
    users: fields.ManyToManyRelation["User"]

    class Meta:
        table = "user_roles"
        table_description = "用户角色"
        ordering = ["-create_time"]
        indexes = [
            ("code", "description"),
        ]

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, code={self.code})>"

    __str__ = __repr__


# =======================
# 权限模型
# =======================

class Permission(BaseModel):
    name = fields.CharField(max_length=64, description="权限名称")
    code = fields.CharField(max_length=64, unique=True, description="权限标识，如 user:create")
    type = fields.CharField(max_length=16, description="权限类型 api / menu / button")
    description = fields.CharField(max_length=255, null=True, description="权限描述")

    roles: fields.ManyToManyRelation[Role]
    routes: fields.ManyToManyRelation["FrontendRoute"]

    class Meta:
        table = "permissions"
        table_description = "权限表"
        ordering = ["-create_time"]
        indexes = [
            ("code", "type"),
        ]

    def __repr__(self):
        return f"<Permission(id={self.id}, code={self.code}, type={self.type})>"

    __str__ = __repr__


# =======================
# 用户模型
# =======================

class User(BaseModel):
    email = fields.CharField(
        max_length=128, unique=True, description="邮箱"
    )
    password_hash = fields.CharField(
        max_length=255, description="密码哈希"
    )
    nickname = fields.CharField(
        max_length=64, description="昵称"
    )
    avatar = fields.CharField(
        max_length=255, null=True, description="头像"
    )
    status = fields.IntField(
        default=UserStatus.NORMAL, description="用户状态"
    )

    roles: fields.ManyToManyRelation[Role]
    tokens: fields.ReverseRelation["Token"]
    logs: fields.ReverseRelation["UserLog"]

    class Meta:
        table = "users"
        table_description = "用户信息"
        ordering = ["-create_time"]
        indexes = [
            ("email", "status"),
        ]

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

    __str__ = __repr__


# =======================
# Token 模型（多端登录）
# =======================

class Token(BaseModel):
    user = fields.ForeignKeyField(
        "models.User",
        related_name="tokens",
        on_delete=fields.CASCADE,
        description="所属用户"
    )
    access_token = fields.CharField(
        max_length=255, unique=True, description="访问令牌"
    )
    refresh_token = fields.CharField(
        max_length=255, unique=True, null=True, description="刷新令牌"
    )
    expired_at = fields.DatetimeField(description="过期时间")
    is_revoked = fields.BooleanField(
        default=False, description="是否已失效"
    )

    class Meta:
        table = "tokens"
        table_description = "用户 Token"
        ordering = ["-create_time"]
        indexes = [
            ("user_id", "is_revoked"),
        ]

    def __repr__(self):
        return f"<Token(id={self.id}, user_id={self.user.id})>"

    __str__ = __repr__


# =======================
# 用户操作日志
# =======================


class UserLog(BaseModel):
    user = fields.ForeignKeyField(
        "models.User",
        related_name="logs",
        on_delete=fields.CASCADE,
        description="用户"
    )
    action = fields.CharField(
        max_length=32, description="操作类型"
    )
    description = fields.TextField(description="操作描述")
    ip = fields.CharField(
        max_length=64, null=True, description="IP 地址"
    )
    user_agent = fields.CharField(
        max_length=255, null=True, description="User-Agent"
    )

    class Meta:
        table = "user_logs"
        table_description = "用户操作日志"
        ordering = ["-create_time"]
        indexes = [
            ("user_id", "create_time"),
        ]

    def __repr__(self):
        return f"<UserLog(id={self.id}, user_id={self.user.id}, action={self.action})>"

    __str__ = __repr__


# =======================
# 前端路由模型
# =======================

class FrontendRoute(BaseModel):
    name = fields.CharField(
        max_length=64, description="路由名称"
    )
    path = fields.CharField(
        max_length=128, description="路由路径"
    )
    component = fields.CharField(
        max_length=128, description="前端组件路径"
    )
    status = fields.IntField(
        default=1, description="状态 1正常 2停用 3异常 4封禁"
    )

    permissions: fields.ManyToManyRelation[Permission]

    class Meta:
        table = "frontend_routes"
        table_description = "前端路由"
        ordering = ["-create_time"]
        indexes = [
            ("path", "status"),
        ]

    def __repr__(self):
        return f"<FrontendRoute(id={self.id}, path={self.path})>"

    __str__ = __repr__


# =======================
# 多对多关系定义
# =======================

# User <-> Role
User.roles = fields.ManyToManyField(
    "models.Role",
    related_name="users",
    through="user_role_rel",
    description="用户角色关联"
)

# Role <-> Permission
Role.permissions = fields.ManyToManyField(
    "models.Permission",
    related_name="roles",
    through="role_permission_rel",
    description="角色权限关联"
)

# FrontendRoute <-> Permission
FrontendRoute.permissions = fields.ManyToManyField(
    "models.Permission",
    related_name="routes",
    through="route_permission_rel",
    description="路由权限关联"
)
