from typing import Dict, Any
from uuid import UUID

from app.models.server import ServerCountry
from ..base import CRUDBase


class CRUD(CRUDBase[ServerCountry]):
    """
    国家信息专用 CRUD

    主要职责：
    - 提供 short_name/status 维度的列表查询
    - 支持按创建时间/更新时间范围过滤
    - 在创建/更新时校验国家简称唯一性
    """
    # 列表查询支持的字段及其查询方式
    QUERY_FIELD_RULES = {
        # 国家简称模糊查询（API 中会先转为大写）
        "short_name": "contains",
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

    async def _before_create(self, obj_in: Dict[str, Any]) -> None:
        """
        创建数据前的校验钩子
        :param obj_in: 创建数据字典
        :raise ValueError: 校验失败时抛异常
        """
        if await self.model.filter(short_name=obj_in['short_name']).first():
            raise ValueError('国家简称已存在')

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: ServerCountry) -> None:
        """更新前校验国家简称唯一性（排除自身）"""
        if "short_name" in update_data:
            new_short_name = update_data["short_name"]
            exists = await self.model.filter(short_name=new_short_name, id__not=id).first()
            if exists:
                raise ValueError(f"国家简称 {new_short_name} 已被占用")


server_country_crud = CRUD(ServerCountry)
