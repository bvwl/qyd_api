from typing import Dict, Any
from uuid import UUID

from app.models.server import ServerGroup
from ..base import CRUDBase


class CRUD(CRUDBase[ServerGroup]):
    """
    分组信息专用 CRUD

    主要职责：
    - 提供 name/status 维度的列表查询
    - 支持按创建时间/更新时间范围过滤
    - 预加载关联的国家信息，方便在 schema 中直接返回嵌套对象
    """
    # 列表查询支持的字段及其查询方式
    QUERY_FIELD_RULES = {
        # 分组名称模糊查询（API 中会先转为大写）
        "name": "contains",
        # 状态精确匹配
        "status": "exact",
        # 创建/更新时间范围查询（配合 QUERY_FIELD_MAP 使用）
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
    # 本模型目前没有通过 CRUD 基类写入的关联字段
    RELATED_FIELDS = {}
    # 查询时预加载国家信息，便于在 schema 中返回嵌套国家对象
    FETCH_RELATED_FIELDS = ("country",)

    async def _before_create(self, obj_in: Dict[str, Any]) -> None:
        """
        创建数据前的校验钩子
        :param obj_in: 创建数据字典
        :raise ValueError: 校验失败时抛异常
        """
        if await self.model.filter(name=obj_in['name']).first():
            raise ValueError('分组名称已存在')

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: ServerGroup) -> None:
        """更新前校验分组名称唯一性（排除自身）"""
        if "name" in update_data:
            new_name = update_data["name"]
            exists = await self.model.filter(name=new_name, id__not=id).first()
            if exists:
                raise ValueError(f"分组名称 {new_name} 已被占用")


server_group_crud = CRUD(ServerGroup)
