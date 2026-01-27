from uuid import UUID
from fastapi import HTTPException
import secrets
import string

from app.models.server import ServerAccount
from app.models.user import UserInfo
from app.schemas.server.account import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time
from app.core.tools import aes_encrypt, aes_decrypt


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

    # 获取账号并解密密码
    async def get_with_password(self, id: UUID) -> Out:
        """
        获取服务器账号，返回固定密码
        - 统一使用固定账号密码：cqrxy:Zpaily88
        """
        res = await ServerAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='账号不存在')
        await res.fetch_related('user')
        
        result = Out.model_validate(res)
        
        # 使用固定密码
        result.password = "Zpaily88"
        
        return result

    # 条件查询
    async def get_multi(self,
                        username: str | None = None,
                        user_id: UUID | None = None,
                        proxy_type: str | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None,
                        is_admin: bool = False
                        ) -> OutList:
        query = ServerAccount.all()
        if username:
            query = query.filter(username__icontains=username)
        if user_id:
            query = query.filter(user_id=user_id)
        
        # 根据代理类型过滤（基于端口范围）
        if proxy_type:
            from app.models.xui import XuiInbound
            
            if proxy_type == 'HTTP':
                # HTTP 类型：端口在 21999-22999 之间
                # 使用子查询优化，避免 N+1 问题
                http_account_ids = await XuiInbound.filter(
                    listen_port__gte=21999,
                    listen_port__lte=22999
                ).values_list('accounts__id', flat=True)
                
                if http_account_ids:
                    query = query.filter(id__in=list(http_account_ids))
                else:
                    # 如果没有找到任何HTTP账号，返回空结果
                    query = query.filter(id__in=[])
                    
            elif proxy_type == 'SOCKS5':
                # SOCKS5 类型：端口在 31999-32999 之间
                socks5_account_ids = await XuiInbound.filter(
                    listen_port__gte=31999,
                    listen_port__lte=32999
                ).values_list('accounts__id', flat=True)
                
                if socks5_account_ids:
                    query = query.filter(id__in=list(socks5_account_ids))
                else:
                    # 如果没有找到任何SOCKS5账号，返回空结果
                    query = query.filter(id__in=[])
        
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
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = []
        
        # 预加载所有账号的入站信息，用于判断代理类型
        from app.models.xui import XuiInbound
        account_ids = [str(obj.id) for obj in res]
        
        # 一次性查询所有相关的入站（使用 prefetch_related 优化）
        inbounds_with_accounts = await XuiInbound.filter(
            accounts__id__in=account_ids
        ).prefetch_related('accounts', 'server').all()
        
        # 构建账号ID到入站信息的映射（避免重复查询）
        account_inbound_map = {}
        for inbound in inbounds_with_accounts:
            # 使用 prefetch_related 已经加载的数据，不会触发额外查询
            for account in inbound.accounts:
                account_id = str(account.id)
                if account_id not in account_inbound_map:
                    account_inbound_map[account_id] = []
                account_inbound_map[account_id].append({
                    'port': inbound.listen_port,
                    'host': inbound.listen_host,
                    'server': inbound.server
                })
        
        # 如果是管理员，返回固定密码
        for obj in res:
            item = Out.model_validate(obj)
            if is_admin:
                # 使用固定密码
                item.password = "Zpaily88"
            
            # 添加代理类型和入站信息
            account_id = str(obj.id)
            inbounds = account_inbound_map.get(account_id, [])
            
            # 根据端口判断代理类型
            proxy_types = set()
            inbound_host = None
            inbound_port = None
            
            for inbound_info in inbounds:
                port = inbound_info['port']
                if 21999 <= port <= 22999:
                    proxy_types.add('HTTP')
                    # 优先使用 HTTP 入站信息
                    if not inbound_host or 'HTTP' not in item.proxy_type if item.proxy_type else True:
                        inbound_host = inbound_info['host']
                        inbound_port = port
                elif 31999 <= port <= 32999:
                    proxy_types.add('SOCKS5')
                    # 如果没有 HTTP，使用 SOCKS5 入站信息
                    if not inbound_host:
                        inbound_host = inbound_info['host']
                        inbound_port = port
            
            # 如果有多个类型，用逗号分隔；如果没有，显示为空
            item.proxy_type = ','.join(sorted(proxy_types)) if proxy_types else None
            item.inbound_host = inbound_host
            item.inbound_port = inbound_port
            
            items.append(item)
        
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

    # 为用户生成服务器账号
    async def generate_account(self, user_id: UUID) -> Out:
        """
        为用户生成服务器账号（SOCKS5代理账号）
        - 如果用户已有账号，返回现有账号（使用固定密码）
        - 如果没有，创建新账号
        - 用户名格式：user_{user_id前8位}，如果重复则添加随机后缀
        - 密码：统一使用固定密码 Zpaily88
        """
        # 检查用户是否存在
        user = await UserInfo.get_or_none(id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail='用户不存在')
        
        # 检查用户是否已有服务器账号
        existing_account = await ServerAccount.get_or_none(user_id=user_id)
        if existing_account:
            await existing_account.fetch_related('user')
            result = Out.model_validate(existing_account)
            # 使用固定密码
            result.password = "Zpaily88"
            return result
        
        # 生成用户名：user_{user_id前8位}
        base_username = f"user_{str(user_id).replace('-', '')[:8]}"
        username = base_username
        
        # 检查用户名是否重复，如果重复则添加随机后缀
        attempt = 0
        while await ServerAccount.get_or_none(username=username):
            attempt += 1
            # 添加4位随机字符作为后缀
            random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
            username = f"{base_username}_{random_suffix}"
            
            # 防止无限循环
            if attempt > 10:
                raise HTTPException(status_code=500, detail='生成用户名失败，请重试')
        
        # 使用固定密码
        raw_password = "Zpaily88"
        
        # 使用AES加密密码（每个用户不同的密钥）
        encrypted_password = aes_encrypt(raw_password, str(user_id))
        
        # 创建服务器账号
        account = await ServerAccount.create(
            username=username,
            password=encrypted_password,
            user_id=user_id
        )
        
        await account.fetch_related('user')
        
        # 返回时直接在 password 字段返回明文密码
        result = Out.model_validate(account)
        result.password = raw_password  # 固定密码
        
        return result


server_account_crud = CRUD()
