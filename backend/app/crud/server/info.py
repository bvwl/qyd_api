from typing import Dict, Any
from uuid import UUID

from app.models.server import ServerInfo
from ..base import CRUDBase


class CRUD(CRUDBase[ServerInfo]):
    """
    服务器信息专用 CRUD

    主要职责：
    - 提供 host/domain 维度的查询
    - 支持按创建时间/更新时间范围过滤
    - 写入时处理分组外键（group_id -> group）
    """
    # 列表查询支持的字段及其查询方式
    QUERY_FIELD_RULES = {
        # 服务器地址 / 域名模糊查询
        "host": "contains",
        "domain": "contains",
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
    # 查询时预加载分组，便于 schema 中直接返回嵌套分组对象
    FETCH_RELATED_FIELDS = ("group",)
    # 关联字段配置：请求中的 group_id 映射到模型的 group 外键
    RELATED_FIELDS = {
        "group_id": "group",
    }

    async def _before_create(self, obj_in: Dict[str, Any]) -> None:
        """
        创建数据前的校验钩子
        :param obj_in: 创建数据字典
        :raise ValueError: 校验失败时抛异常
        """
        if await self.model.filter(host=obj_in['host']).first():
            raise ValueError('服务器地址已存在')

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: ServerInfo) -> None:
        """更新前校验服务器地址唯一性（排除自身）"""
        if "host" in update_data:
            new_host = update_data["host"]
            exists = await self.model.filter(host=new_host, id__not=id).first()
            if exists:
                raise ValueError(f"服务器地址 {new_host} 已被占用")

    async def _handle_related_fields(self, db_obj: ServerInfo, related_data: Dict[str, Any], is_created: bool) -> None:
        """
        处理关联字段：分组外键 group_id
        """
        group_id = related_data.get("group_id")
        if group_id is not None:
            db_obj.group_id = group_id
            await db_obj.save()


server_info_crud = CRUD(ServerInfo)
