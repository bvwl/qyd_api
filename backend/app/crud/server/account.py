from typing import Dict, Any
from uuid import UUID

from app.models.server import ProxyAccount
from ..base import CRUDBase


class CRUD(CRUDBase[ProxyAccount]):
    """
    代理账号专用 CRUD

    主要职责：
    - 提供用户名维度的模糊查询
    - 支持按创建时间/更新时间范围过滤
    - 在创建/更新时校验用户名唯一性
    """
    # 列表查询支持的字段及其查询方式
    QUERY_FIELD_RULES = {
        # 用户名模糊查询
        "username": "icontains",
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
        if await self.model.filter(username=obj_in['username']).first():
            raise ValueError('用户名已存在')

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: ProxyAccount) -> None:
        """更新前校验用户名唯一性（排除自身）"""
        if "username" in update_data:
            new_username = update_data["username"]
            exists = await self.model.filter(username=new_username, id__not=id).first()
            if exists:
                raise ValueError(f"用户名 {new_username} 已被占用")



server_account_crud = CRUD(ProxyAccount)
