from uuid import UUID
from fastapi import HTTPException

from app.models.mail import EmailInfo
from app.schemas.mail.info import Create, Update, Out, OutList, EmailType
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


# 邮件类型过滤条件映射
EMAIL_TYPE_CONDITIONS = {
    EmailType.IP_OK: (False, None),
    EmailType.IP_NOT: (True, None),
    EmailType.TOKEN_OK: (None, False),
    EmailType.TOKEN_NOT: (None, True),
    EmailType.IP_OK_TOKEN_OK: (False, False),
    EmailType.IP_OK_TOKEN_NOT: (False, True),
    EmailType.IP_NOT_TOKEN_OK: (True, False),
    EmailType.IP_NOT_TOKEN_NOT: (True, True),
}


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        is_exist = await EmailInfo.get_or_none(email=item.email)
        if is_exist:
            raise HTTPException(status_code=400, detail='邮箱号已存在')
        
        # 处理外键字段
        data = item.model_dump(exclude={'server_id'})
        if item.server_id:
            data['server_id'] = item.server_id
        
        res = await EmailInfo.create(**data)
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        await res.fetch_related('server')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await EmailInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('server')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        email: str | None = None,
                        status: int | None = None,
                        server_id: UUID | None = None,
                        email_type: EmailType | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None
                        ) -> OutList:
        query = EmailInfo.all()
        
        if email:
            query = query.filter(email__icontains=email)
        if status is not None:
            query = query.filter(status=status)
        if server_id:
            query = query.filter(server_id=server_id)
        
        # 应用邮件类型过滤
        if email_type:
            ip_is_null, token_is_null = EMAIL_TYPE_CONDITIONS.get(email_type, (None, None))
            if ip_is_null is not None:
                query = query.filter(server_id__isnull=ip_is_null)
            if token_is_null is not None:
                query = query.filter(access_token__isnull=token_is_null)
        
        if create_time_start:
            query = query.filter(create_time__gte=parse_time(create_time_start))
        if create_time_end:
            query = query.filter(create_time__lte=parse_time(
                create_time_end, is_end=True))
        if update_time_start:
            query = query.filter(update_time__gte=parse_time(update_time_start))
        if update_time_end:
            query = query.filter(update_time__lte=parse_time(
                update_time_end, is_end=True))

        if order_by:
            query = query.order_by(order_by)

        if res_count:
            count = await query.count()
        else:
            count = -1

        offset = (page - 1) * limit
        query = query.limit(limit).offset(offset)
        
        # 使用 prefetch_related 预加载 ForeignKey 关联数据
        res = await query.prefetch_related('server')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await EmailInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        if 'email' in update_data:
            new_email = update_data['email']
            is_exist = await EmailInfo.get_or_none(email=new_email)
            if is_exist and is_exist.id != id:
                raise HTTPException(status_code=400, detail=f'邮箱号 {new_email} 已被占用')

        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('server')
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await EmailInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)

    # 创建或更新
    async def upsert(self, item: Create) -> Out:
        # 处理外键字段
        data = item.model_dump(exclude={'server_id'})
        if item.server_id:
            data['server_id'] = item.server_id
        
        record, created = await EmailInfo.get_or_create(
            defaults=data,
            email=item.email
        )
        if not created:
            await record.update_from_dict(item.model_dump(exclude_unset=True, exclude={'server_id'}))
            if item.server_id:
                record.server_id = item.server_id
            await record.save()
        await record.fetch_related('server')
        return Out.model_validate(record)


email_info_crud = CRUD()
