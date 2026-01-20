from uuid import UUID
from fastapi import HTTPException

from app.models.server import ServerInfo
from app.schemas.server.info import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        is_exist = await ServerInfo.get_or_none(host=item.host)
        if is_exist:
            raise HTTPException(status_code=400, detail='服务器地址已存在')
        res = await ServerInfo.create(**item.model_dump())
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        await res.fetch_related('group', 'group__country')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await ServerInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('group', 'group__country')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        host: str | None = None,
                        domain: str | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None
                        ) -> OutList:
        query = ServerInfo.all()
        if host:
            query = query.filter(host__icontains=host)
        if domain:
            query = query.filter(domain__icontains=domain)
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
        
        # 使用 prefetch_related 预加载关联数据（包括嵌套关联）
        res = await query.prefetch_related('group', 'group__country')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await ServerInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        if 'host' in update_data:
            new_host = update_data['host']
            is_exist = await ServerInfo.get_or_none(host=new_host)
            if is_exist and is_exist.id != id:
                raise HTTPException(status_code=400, detail=f'服务器地址 {new_host} 已被占用')

        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('group', 'group__country')
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await ServerInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)

    # 创建或更新
    async def upsert(self, item: Create) -> Out:
        record, created = await ServerInfo.get_or_create(
            defaults=item.model_dump(),
            host=item.host
        )
        if not created:
            await record.update_from_dict(item.model_dump(exclude_unset=True))
            await record.save()
        await record.fetch_related('group', 'group__country')
        return Out.model_validate(record)


server_info_crud = CRUD()
