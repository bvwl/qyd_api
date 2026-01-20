from uuid import UUID
from fastapi import HTTPException

from app.models.project import ProjectAccount
from app.schemas.project.account import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        res = await ProjectAccount.create(**item.model_dump())
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        await res.fetch_related('project', 'server', 'server__group', 'server__group__country')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await ProjectAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('project', 'server', 'server__group', 'server__group__country')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        account: str | None = None,
                        status: int | None = None,
                        account_type: int | None = None,
                        project_id: UUID | None = None,
                        server_info_id: UUID | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None
                        ) -> OutList:
        query = ProjectAccount.all()
        if account:
            query = query.filter(account__icontains=account)
        if status is not None:
            query = query.filter(status=status)
        if account_type is not None:
            query = query.filter(account_type=account_type)
        if project_id:
            query = query.filter(project_id=project_id)
        if server_info_id:
            query = query.filter(server_info_id=server_info_id)
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
            await item.fetch_related('project', 'server', 'server__group', 'server__group__country')
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await ProjectAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')

        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('project', 'server', 'server__group', 'server__group__country')
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await ProjectAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.delete()
        return BaseOut(message='成功', count=1)

    # 创建或更新
    async def upsert(self, item: Create) -> Out:
        record, created = await ProjectAccount.get_or_create(
            defaults=item.model_dump(),
            account=item.account,
            project_id=item.project_id
        )
        if not created:
            await record.update_from_dict(item.model_dump(exclude_unset=True))
            await record.save()
        await record.fetch_related('project', 'server', 'server__group', 'server__group__country')
        return Out.model_validate(record)


project_account_crud = CRUD()
