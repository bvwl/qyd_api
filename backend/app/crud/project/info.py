from uuid import UUID
from fastapi import HTTPException

from app.models.project import ProjectInfo
from app.schemas.project.info import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    # 创建
    async def create(self, item: dict | Create) -> Out:
        from app.models.user import UserInfo
        
        # 统一处理为字典
        if isinstance(item, dict):
            data = item.copy()
            name = data.get('name')
        else:
            data = item.model_dump()
            name = item.name
        
        is_exist = await ProjectInfo.get_or_none(name=name)
        if is_exist:
            raise HTTPException(status_code=400, detail='项目名称已存在')
        
        # 分离关联字段
        user_ids = data.pop('user_ids', None)
        
        res = await ProjectInfo.create(**data)
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        
        # 处理多对多关系
        if user_ids:
            # 获取UserInfo对象
            users = await UserInfo.filter(id__in=user_ids).all()
            if users:
                await res.users.add(*users)
        
        await res.fetch_related('users')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await ProjectInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('users')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        name: str | None = None,
                        status: int | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None,
                        user_id: UUID | None = None,
                        user_project_ids: list[str] | None = None
                        ) -> OutList:
        query = ProjectInfo.all()
        
        # 数据权限过滤：如果指定了user_id，只返回该用户关联的项目
        if user_id:
            query = query.filter(users__id=user_id)
        
        # 数据权限过滤：如果指定了user_project_ids，只返回这些项目
        if user_project_ids is not None:
            if len(user_project_ids) == 0:
                # 如果用户没有关联任何项目，返回空列表
                return OutList(message='成功', count=0, num=0, items=[])
            query = query.filter(id__in=user_project_ids)
        
        if name:
            query = query.filter(name__icontains=name)
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
        
        # 使用 prefetch_related 预加载关联数据
        res = await query.prefetch_related('users')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = [Out.model_validate(item) for item in res]
        return OutList(message='成功', count=count, num=num, items=items)
    
    # 获取计数（用于API层）
    async def get_count(self,
                        name: str | None = None,
                        status: int | None = None,
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None,
                        user_id: UUID | None = None,
                        user_project_ids: list[str] | None = None
                        ) -> int:
        query = ProjectInfo.all()
        
        # 数据权限过滤
        if user_id:
            query = query.filter(users__id=user_id)
        
        # 数据权限过滤：如果指定了user_project_ids，只返回这些项目
        if user_project_ids is not None:
            if len(user_project_ids) == 0:
                return 0
            query = query.filter(id__in=user_project_ids)
        
        if name:
            query = query.filter(name__icontains=name)
        if status is not None:
            query = query.filter(status=status)
        if create_time_start:
            query = query.filter(create_time__gte=create_time_start)
        if create_time_end:
            query = query.filter(create_time__lte=create_time_end)
        if update_time_start:
            query = query.filter(update_time__gte=update_time_start)
        if update_time_end:
            query = query.filter(update_time__lte=update_time_end)
        return await query.count()

    # 更新
    async def update(self, id: UUID, item: dict | Update) -> Out:
        from app.models.user import UserInfo
        
        res = await ProjectInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        # 统一处理为字典
        if isinstance(item, dict):
            update_data = item.copy()
        else:
            update_data = item.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        
        # 检查名称唯一性
        if 'name' in update_data:
            new_name = update_data['name']
            is_exist = await ProjectInfo.get_or_none(name=new_name)
            if is_exist and is_exist.id != id:
                raise HTTPException(status_code=400, detail=f'项目名称 {new_name} 已被占用')
        
        # 分离关联字段
        user_ids = update_data.pop('user_ids', None)
        
        # 更新基本字段
        if update_data:
            await res.update_from_dict(update_data)
            await res.save()
        
        # 处理多对多关系
        if user_ids is not None:
            await res.users.clear()
            if user_ids:
                # 获取UserInfo对象
                users = await UserInfo.filter(id__in=user_ids).all()
                if users:
                    await res.users.add(*users)
        
        await res.fetch_related('users')
        return Out.model_validate(res)

    # 删除
    async def delete(self, id: UUID) -> bool:
        res = await ProjectInfo.get_or_none(id=id)
        if not res:
            return False
        await res.delete()
        return True

    # 创建或更新
    async def upsert(self, item: Create) -> Out:
        from app.models.user import UserInfo
        
        # 分离关联字段
        data = item.model_dump()
        user_ids = data.pop('user_ids', None)
        
        record, created = await ProjectInfo.get_or_create(
            defaults=data,
            name=item.name
        )
        
        if not created:
            await record.update_from_dict(data)
            await record.save()
        
        # 处理多对多关系
        if user_ids is not None:
            await record.users.clear()
            if user_ids:
                # 获取UserInfo对象
                users = await UserInfo.filter(id__in=user_ids).all()
                if users:
                    await record.users.add(*users)
        
        await record.fetch_related('users')
        return Out.model_validate(record)


project_info_crud = CRUD()
