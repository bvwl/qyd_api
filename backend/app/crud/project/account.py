from uuid import UUID
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException

from app.models.project import ProjectAccount, ProjectInfo
from app.schemas.project.account import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time
from app.utils.project_crypto import (
    encrypt_sensitive_fields, 
    decrypt_sensitive_fields, 
    check_user_can_decrypt
)


class CRUD:
    # 创建
    async def create(self, item: Create) -> Out:
        # 如果提供了 host，查询对应的 server_id
        if item.host:
            from app.models.server import ServerInfo
            server = await ServerInfo.get_or_none(host=item.host)
            if server:
                # 找到服务器，使用其 ID
                item.server_id = server.id
            else:
                # 未找到服务器，可以选择：
                # 1. 抛出错误（严格模式）
                # 2. 忽略（宽松模式）
                # 这里使用宽松模式，记录日志但不中断
                print(f"⚠️  未找到 host={item.host} 的服务器，server_id 将为空")
        
        # 过滤掉None值和需要自动计算的字段，以及 host（不存储到数据库）
        filtered_item = {
            k: v for k, v in item.model_dump().items() 
            if v is not None and k not in ['variable', 'balance_history', 'host']
        }
        
        # 检查项目是否存在
        project = await ProjectInfo.get_or_none(id=item.project_id)
        if not project:
            raise HTTPException(status_code=404, detail='项目不存在')
        
        # 获取账号（用于加密）
        account = item.account
        
        # 如果有 data 字段，加密敏感字段
        if 'data' in filtered_item and filtered_item['data']:
            filtered_item['data'] = encrypt_sensitive_fields(filtered_item['data'], account)
        
        # password 字段不加密，直接存储明文
        
        # 先创建记录
        res = await ProjectAccount.create(**filtered_item)
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        
        # 如果传入了 balance，需要更新 variable 和 balance_history
        if 'balance' in filtered_item:
            new_balance = Decimal(str(filtered_item['balance']))
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 初始化 balance_history（首次创建只有今天的记录）
            balance_history = {today: float(new_balance.quantize(Decimal('0.000001')))}
            
            # 首次创建，variable 等于 balance（从0增加到balance）
            variable = new_balance.quantize(Decimal('0.01'))
            
            # 使用 update 方法更新字段
            await ProjectAccount.filter(id=res.id).update(
                balance_history=balance_history,
                variable=variable
            )
            
            # 重新查询
            res = await ProjectAccount.get(id=res.id)
        
        await res.fetch_related('project', 'server')
        return Out.model_validate(res)

    # 查询
    async def get(self, id: UUID, user_id: str | None = None, user_roles: list[str] | None = None) -> Out:
        """
        获取项目账号
        
        :param id: 账号ID
        :param user_id: 当前用户ID（用于权限判断）
        :param user_roles: 当前用户角色列表（用于权限判断）
        :return: 账号信息（敏感字段根据权限决定是否解密）
        """
        res = await ProjectAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('project', 'server')
        
        # 获取项目所属用户ID列表
        project = res.project
        await project.fetch_related('users')
        project_user_ids = [str(user.id) for user in project.users]
        
        # 转换为 Pydantic 模型
        result = Out.model_validate(res)
        
        # 如果提供了用户信息，根据权限决定是否解密
        if user_id and user_roles:
            can_decrypt = check_user_can_decrypt(user_id, user_roles, project_user_ids)
            if can_decrypt:
                # 有权限，解密敏感字段
                # 解密 data 字段
                if result.data:
                    try:
                        result.data = decrypt_sensitive_fields(result.data, res.account)
                    except Exception as e:
                        # 解密失败，保持加密状态
                        print(f"解密 data 失败: {e}")
                
                # password 字段不解密，直接返回明文
            # 没有权限，保持加密状态（不做任何处理）
        
        return result

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
                        user_project_ids: list[str] | None = None,
                        user_id: str | None = None,
                        user_roles: list[str] | None = None
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
        res = await query.prefetch_related('project', 'project__users', 'server')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = []
        
        # 处理每个账号的敏感字段
        for obj in res:
            item = Out.model_validate(obj)
            
            # 如果提供了用户信息，根据权限决定是否解密
            if user_id and user_roles:
                # 获取项目所属用户ID列表
                project_user_ids_list = [str(user.id) for user in obj.project.users]
                
                can_decrypt = check_user_can_decrypt(user_id, user_roles, project_user_ids_list)
                if can_decrypt:
                    # 有权限，解密敏感字段
                    # 解密 data 字段
                    if item.data:
                        try:
                            item.data = decrypt_sensitive_fields(item.data, obj.account)
                        except Exception as e:
                            # 解密失败，保持加密状态
                            print(f"解密 data 失败: {e}")
                    
                    # password 字段不解密，直接返回明文
                # 没有权限，保持加密状态（不做任何处理）
            
            items.append(item)
        
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update) -> Out:
        res = await ProjectAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        # 如果提供了 host，查询对应的 server_id
        if item.host:
            from app.models.server import ServerInfo
            server = await ServerInfo.get_or_none(host=item.host)
            if server:
                # 找到服务器，使用其 ID
                item.server_id = server.id
            else:
                # 未找到服务器
                print(f"⚠️  未找到 host={item.host} 的服务器，server_id 将保持不变")
        
        # 获取账号（用于加密）
        account = res.account
        
        # 过滤掉 host 字段（不存储到数据库）
        update_data = item.model_dump(exclude_unset=True, exclude={'balance', 'variable', 'balance_history', 'host'})
        
        # 如果更新了 data 字段，加密敏感字段
        if 'data' in update_data and update_data['data']:
            update_data['data'] = encrypt_sensitive_fields(update_data['data'], account)
        
        # password 字段不加密，直接存储明文
        
        # 如果传入了余额，需要计算变动余额和更新历史
        if item.balance is not None:
            new_balance = item.balance
            
            # 获取当前日期
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 初始化 balance_history
            if res.balance_history is None:
                res.balance_history = {}
            
            # 实时更新当天的余额记录（覆盖，保留6位小数）
            res.balance_history[today] = float(new_balance.quantize(Decimal('0.000001')))
            
            # 按日期排序并保留最近7条记录
            sorted_data = dict(sorted(res.balance_history.items(), key=lambda x: x[0], reverse=True))
            res.balance_history = dict(list(sorted_data.items())[:7])
            
            # 实时计算变动余额：当前余额 - 昨天的余额
            if len(res.balance_history) >= 2:
                dates = list(res.balance_history.keys())
                today_balance = Decimal(str(res.balance_history[dates[0]]))  # 今天的余额（最新）
                yesterday_balance = Decimal(str(res.balance_history[dates[1]]))  # 昨天的余额
                update_data['variable'] = (today_balance - yesterday_balance).quantize(Decimal('0.01'))
            else:
                # 只有今天的记录，variable 等于 balance（从0增加到balance）
                update_data['variable'] = new_balance.quantize(Decimal('0.01'))
            
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
        """
        创建或更新项目账号
        - 如果记录存在，只更新传入的非空字段（类似PUT）
        - 如果记录不存在，创建新记录
        """
        # 如果提供了 host，查询对应的 server_id
        if item.host:
            from app.models.server import ServerInfo
            server = await ServerInfo.get_or_none(host=item.host)
            if server:
                # 找到服务器，使用其 ID
                item.server_id = server.id
            else:
                # 未找到服务器
                print(f"⚠️  未找到 host={item.host} 的服务器，server_id 将为空")
        
        # 获取项目信息（验证项目是否存在）
        project = await ProjectInfo.get_or_none(id=item.project_id)
        if not project:
            raise HTTPException(status_code=404, detail='项目不存在')
        
        # 获取账号（用于加密）
        account = item.account
        
        # 获取当前日期
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 查询现有记录
        existing = await ProjectAccount.get_or_none(
            account=item.account,
            project_id=item.project_id
        )
        
        if existing:
            # 如果记录存在，只更新非空字段
            # 使用 exclude_unset=True 排除未设置的字段
            # 使用 exclude_none=True 排除值为None的字段
            # 排除 host 字段（不存储到数据库）
            update_data = item.model_dump(
                exclude_unset=True,
                exclude_none=True,
                exclude={'balance', 'variable', 'balance_history', 'project_id', 'account', 'host'}
            )
            
            # 如果更新了 data 字段，加密敏感字段
            if 'data' in update_data and update_data['data']:
                update_data['data'] = encrypt_sensitive_fields(update_data['data'], account)
            
            # password 字段不加密，直接存储明文
            
            # 如果传入了余额，需要计算变动余额和更新历史
            if item.balance is not None:
                new_balance = item.balance
                
                # 初始化 balance_history
                if existing.balance_history is None:
                    existing.balance_history = {}
                
                # 实时更新当天的余额记录（覆盖，保留6位小数）
                existing.balance_history[today] = float(new_balance.quantize(Decimal('0.000001')))
                
                # 按日期排序并保留最近7条记录
                sorted_data = dict(sorted(existing.balance_history.items(), key=lambda x: x[0], reverse=True))
                existing.balance_history = dict(list(sorted_data.items())[:7])
                
                # 实时计算变动余额：当前余额 - 昨天的余额
                if len(existing.balance_history) >= 2:
                    dates = list(existing.balance_history.keys())
                    today_balance = Decimal(str(existing.balance_history[dates[0]]))  # 今天的余额（最新）
                    yesterday_balance = Decimal(str(existing.balance_history[dates[1]]))  # 昨天的余额
                    update_data['variable'] = (today_balance - yesterday_balance).quantize(Decimal('0.01'))
                else:
                    # 只有今天的记录，variable 等于 balance（从0增加到balance）
                    update_data['variable'] = new_balance.quantize(Decimal('0.01'))
                
                update_data['balance'] = new_balance
                update_data['balance_history'] = existing.balance_history
            
            # 只有在有更新数据时才执行更新
            if update_data:
                await existing.update_from_dict(update_data)
                await existing.save()
            
            await existing.fetch_related('project', 'server')
            return Out.model_validate(existing)
        else:
            # 如果记录不存在，创建新记录
            return await self.create(item)

    # 统计
    async def get_stats(
        self,
        project_id: UUID,
        account: str | None = None,
        status: int | None = None,
        account_type: int | None = None,
        create_time_start: datetime | None = None,
        create_time_end: datetime | None = None,
        update_time_start: datetime | None = None,
        update_time_end: datetime | None = None,
    ) -> dict:
        """
        统计项目账号的余额和变动数据
        使用数据库聚合函数，一次查询获取所有统计数据
        """
        from tortoise.functions import Max, Min, Avg, Sum
        
        # 构建查询条件
        query = ProjectAccount.filter(project_id=project_id)
        
        if account:
            query = query.filter(account__icontains=account)
        if status is not None:
            query = query.filter(status=status)
        if account_type is not None:
            query = query.filter(account_type=account_type)
        if create_time_start:
            query = query.filter(create_time__gte=create_time_start)
        if create_time_end:
            query = query.filter(create_time__lte=create_time_end)
        if update_time_start:
            query = query.filter(update_time__gte=update_time_start)
        if update_time_end:
            query = query.filter(update_time__lte=update_time_end)
        
        # 先获取总数
        total_count = await query.count()
        
        # 如果没有数据，直接返回默认值
        if total_count == 0:
            return {
                "total_count": 0,
                "max_balance": 0,
                "min_balance": 0,
                "avg_balance": 0,
                "sum_balance": 0,
                "max_variable": 0,
                "min_variable": 0,
                "avg_variable": 0,
                "sum_variable": 0,
            }
        
        # 使用聚合函数获取统计数据
        stats = await query.annotate(
            max_balance=Max('balance'),
            min_balance=Min('balance'),
            avg_balance=Avg('balance'),
            sum_balance=Sum('balance'),
            max_variable=Max('variable'),
            min_variable=Min('variable'),
            avg_variable=Avg('variable'),
            sum_variable=Sum('variable'),
        ).values(
            'max_balance',
            'min_balance',
            'avg_balance',
            'sum_balance',
            'max_variable',
            'min_variable',
            'avg_variable',
            'sum_variable',
        )
        
        # stats 是一个列表，取第一个元素
        if stats and len(stats) > 0:
            result = stats[0]
            result['total_count'] = total_count
            return result
        
        # 如果没有统计数据，返回默认值
        return {
            "total_count": total_count,
            "max_balance": 0,
            "min_balance": 0,
            "avg_balance": 0,
            "sum_balance": 0,
            "max_variable": 0,
            "min_variable": 0,
            "avg_variable": 0,
            "sum_variable": 0,
        }


project_account_crud = CRUD()
