from typing import Dict, Any

from app.models.user import UserLog
from ..base import CRUDBase


class CRUD(CRUDBase[UserLog]):
    QUERY_FIELD_RULES = {
        "user_id": "exact",
        "action": "contains",
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
        return None


log_crud = CRUD(UserLog)

