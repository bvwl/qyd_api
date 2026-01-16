from typing import Dict, Any
from uuid import UUID

from app.models.mail import EmailAuth
from ..base import CRUDBase


class CRUD(CRUDBase[EmailAuth]):
    """
    邮箱授权记录专用 CRUD

    主要职责：
    - 提供授权地址维度的模糊查询
    - 支持按创建时间/更新时间范围过滤
    - 在创建时校验授权地址唯一性
    """
    # 列表查询支持的字段及其查询方式
    QUERY_FIELD_RULES = {
        # 授权地址模糊查询
        "authorization_address": "contains",
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
        if await self.model.filter(authorization_address=obj_in['authorization_address']).first():
            raise ValueError('授权地址已存在')


email_auth_crud = CRUD(EmailAuth)
