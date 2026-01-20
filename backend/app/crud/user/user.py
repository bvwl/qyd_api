from uuid import UUID
from fastapi import HTTPException

from app.models.user import UserInfo
from app.schemas.user.info import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    # 创建
    async def create(self, item: dict | Create) -> Out:
        # 统一处理为字典
        if isinstance(item, dict):
            data = item.copy()
            email = data.get('email')
        else:
            data = item.model_dump()
            email = item.email
        
        is_exist = await UserInfo.get_or_none(email=email)
        if is_exist:
            raise HTTPException(status_code=400, detail='邮箱已存在')
        
        # 分离关联字段
        role_ids = data.pop('role_ids', None)
        
        res = await UserInfo.create(**data)
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        
        # 处理多对多关系
        if role_ids:
            await res.roles.add(*role_ids)
        
        await res.fetch_related('roles', 'projects')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await UserInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('roles', 'projects')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        email: str | None = None,
                        status: int | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None
                        ) -> OutList:
        query = UserInfo.all()
        if email:
            query = query.filter(email__icontains=email)
        if status is not None:
            query = query.filter(status=status)
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
        res = await query.prefetch_related('roles', 'projects')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await UserInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        
        # 检查邮箱唯一性
        if 'email' in update_data:
            new_email = update_data['email']
            is_exist = await UserInfo.get_or_none(email=new_email)
            if is_exist and is_exist.id != id:
                raise HTTPException(status_code=400, detail=f'邮箱 {new_email} 已被占用')
        
        # 分离关联字段
        role_ids = update_data.pop('role_ids', None)
        
        # 更新基本字段
        if update_data:
            await res.update_from_dict(update_data)
            await res.save()
        
        # 处理多对多关系
        if role_ids is not None:
            await res.roles.clear()
            if role_ids:
                await res.roles.add(*role_ids)
        
        await res.fetch_related('roles', 'projects')
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await UserInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)

    # 创建或更新
    async def upsert(self, item: Create) -> Out:
        # 分离关联字段
        data = item.model_dump()
        role_ids = data.pop('role_ids', None)
        
        record, created = await UserInfo.get_or_create(
            defaults=data,
            email=item.email
        )
        
        if not created:
            update_data = {k: v for k, v in data.items() if k != 'email'}
            if update_data:
                await record.update_from_dict(update_data)
                await record.save()
        
        # 处理多对多关系
        if role_ids is not None:
            await record.roles.clear()
            if role_ids:
                await record.roles.add(*role_ids)
        
        await record.fetch_related('roles', 'projects')
        return Out.model_validate(record)


user_crud = CRUD()
