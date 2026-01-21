from uuid import UUID
from fastapi import HTTPException

from app.models.project import ProjectWallet
from app.schemas.project.wallet import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        res = await ProjectWallet.create(**item.model_dump())
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        await res.fetch_related('project')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await ProjectWallet.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('project')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        project_id: UUID | None = None,
                        chain: str | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None
                        ) -> OutList:
        query = ProjectWallet.all()
        
        if project_id:
            query = query.filter(project_id=project_id)
        
        if chain:
            query = query.filter(chain__icontains=chain)
        
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
        
        # 预加载关联的项目信息
        res = await query.prefetch_related('project')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await ProjectWallet.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        
        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('project')
        
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await ProjectWallet.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)

    # 创建或更新（根据公钥唯一性）
    async def upsert(self, item: Create) -> Out:
        record, created = await ProjectWallet.get_or_create(
            defaults=item.model_dump(),
            public_key=item.public_key
        )
        
        if not created:
            update_data = item.model_dump(exclude_unset=True)
            if update_data:
                await record.update_from_dict(update_data)
                await record.save()
        
        await record.fetch_related('project')
        return Out.model_validate(record)


project_wallet_crud = CRUD()
