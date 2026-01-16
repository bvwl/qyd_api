from typing import Dict, Any
from uuid import UUID

from app.models.user import Token
from ..base import CRUDBase


class CRUD(CRUDBase[Token]):
    QUERY_FIELD_RULES = {
        "user_id": "exact",
        "is_revoked": "exact",
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
    RELATED_FIELDS = {
        "user_id": "user",
    }

    async def _before_create(self, obj_in: Dict[str, Any]) -> None:
        if await self.model.filter(access_token=obj_in["access_token"]).first():
            raise ValueError("访问令牌已存在")

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: Token) -> None:
        if "access_token" in update_data:
            new_token = update_data["access_token"]
            exists = await self.model.filter(access_token=new_token, id__not=id).first()
            if exists:
                raise ValueError("访问令牌已存在")

    async def _handle_related_fields(self, db_obj: Token, related_data: Dict[str, Any], is_created: bool) -> None:
        user_id = related_data.get("user_id")
        if user_id is not None:
            db_obj.user_id = user_id
            await db_obj.save()


token_crud = CRUD(Token)
