from tortoise import fields
from tortoise.fields import ManyToManyRelation
from enum import IntEnum
from typing import TYPE_CHECKING
from .base import BaseModel

if TYPE_CHECKING:
    from .project import ProjectInfo

"""
- 用户角色模型 - 角色名 描述 创建时间 更新时间
- 用户信息模型 - 邮箱 密码 昵称 头像 状态(1:正常 2:暂停 3:异常 4:封禁) 创建时间 更新时间 角色(关联)
- 用户日志模型 - 描述 创建时间 更新时间 用户(关联)
- token模型 - token 创建时间 更新时间 用户(关联)
- 前端路由模型 - 路由名 描述 创建时间 更新时间 状态(1:正常 2:暂停 3:异常 4:封禁) 角色(关联)
"""


class Status(IntEnum):
    OK = 1  # 正常
    NOT = 2  # 异常


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


class UserRole(BaseModel):
    name = fields.CharField(max_length=32, description="角色名称")
    code = fields.CharField(max_length=32, unique=True, description="角色标识")
    description = fields.CharField(max_length=255, null=True, description="角色描述")

    # 多对多关联：角色 <-> 用户
    users: ManyToManyRelation["UserInfo"] = fields.ManyToManyField(
        "models.UserInfo",
        related_name="roles",
        through="user_role_rel",
        description="角色关联的用户",
    )

    # 角色 <-> 路由（反向关联，由 FrontendRoute 定义）
    routes: ManyToManyRelation["FrontendRoute"]

    class Meta:
        table = "user_roles"
        table_description = "用户角色"
        ordering = ["-create_time"]
        indexes = [
            ("code",),  # 唯一索引已存在，单独索引用于查询
            ("name",),  # 按名称模糊查询
            ("create_time",),  # 时间范围查询
        ]

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name}, code={self.code})>"

    __str__ = __repr__


# =======================
# 用户模型
# =======================

class UserInfo(BaseModel):
    email = fields.CharField(
        max_length=128, unique=True, description="邮箱"
    )
    password = fields.TextField(description="密码加密")
    nickname = fields.CharField(
        max_length=64, description="昵称"
    )
    avatar = fields.CharField(
        max_length=255, null=True, description="头像"
    )
    status = fields.IntEnumField(
        UserStatus, default=UserStatus.NORMAL, description="用户状态"
    )

    # 用户 <-> 角色（反向关联，由 UserRole 定义）
    roles: ManyToManyRelation["UserRole"]

    # 用户 <-> 项目（反向关联，由 ProjectInfo 定义）
    projects: ManyToManyRelation["ProjectInfo"]  # type: ignore

    class Meta:
        table = "users"
        table_description = "用户信息"
        ordering = ["-create_time"]
        indexes = [
            ("status", "create_time"),  # 按状态和时间查询（常用组合）
            ("create_time",),  # 时间范围查询
        ]

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

    __str__ = __repr__


# =======================
# Token 模型（api使用）
# =======================

class UserToken(BaseModel):
    user = fields.ForeignKeyField(
        "models.UserInfo",
        related_name="tokens",
        description="所属用户"
    )
    token = fields.TextField(description="访问令牌")  # 使用TextField支持长Token
    status = fields.IntEnumField(
        Status, default=Status.OK, description="是否已失效"
    )

    class Meta:
        table = "tokens"
        table_description = "用户 Token"
        ordering = ["-create_time"]
        indexes = [
            ("user_id", "status", "create_time"),  # 按用户和状态查询，包含时间排序
            ("status", "create_time"),  # 按状态和时间查询
            ("create_time",),  # 时间范围查询
        ]

    def __repr__(self):
        return f"<Token(id={self.id}, user_id={self.user.id})>"

    __str__ = __repr__


# =======================
# 用户操作日志
# =======================


class UserLog(BaseModel):
    user = fields.ForeignKeyField(
        "models.UserInfo",
        related_name="logs",
        description="用户"
    )
    action = fields.SmallIntField(description="操作类型(枚举)")
    description = fields.TextField(description="操作描述")
    ip = fields.CharField(max_length=64, null=True, index=True, description="IP 地址")
    user_agent = fields.CharField(max_length=255, null=True, description="User-Agent")

    class Meta:
        table = "user_logs"
        table_description = "用户操作日志"
        ordering = ["-create_time"]
        indexes = [
            ("user_id", "create_time"),  # 按用户查询日志（最常用）
            ("user_id", "action", "create_time"),  # 按用户和操作类型查询
            ("action", "create_time"),  # 按操作类型查询
            ("create_time",),  # 时间范围查询
        ]

    def __repr__(self):
        return f"<UserLog(id={self.id}, user_id={self.user.id}, action={self.action})>"

    __str__ = __repr__


# =======================
# 路由类型枚举
# =======================

class RouteType(IntEnum):
    MENU = 1      # 菜单
    BUTTON = 2    # 按钮
    API = 3       # 接口


# =======================
# 前端路由模型（菜单权限）
# =======================

class FrontendRoute(BaseModel):
    """
    前端路由/菜单配置
    """
    # 基础信息
    name = fields.CharField(max_length=64, description="路由名称（唯一标识）")
    path = fields.CharField(max_length=128, description="路由路径")
    component = fields.CharField(max_length=128, null=True, description="前端组件路径")

    # 显示信息
    title = fields.CharField(max_length=64, description="菜单标题")
    icon = fields.CharField(max_length=64, null=True, description="菜单图标")

    # 层级关系
    parent = fields.ForeignKeyField(
        "models.FrontendRoute",
        related_name="children",
        null=True,
        description="父级路由",
        on_delete=fields.CASCADE,
    )
    sort = fields.IntField(default=0, description="排序（数字越小越靠前）")

    # 路由配置
    redirect = fields.CharField(max_length=128, null=True, description="重定向路径")
    is_hidden = fields.BooleanField(default=False, description="是否隐藏菜单")
    is_cache = fields.BooleanField(default=True, description="是否缓存页面")
    is_affix = fields.BooleanField(default=False, description="是否固定在标签页")

    # 权限配置（新增）
    route_type = fields.IntEnumField(
        RouteType,
        default=RouteType.MENU,
        description="路由类型(1:菜单,2:按钮,3:接口)"
    )
    permission = fields.CharField(
        max_length=128,
        null=True,
        description="权限标识（如：user:create, user:edit）"
    )
    api_method = fields.CharField(
        max_length=16,
        null=True,
        description="API方法(GET/POST/PUT/DELETE)"
    )
    api_path = fields.CharField(
        max_length=255,
        null=True,
        description="API路径"
    )

    # 多对多关联：路由 <-> 角色
    roles: ManyToManyRelation["UserRole"] = fields.ManyToManyField(
        "models.UserRole",
        related_name="routes",
        through="role_route_rel",
        description="路由关联的角色",
    )

    # 状态
    status = fields.IntEnumField(
        Status,
        default=Status.OK,
        description="状态(1:正常,2:异常)",
    )

    class Meta:
        table = "frontend_routes"
        table_description = "前端路由/菜单"
        ordering = ["sort", "-create_time"]
        indexes = [
            ("status", "parent_id", "sort"),  # 按状态和父级查询，包含排序
            ("parent_id", "sort"),  # 按父级查询子路由（树形结构常用）
            ("path",),  # 按路径查询
            ("name",),  # 按名称模糊查询
            ("permission",),  # 按权限标识查询
            ("route_type",),  # 按路由类型查询
            ("create_time",),  # 时间范围查询
        ]

    def __repr__(self):
        return f"<FrontendRoute(id={self.id}, name={self.name}, path={self.path})>"

    __str__ = __repr__
