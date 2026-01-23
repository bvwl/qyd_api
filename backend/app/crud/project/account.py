from uuid import UUID
from datetime import datetime
from fastapi import HTTPException

from app.models.project import ProjectAccount
from app.schemas.project.account import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        # 处理外键字段
        data = item.model_dump(exclude={'project_id', 'server_id', 'balance', 'variable', 'balance_history'})
        if item.project_id:
            data['project_id'] = item.project_id
        if item.server_id:
            data['server_id'] = item.server_id
        
        # 余额字段：如果传入则使用，否则使用默认值0
        data['balance'] = item.balance if item.balance is not None else 0
        data['variable'] = 0  # 创建时变动余额为0
        data['balance_history'] = {}  # 创建时历史为空

        res = await ProjectAccount.create(**data)
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        await res.fetch_related('project', 'server')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID) -> Out:
        res = await ProjectAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('project', 'server')
        return Out.model_validate(res)

    # 条件查询
    async def get_multi(self,
                        account: str | None = None,
                        status: int | None = None,
                        account_type: int | None = None,
                        project_id: UUID | None = None,
                        server_id: UUID | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None,
                        user_project_ids: list[str] | None = None
                        ) -> OutList:
        query = ProjectAccount.all()
        
        # 数据权限过滤：如果指定了user_project_ids，只返回这些项目的账号
        if user_project_ids is not None:
            if len(user_project_ids) == 0:
                # 如果用户没有关联任何项目，返回空列表
                return OutList(message='成功', count=0, num=0, items=[])
            query = query.filter(project_id__in=user_project_ids)
        
        if account:
            query = query.filter(account__icontains=account)
        if status is not None:
            query = query.filter(status=status)
        if account_type is not None:
            query = query.filter(account_type=account_type)
        if project_id:
            query = query.filter(project_id=project_id)
        if server_id:
            query = query.filter(server_id=server_id)
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
        res = await query.prefetch_related('project', 'server')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = [Out.model_validate(obj) for obj in res]
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await ProjectAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        update_data = item.model_dump(exclude_unset=True, exclude={'balance', 'variable', 'balance_history'})
        
        # 如果传入了余额，需要计算变动余额和更新历史
        if item.balance is not None:
            new_balance = item.balance
            
            # 获取当前日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 初始化 balance_history
            if res.balance_history is None:
                res.balance_history = {}
            
            # 实时更新当天的余额记录（覆盖）
            res.balance_history[today] = float(new_balance)
            
            # 按日期排序并保留最近7条记录
            sorted_data = dict(sorted(res.balance_history.items(), key=lambda x: x[0], reverse=True))
            res.balance_history = dict(list(sorted_data.items())[:7])
            
            # 实时计算变动余额：当前余额 - 昨天的余额
            if len(res.balance_history) >= 2:
                dates = list(res.balance_history.keys())
                today_balance = res.balance_history[dates[0]]  # 今天的余额（最新）
                yesterday_balance = res.balance_history[dates[1]]  # 昨天的余额
                update_data['variable'] = today_balance - yesterday_balance
            else:
                update_data['variable'] = 0
            
            update_data['balance'] = new_balance
            update_data['balance_history'] = res.balance_history
        
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')

        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('project', 'server')
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
        # 获取当前日期
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 查询现有记录
        existing = await ProjectAccount.get_or_none(
            account=item.account,
            project_id=item.project_id
        )
        
        if existing:
            # 如果记录存在，更新余额
            if item.balance is not None:
                new_balance = item.balance
                
                # 初始化 balance_history
                if existing.balance_history is None:
                    existing.balance_history = {}
                
                # 实时更新当天的余额记录（覆盖）
                existing.balance_history[today] = float(new_balance)
                
                # 按日期排序并保留最近7条记录
                sorted_data = dict(sorted(existing.balance_history.items(), key=lambda x: x[0], reverse=True))
                existing.balance_history = dict(list(sorted_data.items())[:7])
                
                # 实时计算变动余额：当前余额 - 昨天的余额
                if len(existing.balance_history) >= 2:
                    dates = list(existing.balance_history.keys())
                    today_balance = existing.balance_history[dates[0]]  # 今天的余额（最新）
                    yesterday_balance = existing.balance_history[dates[1]]  # 昨天的余额
                    existing.variable = today_balance - yesterday_balance
                else:
                    existing.variable = 0
                
                existing.balance = new_balance
                await existing.save()
            
            await existing.fetch_related('project', 'server')
            return Out.model_validate(existing)
        else:
            # 如果记录不存在，创建新记录
            return await self.create(item)


project_account_crud = CRUD()
