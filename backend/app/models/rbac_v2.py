"""
现代化 RBAC 模型 v2
职责分离：菜单显示 ≠ 功能权限 ≠ 数据权限
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
    OK = 1        # 正常
    DISABLED = 2  # 停用


class PermissionType(IntEnum):
    """权限类型"""
    FUNCTION = 1  # 功能权限（按钮、操作）
    API = 2       # API 权限
    DATA = 3      # 数据权限


class DataScope(IntEnum):
    """数据权限范围"""
    ALL = 1              # 全部数据
    DEPT = 2             # 本部门数据
    DEPT_AND_CHILD = 3   # 本部门及下级部门数据
    SELF = 4             # 仅本人数据
    CUSTOM = 5           # 自定义数据范围


# =======================
# 菜单表
# =======================

class Menu(BaseModel):
    """
    菜单表 - 纯粹的前端菜单配置
    
    职责：
    - 只负责前端菜单的显示和路由
    - 不包含权限逻辑
    - 支持无限层级
    
    示例：
        一级菜单：用户管理、项目管理、服务器管理
        二级菜单：用户列表、角色管理、权限管理
        三级菜单：用户详情、角色详情
    """
    # 基础信息
    code = fields.CharField(
        max_length=64,
        unique=True,
        description="菜单编码（唯一标识）"
    )
    title = fields.CharField(
        max_length=64,
        description="菜单标题（显示名称）"
    )
    
    # 路由信息
    path = fields.CharField(
        max_length=128,
        description="路由路径（如：/user/list）"
    )
    component = fields.CharField(
        max_length=128,
        null=True,
        description="组件路径（如：views/User/List）"
    )
    
    # 显示配置
    icon = fields.CharField(
        max_length=64,
        null=True,
        description="图标（如：UserOutlined）"
    )
    sort = fields.IntField(
        default=0,
        description="排序（数字越小越靠前）"
    )
    
    # 层级关系
    parent = fields.ForeignKeyField(
        "models.Menu",
        related_name="children",
        null=True,
        description="父级菜单",
        on_delete=fields.CASCADE
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
    
    # 状态
    status = fields.IntEnumField(
        Status,
        default=Status.OK,
        description="状态(1:正常,2:停用)"
    )
    
    # 关联
    roles: ManyToManyRelation["Role"]
    
    class Meta:
        table = "menus_v2"
        table_description = "菜单表（v2）"
        ordering = ["sort", "create_time"]
        indexes = [
            ("code",),
            ("parent_id", "sort"),
            ("status",),
        ]
    
    def __repr__(self):
        return f"<Menu(code={self.code}, title={self.title})>"
    
    __str__ = __repr__


# =======================
# 权限表
# =======================

class Permission(BaseModel):
    """
    权限表 - 功能权限的最小单元
    
    职责：
    - 定义系统中所有的功能权限点
    - 支持多种权限类型
    - 可选的 API 映射
    
    权限命名规范：{resource}:{action}
    示例：
        - user:view      - 查看用户
        - user:create    - 创建用户
        - user:edit      - 编辑用户
        - user:delete    - 删除用户
        - user:export    - 导出用户
        - project:view   - 查看项目
        - project:create - 创建项目
    """
    # 权限标识（唯一）
    code = fields.CharField(
        max_length=64,
        unique=True,
        description="权限编码（如：user:create）"
    )
    name = fields.CharField(
        max_length=64,
        description="权限名称（如：创建用户）"
    )
    description = fields.CharField(
        max_length=255,
        null=True,
        description="权限描述"
    )
    
    # 权限分类
    resource = fields.CharField(
        max_length=32,
        description="资源类型（user/project/server/mail）"
    )
    action = fields.CharField(
        max_length=32,
        description="操作类型（create/edit/delete/view/export）"
    )
    
    # 权限类型
    permission_type = fields.IntEnumField(
        PermissionType,
        default=PermissionType.FUNCTION,
        description="权限类型(1:功能,2:API,3:数据)"
    )
    
    # API 映射（可选，用于 API 权限）
    api_method = fields.CharField(
        max_length=16,
        null=True,
        description="HTTP方法（GET/POST/PUT/DELETE）"
    )
    api_path = fields.CharField(
        max_length=255,
        null=True,
        description="API路径（如：/api/v1/user）"
    )
    
    # 分组（用于前端展示）
    group = fields.CharField(
        max_length=32,
        null=True,
        description="权限分组（用于前端分组展示）"
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
        table = "permissions_v2"
        table_description = "权限表（v2）"
        ordering = ["resource", "action"]
        indexes = [
            ("code",),
            ("resource",),
            ("permission_type",),
            ("status",),
            ("group",),
        ]
    
    def __repr__(self):
        return f"<Permission(code={self.code}, name={self.name})>"
    
    __str__ = __repr__


# =======================
# 角色表
# =======================

class Role(BaseModel):
    """
    角色表 - 连接用户、菜单、权限的桥梁
    
    职责：
    - 用户组，关联菜单和权限
    - 定义数据权限范围
    - 支持角色级别（用于层级控制）
    
    示例：
        - ADMIN: 系统管理员，拥有所有权限
        - GM: 项目经理，管理项目相关数据
        - IT: 技术人员，管理服务器相关数据
        - MANUAL: 手动操作员，只能查看和编辑
    """
    # 基础信息
    code = fields.CharField(
        max_length=32,
        unique=True,
        description="角色编码（唯一标识）"
    )
    name = fields.CharField(
        max_length=32,
        description="角色名称"
    )
    description = fields.CharField(
        max_length=255,
        null=True,
        description="角色描述"
    )
    
    # 角色级别（用于数据权限和层级控制）
    level = fields.IntField(
        default=0,
        description="角色级别（数字越大权限越高，ADMIN=100）"
    )
    
    # 数据权限范围
    data_scope = fields.IntEnumField(
        DataScope,
        default=DataScope.SELF,
        description="数据权限范围(1:全部,2:本部门,3:本部门及下级,4:仅本人,5:自定义)"
    )
    
    # 系统角色标识
    is_system = fields.BooleanField(
        default=False,
        description="是否系统内置角色（不可删除）"
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
        related_name="roles_v2",
        through="user_role_v2_rel",
        description="角色关联的用户"
    )
    
    menus: ManyToManyRelation["Menu"] = fields.ManyToManyField(
        "models.Menu",
        related_name="roles",
        through="role_menu_v2_rel",
        description="角色关联的菜单"
    )
    
    permissions: ManyToManyRelation["Permission"] = fields.ManyToManyField(
        "models.Permission",
        related_name="roles",
        through="role_permission_v2_rel",
        description="角色关联的权限"
    )
    
    class Meta:
        table = "roles_v2"
        table_description = "角色表（v2）"
        ordering = ["-level", "-create_time"]
        indexes = [
            ("code",),
            ("status",),
            ("level",),
            ("is_system",),
        ]
    
    def __repr__(self):
        return f"<Role(code={self.code}, name={self.name}, level={self.level})>"
    
    __str__ = __repr__


# =======================
# 自定义数据权限表
# =======================

class CustomDataScope(BaseModel):
    """
    自定义数据权限表
    
    用于配置用户/角色的自定义数据访问范围
    
    示例：
        - 角色 GM 可以访问项目 A、B、C
        - 用户 张三 可以访问项目 D、E
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
        related_name="custom_data_scopes_v2",
        null=True,
        description="用户"
    )
    
    # 资源和范围
    resource = fields.CharField(
        max_length=32,
        description="资源类型（project/user/server）"
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
        table = "custom_data_scopes_v2"
        table_description = "自定义数据权限表（v2）"
        indexes = [
            ("role_id", "resource"),
            ("user_id", "resource"),
            ("resource", "resource_id"),
        ]
    
    def __repr__(self):
        return f"<CustomDataScope(resource={self.resource}, resource_id={self.resource_id})>"
    
    __str__ = __repr__


# =======================
# 部门表（可选，用于数据权限）
# =======================

class Department(BaseModel):
    """
    部门表（可选）
    
    用于支持基于部门的数据权限
    
    示例：
        - 技术部
          - 前端组
          - 后端组
        - 运营部
          - 市场组
          - 客服组
    """
    # 基础信息
    code = fields.CharField(
        max_length=32,
        unique=True,
        description="部门编码"
    )
    name = fields.CharField(
        max_length=64,
        description="部门名称"
    )
    description = fields.CharField(
        max_length=255,
        null=True,
        description="部门描述"
    )
    
    # 层级关系
    parent = fields.ForeignKeyField(
        "models.Department",
        related_name="children",
        null=True,
        description="父级部门",
        on_delete=fields.CASCADE
    )
    
    # 负责人
    leader = fields.ForeignKeyField(
        "models.UserInfo",
        related_name="led_departments_v2",
        null=True,
        description="部门负责人"
    )
    
    # 排序
    sort = fields.IntField(
        default=0,
        description="排序"
    )
    
    # 状态
    status = fields.IntEnumField(
        Status,
        default=Status.OK,
        description="状态(1:正常,2:停用)"
    )
    
    class Meta:
        table = "departments"
        table_description = "部门表"
        ordering = ["sort", "create_time"]
        indexes = [
            ("code",),
            ("parent_id",),
            ("status",),
        ]
    
    def __repr__(self):
        return f"<Department(code={self.code}, name={self.name})>"
    
    __str__ = __repr__
