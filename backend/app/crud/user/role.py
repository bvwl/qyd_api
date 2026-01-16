from typing import Dict, Any
from uuid import UUID

from app.models.user import Role
from ..base import CRUDBase


class CRUD(CRUDBase[Role]):
    """
    角色专用 CRUD

    主要职责：
    - 提供 name/code 维度的查询
    - 支持按创建时间/更新时间范围过滤
    - 写入时校验角色标识唯一性
    """
    # 列表查询支持的字段及其查询方式
    QUERY_FIELD_RULES = {
        # 角色名称 / 标识模糊查询
        "name": "contains",
        "code": "contains",
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

    async def _before_create(self, obj_in: Dict[str, Any]) -> None:
        """
        创建数据前的校验钩子
        :param obj_in: 创建数据字典
        :raise ValueError: 校验失败时抛异常
        """
        if await self.model.filter(code=obj_in["code"]).first():
            raise ValueError("角色标识已存在")

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: Role) -> None:
        """更新前校验角色标识唯一性（排除自身）"""
        if "code" in update_data:
            new_code = update_data["code"]
            exists = await self.model.filter(code=new_code, id__not=id).first()
            if exists:
                raise ValueError(f"角色标识 {new_code} 已被占用")


role_crud = CRUD(Role)

