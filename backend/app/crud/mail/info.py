from typing import Dict, Any, List
from uuid import UUID

from app.models.mail import EmailInfo
from ..base import CRUDBase
from app.schemas.mail.info import EmailType
from tortoise.queryset import QuerySet


EMAIL_TYPE_CONDITIONS = {
    # 只看 IP（server_info 是否为空）
    EmailType.IP_OK: (False, None),
    EmailType.IP_NOT: (True, None),
    # 只看 TOKEN（access_token 是否为空）
    EmailType.TOKEN_OK: (None, False),
    EmailType.TOKEN_NOT: (None, True),
    # 同时看 IP + TOKEN 组合
    EmailType.IP_OK_TOKEN_OK: (False, False),
    EmailType.IP_OK_TOKEN_NOT: (False, True),
    EmailType.IP_NOT_TOKEN_OK: (True, False),
    EmailType.IP_NOT_TOKEN_NOT: (True, True),
}


class CRUD(CRUDBase[EmailInfo]):
    """
    邮箱信息专用 CRUD

    主要职责：
    - 提供 email/status 维度的查询
    - 支持按代理信息 server_info_id 过滤
    - 支持按创建时间/更新时间范围过滤
    - 支持按 email_type（IP/TOKEN 组合）进行复杂过滤
    """
    # 列表查询支持的字段及其查询方式
    QUERY_FIELD_RULES = {
        # 邮箱号模糊查询
        "email": "contains",
        # 状态精确匹配
        "status": "exact",
        # 按代理信息 ID 精确过滤
        "server_info_id": "exact",
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
    # 关联字段配置：请求中的 server_info_id 映射到模型的 server_info 外键
    RELATED_FIELDS = {
        "server_info_id": "server_info",
    }
    # 查询时预加载代理信息，方便在 schema 中返回嵌套 server_info
    FETCH_RELATED_FIELDS = ("server_info",)

    def _apply_email_type_filter(
        self,
        query: QuerySet[EmailInfo],
        email_type: EmailType | None,
    ) -> QuerySet[EmailInfo]:
        if email_type is None:
            return query
        ip_is_null, token_is_null = EMAIL_TYPE_CONDITIONS.get(email_type, (None, None))
        if ip_is_null is not None:
            query = query.filter(server_info_id__isnull=ip_is_null)
        if token_is_null is not None:
            query = query.filter(access_token__isnull=token_is_null)
        return query

    async def _before_create(self, obj_in: Dict[str, Any]) -> None:
        """
        创建数据前的校验钩子
        :param obj_in: 创建数据字典
        :raise ValueError: 校验失败时抛异常
        """
        if await self.model.filter(email=obj_in['email']).first():
            raise ValueError('邮箱号已存在')

    async def _before_update(self, id: UUID, update_data: Dict[str, Any], db_obj: EmailInfo) -> None:
        if "email" in update_data:
            new_email = update_data["email"]
            exists = await self.model.filter(email=new_email, id__not=id).first()
            if exists:
                raise ValueError(f"邮箱号 {new_email} 已被占用")

    async def _handle_related_fields(self, db_obj: EmailInfo, related_data: Dict[str, Any], is_created: bool) -> None:
        server_info_id = related_data.get("server_info_id")
        if server_info_id is not None:
            db_obj.server_info_id = server_info_id
            await db_obj.save()

    async def get_multi(
        self,
        page: int = 1,
        limit: int = 10,
        order_by: str = "-create_time",
        email_type: EmailType | None = None,
        proxy_info_id: UUID | None = None,
        **kwargs,
    ) -> List[EmailInfo]:
        """
        邮箱列表查询

        参数说明：
        - email/status：由 QUERY_FIELD_RULES/QUERY_FIELD_MAP 统一处理
        - proxy_info_id：转为 server_info_id 精确过滤
        - email_type：通过 _apply_email_type_filter 追加 IP/TOKEN 组合条件
        """
        if proxy_info_id is not None:
            kwargs["server_info_id"] = proxy_info_id
        query = self._build_query(**kwargs)
        query = self._apply_email_type_filter(query, email_type)
        query = query.order_by(order_by).limit(limit).offset((page - 1) * limit)
        return await query

    async def get_count(
        self,
        email_type: EmailType | None = None,
        proxy_info_id: UUID | None = None,
        **kwargs,
    ) -> int:
        if proxy_info_id is not None:
            kwargs["server_info_id"] = proxy_info_id
        query = self._build_query(**kwargs)
        query = self._apply_email_type_filter(query, email_type)
        return await query.count()


email_info_crud = CRUD(EmailInfo)
