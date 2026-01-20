from uuid import UUID
from fastapi import HTTPException

from app.models.user import UserRole
from app.schemas.user.role import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        is_exist = await UserRole.get_or_none(code=item.code)
        if is_exist:
            raise HTTPException(status_code=400, detail='角色标识已存在')
        
        # 分离关联字段
        data = item.model_dump()
        user_ids = data.pop('user_ids', None)
        route_ids = data.pop('route_ids', None)
        
        res = await UserRole.create(**data)
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        
        # 处理多对多关系
        if user_ids:
            await res.users.add(*user_ids)
        if route_ids:
            await res.routes.add(*route_ids)
        
        await res.fetch_related('users', 'routes')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await UserRole.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('users', 'routes')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        name: str | None = None,
                        code: str | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None
                        ) -> OutList:
        query = UserRole.all()
        if name:
            query = query.filter(name__icontains=name)
        if code:
            query = query.filter(code__icontains=code)
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
        
        # 使用 prefetch_related 预加载多对多关联数据
        res = await query.prefetch_related('users', 'routes')
        
        num = len(res)
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await UserRole.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        if 'code' in update_data:
            new_code = update_data['code']
            is_exist = await UserRole.get_or_none(code=new_code)
            if is_exist and is_exist.id != id:
                raise HTTPException(status_code=400, detail=f'角色标识 {new_code} 已被占用')

        # 分离关联字段
        user_ids = update_data.pop('user_ids', None)
        route_ids = update_data.pop('route_ids', None)
        
        # 更新基本字段
        if update_data:
            await res.update_from_dict(update_data)
            await res.save()
        
        # 处理多对多关系
        if user_ids is not None:
            await res.users.clear()
            if user_ids:
                await res.users.add(*user_ids)
        if route_ids is not None:
            await res.routes.clear()
            if route_ids:
                await res.routes.add(*route_ids)
        
        await res.fetch_related('users', 'routes')
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await UserRole.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)

    # 创建或更新
    async def upsert(self, item: Create) -> Out:
        # 分离关联字段
        data = item.model_dump()
        user_ids = data.pop('user_ids', None)
        route_ids = data.pop('route_ids', None)
        
        record, created = await UserRole.get_or_create(
            defaults=data,
            code=item.code
        )
        if not created:
            update_data = {k: v for k, v in data.items() if k != 'code'}
            if update_data:
                await record.update_from_dict(update_data)
                await record.save()
        
        # 处理多对多关系
        if user_ids is not None:
            await record.users.clear()
            if user_ids:
                await record.users.add(*user_ids)
        if route_ids is not None:
            await record.routes.clear()
            if route_ids:
                await record.routes.add(*route_ids)
        
        await record.fetch_related('users', 'routes')
        return Out.model_validate(record)


role_crud = CRUD()
