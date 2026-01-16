from typing import Dict, Any
from uuid import UUID

from app.models.user import Permission
from ..base import CRUDBase


class CRUD(CRUDBase[Permission]):
    QUERY_FIELD_RULES = {
        "name": "contains",
        "code": "contains",
        "type": "exact",
        "create_time_start": "gte",
        "create_time_end": "lte",
        "update_time_start": "gte",
        "update_time_end": "lte",
    }
    QUERY_FIELD_MAP = {
        "create_time_start": "create_time",
        "create_time_end": "create_time",
        "update_time_start": "update_time",
        "update_time_end": "update_time",
    }

    async def _before_create(self, obj_in: Dict[str, Any]) -> None:
        if await self.model.filter(code=obj_in["code"]).first():
            raise ValueError("权限标识已存在")

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: Permission) -> None:
        if "code" in update_data:
            new_code = update_data["code"]
            exists = await self.model.filter(code=new_code, id__not=id).first()
            if exists:
                raise ValueError(f"权限标识 {new_code} 已被占用")


permission_crud = CRUD(Permission)


