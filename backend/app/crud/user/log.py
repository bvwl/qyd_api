from uuid import UUID
from fastapi import HTTPException

from app.models.user import UserLog
from app.schemas.user.log import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        res = await UserLog.create(**item.model_dump())
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        await res.fetch_related('user')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await UserLog.get_or_none(id=id).select_related('user')
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('user')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        user_id: UUID | None = None,
                        action: str | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None
                        ) -> OutList:
        query = UserLog.all().select_related('user')
        if user_id:
            query = query.filter(user_id=user_id)
        if action:
            query = query.filter(action__icontains=action)
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

        offset = (page - 1) * limit  # 计算偏移量
        query = query.limit(limit).offset(offset)  # 应用分页
        res = await query
        num = len(res)
        for item in res:
            await item.fetch_related('user')
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await UserLog.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')

        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('user')
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await UserLog.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)


log_crud = CRUD()
