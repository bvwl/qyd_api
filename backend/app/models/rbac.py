"""
企业级 RBAC 模型
"""
from tortoise import fields
from tortoise.fields import ManyToManyRelation
from enum import IntEnum
from typing import TYPE_CHECKING
from .base import BaseModel

if TYPE_CHECKING:
    from .user import UserInfo


# =======================
# 枚举定义
# =======================

class Status(IntEnum):
    """状态枚举"""
    OK = 1      # 正常
    DISABLED = 2  # 停用


class PermissionType(IntEnum):
    """权限类型"""
    API = 1      # API权限
    BUTTON = 2   # 按钮权限
    DATA = 3     # 数据权限


class DataScope(IntEnum):
    """数据权限范围"""
    ALL = 1              # 全部数据
    DEPT = 2             # 本部门数据
    DEPT_AND_CHILD = 3   # 本部门及下级部门数据
    SELF = 4             # 仅本人数据
    CUSTOM = 5           # 自定义数据范围


# =======================
# 权限表
# =======================

class Permission(BaseModel):
    """
    权限表 - 最细粒度的权限点
    
    权限命名规范：{resource}:{action}
    例如：
        - user:create    - 创建用户
        - user:edit      - 编辑用户
        - user:delete    - 删除用户
        - user:view      - 查看用户
        - project:export - 导出项目
    """
    # 基础信息
    code = fields.CharField(
        max_length=64,
        unique=True,
        description="权限标识（唯一）"
    )
    name = fields.CharField(
        max_length=64,
        description="权限名称"
    )
    resource = fields.CharField(
        max_length=32,
        description="资源类型（如：user, project, server）"
    )
    action = fields.CharField(
        max_length=32,
        description="操作类型（如：create, edit, delete, view）"
    )
    description = fields.CharField(
        max_length=255,
        null=True,
        description="权限描述"
    )
    
    # 权限类型
    permission_type = fields.IntEnumField(
        PermissionType,
        default=PermissionType.API,
        description="权限类型(1:API,2:按钮,3:数据)"
    )
    
    # API 权限相关
    api_method = fields.CharField(
        max_length=16,
        null=True,
        description="HTTP方法（GET/POST/PUT/DELETE）"
    )
    api_path = fields.CharField(
        max_length=255,
        null=True,
        description="API路径（如：/api/v1/users）"
    )
    
    # 数据权限相关
    data_scope = fields.IntEnumField(
        DataScope,
        null=True,
        description="数据范围(1:全部,2:本部门,3:本部门及下级,4:仅本人,5:自定义)"
    )
    
    # 状态
    status = fields.IntEnumField(
        Status,
        default=Status.OK,
        description="状态(1:正常,2:停用)"
    )
    
    # 关联
    roles: ManyToManyRelation["Role"]
    
    class Meta:
        table = "permissions"
        table_description = "权限表"
        ordering = ["resource", "action"]
        indexes = [
            ("code",),
            ("resource",),
            ("permission_type",),
            ("status",),
        ]
    
    def __repr__(self):
        return f"<Permission(code={self.code}, name={self.name})>"
    
    __str__ = __repr__


# =======================
# 菜单表
# =======================

class Menu(BaseModel):
    """
    菜单表 - 只负责前端菜单显示
    与权限完全分离
    """
    # 基础信息
    name = fields.CharField(
        max_length=64,
        description="菜单名称（路由名称）"
    )
    title = fields.CharField(
        max_length=64,
        description="菜单标题（显示名称）"
    )
    path = fields.CharField(
        max_length=128,
        description="路由路径"
    )
    component = fields.CharField(
        max_length=128,
        null=True,
        description="组件路径"
    )
    icon = fields.CharField(
        max_length=64,
        null=True,
        description="图标"
    )
    
    # 层级关系
    parent = fields.ForeignKeyField(
        "models.Menu",
        related_name="children",
        null=True,
        description="父级菜单",
        on_delete=fields.CASCADE
    )
    sort = fields.IntField(
        default=0,
        description="排序（数字越小越靠前）"
    )
    
    # 菜单配置
    is_hidden = fields.BooleanField(
        default=False,
        description="是否隐藏菜单"
    )
    is_cache = fields.BooleanField(
        default=True,
        description="是否缓存页面"
    )
    is_affix = fields.BooleanField(
        default=False,
        description="是否固定在标签页"
    )
    redirect = fields.CharField(
        max_length=128,
        null=True,
        description="重定向路径"
    )
    
    # 关联权限（可选）
    # 如果设置了，则需要有对应权限才能看到菜单
    required_permission = fields.CharField(
        max_length=64,
        null=True,
        description="所需权限标识"
    )
    
    # 状态
    status = fields.IntEnumField(
        Status,
        default=Status.OK,
        description="状态(1:正常,2:停用)"
    )
    
    # 关联
    roles: ManyToManyRelation["Role"]
    
    class Meta:
        table = "menus"
        table_description = "菜单表"
        ordering = ["sort", "create_time"]
        indexes = [
            ("parent_id", "sort"),
            ("status",),
            ("required_permission",),
        ]
    
    def __repr__(self):
        return f"<Menu(name={self.name}, title={self.title})>"
    
    __str__ = __repr__


# =======================
# 角色表（增强版）
# =======================

class Role(BaseModel):
    """
    角色表 - 增强版
    """
    # 基础信息
    name = fields.CharField(
        max_length=32,
        description="角色名称"
    )
    code = fields.CharField(
        max_length=32,
        unique=True,
        description="角色标识（唯一）"
    )
    description = fields.CharField(
        max_length=255,
        null=True,
        description="角色描述"
    )
    
    # 数据权限范围
    data_scope = fields.IntEnumField(
        DataScope,
        default=DataScope.SELF,
        description="数据范围(1:全部,2:本部门,3:本部门及下级,4:仅本人,5:自定义)"
    )
    
    # 角色级别（用于数据权限判断）
    level = fields.IntField(
        default=0,
        description="角色级别（数字越大权限越高）"
    )
    
    # 是否系统内置角色（不可删除）
    is_system = fields.BooleanField(
        default=False,
        description="是否系统角色"
    )
    
    # 状态
    status = fields.IntEnumField(
        Status,
        default=Status.OK,
        description="状态(1:正常,2:停用)"
    )
    
    # 多对多关联
    users: ManyToManyRelation["UserInfo"] = fields.ManyToManyField(
        "models.UserInfo",
        related_name="roles",
        through="user_role_rel",
        description="角色关联的用户"
    )
    
    permissions: ManyToManyRelation["Permission"] = fields.ManyToManyField(
        "models.Permission",
        related_name="roles",
        through="role_permission_rel",
        description="角色关联的权限"
    )
    
    menus: ManyToManyRelation["Menu"] = fields.ManyToManyField(
        "models.Menu",
        related_name="roles",
        through="role_menu_rel",
        description="角色关联的菜单"
    )
    
    class Meta:
        table = "roles"
        table_description = "角色表"
        ordering = ["-level", "-create_time"]
        indexes = [
            ("code",),
            ("status",),
            ("level",),
            ("is_system",),
        ]
    
    def __repr__(self):
        return f"<Role(code={self.code}, name={self.name})>"
    
    __str__ = __repr__


# =======================
# 自定义数据权限表
# =======================

class CustomDataScope(BaseModel):
    """
    自定义数据权限表
    用于配置用户/角色的自定义数据访问范围
    """
    # 关联
    role = fields.ForeignKeyField(
        "models.Role",
        related_name="custom_data_scopes",
        null=True,
        description="角色"
    )
    user = fields.ForeignKeyField(
        "models.UserInfo",
        related_name="custom_data_scopes",
        null=True,
        description="用户"
    )
    
    # 资源和范围
    resource = fields.CharField(
        max_length=32,
        description="资源类型（如：project, user）"
    )
    resource_id = fields.UUIDField(
        description="资源ID"
    )
    
    # 描述
    description = fields.CharField(
        max_length=255,
        null=True,
        description="描述"
    )
    
    class Meta:
        table = "custom_data_scopes"
        table_description = "自定义数据权限表"
        indexes = [
            ("role_id", "resource"),
            ("user_id", "resource"),
            ("resource", "resource_id"),
        ]
    
    def __repr__(self):
        return f"<CustomDataScope(resource={self.resource}, resource_id={self.resource_id})>"
    
    __str__ = __repr__
