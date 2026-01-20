from uuid import UUID
from fastapi import HTTPException

from app.models.server import ServerAccount
from app.schemas.server.account import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        is_exist = await ServerAccount.get_or_none(username=item.username)
        if is_exist:
            raise HTTPException(status_code=400, detail='用户名已存在')
        
        # 处理外键字段
        data = item.model_dump(exclude={'user_id'})
        if item.user_id:
            data['user_id'] = item.user_id
        
        res = await ServerAccount.create(**data)
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        await res.fetch_related('user')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await ServerAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='用户不存在')
        await res.fetch_related('user')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        username: str | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None
                        ) -> OutList:
        query = ServerAccount.all()
        if username:
            query = query.filter(username__icontains=username)
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
        
        # 使用 prefetch_related 预加载关联数据
        res = await query.prefetch_related('user')
        
        num = len(res)
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await ServerAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='用户不存在')
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')

        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('user')
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await ServerAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='用户不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)

    # 创建或更新
    async def upsert(self, item: Create) -> Out:
        # 处理外键字段
        data = item.model_dump(exclude={'user_id'})
        if item.user_id:
            data['user_id'] = item.user_id
        
        record, created = await ServerAccount.get_or_create(
            defaults=data,
            username=item.username
        )
        if not created:
            await record.update_from_dict(item.model_dump(exclude_unset=True, exclude={'user_id'}))
            if item.user_id:
                record.user_id = item.user_id
            await record.save()
        await record.fetch_related('user')
        return Out.model_validate(record)


server_account_crud = CRUD()
