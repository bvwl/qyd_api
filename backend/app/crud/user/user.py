from typing import Dict, Any
from uuid import UUID

from app.models.user import User
from ..base import CRUDBase


class CRUD(CRUDBase[User]):
    """
    用户信息专用 CRUD

    主要职责：
    - 提供 email/status 维度的查询
    - 支持按创建时间/更新时间范围过滤
    - 查询时预加载角色信息
    - 写入时处理角色多对多关联（role_ids -> roles）
    """
    # 列表查询支持的字段及其查询方式
    QUERY_FIELD_RULES = {
        # 邮箱模糊查询
        "email": "contains",
        # 状态精确匹配
        "status": "exact",
        # 创建/更新时间范围查询
        "create_time_start": "gte",
        "create_time_end": "lte",
        "update_time_start": "gte",
        "update_time_end": "lte",
    }
    # 查询参数名到模型字段名的映射（处理 xxx_start/xxx_end）
    QUERY_FIELD_MAP = {
        "create_time_start": "create_time",
        "create_time_end": "create_time",
        "update_time_start": "update_time",
        "update_time_end": "update_time",
    }
    # 查询时预加载角色信息
    FETCH_RELATED_FIELDS = ("roles",)
    # 关联字段配置：请求中的 role_ids 映射到模型的 roles 多对多关系
    RELATED_FIELDS = {
        "role_ids": "roles",
    }

    async def _before_create(self, obj_in: Dict[str, Any]) -> None:
        """
        创建数据前的校验钩子
        :param obj_in: 创建数据字典
        :raise ValueError: 校验失败时抛异常
        """
        if await self.model.filter(email=obj_in["email"]).first():
            raise ValueError("邮箱已存在")

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: User) -> None:
        """更新前校验邮箱唯一性（排除自身）"""
        if "email" in update_data:
            new_email = update_data["email"]
            exists = await self.model.filter(email=new_email, id__not=id).first()
            if exists:
                raise ValueError(f"邮箱 {new_email} 已被占用")

    async def _handle_related_fields(self, db_obj: User, related_data: Dict[str, Any], is_created: bool) -> None:
        """
        处理关联字段：角色多对多关系
        """
        role_ids = related_data.get("role_ids")
        if role_ids is not None:
            # 先清空原有关联
            await db_obj.roles.clear()
            # 再添加新的角色
            if role_ids:
                await db_obj.roles.add(*role_ids)


user_crud = CRUD(User)

