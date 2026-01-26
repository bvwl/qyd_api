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
        获取服务器账号并解密密码
        - 仅用于需要查看密码的场景
        - 直接在 password 字段返回解密后的明文
        """
        res = await ServerAccount.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='账号不存在')
        await res.fetch_related('user')
        
        result = Out.model_validate(res)
        
        # 解密密码并直接替换 password 字段
        if res.user_id:
            try:
                decrypted_password = aes_decrypt(res.password, str(res.user_id))
                result.password = decrypted_password  # 直接替换 password 字段
            except Exception as e:
                raise HTTPException(status_code=500, detail=f'密码解密失败: {str(e)}')
        
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
                # 查找符合条件的账号ID
                http_inbounds = await XuiInbound.filter(
                    listen_port__gte=21999,
                    listen_port__lte=22999
                ).prefetch_related('accounts')
                
                http_account_ids = set()
                for inbound in http_inbounds:
                    accounts = await inbound.accounts.all()
                    http_account_ids.update([str(acc.id) for acc in accounts])
                
                if http_account_ids:
                    query = query.filter(id__in=list(http_account_ids))
                else:
                    # 如果没有找到任何HTTP账号，返回空结果
                    query = query.filter(id__in=[])
                    
            elif proxy_type == 'SOCKS5':
                # SOCKS5 类型：端口在 31999-32999 之间
                socks5_inbounds = await XuiInbound.filter(
                    listen_port__gte=31999,
                    listen_port__lte=32999
                ).prefetch_related('accounts')
                
                socks5_account_ids = set()
                for inbound in socks5_inbounds:
                    accounts = await inbound.accounts.all()
                    socks5_account_ids.update([str(acc.id) for acc in accounts])
                
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
        
        # 查询所有相关的入站
        inbounds_with_accounts = await XuiInbound.filter(
            accounts__id__in=account_ids
        ).prefetch_related('accounts')
        
        # 构建账号ID到端口的映射
        account_port_map = {}
        for inbound in inbounds_with_accounts:
            accounts = await inbound.accounts.all()
            for account in accounts:
                account_id = str(account.id)
                if account_id not in account_port_map:
                    account_port_map[account_id] = []
                account_port_map[account_id].append(inbound.listen_port)
        
        # 如果是管理员，自动解密所有密码并替换 password 字段
        for obj in res:
            item = Out.model_validate(obj)
            if is_admin and obj.user_id:
                try:
                    decrypted_password = aes_decrypt(obj.password, str(obj.user_id))
                    item.password = decrypted_password  # 直接替换 password 字段
                except Exception:
                    # 解密失败，保持原密文
                    pass
            
            # 添加代理类型字段
            account_id = str(obj.id)
            ports = account_port_map.get(account_id, [])
            
            # 根据端口判断代理类型
            proxy_types = set()
            for port in ports:
                if 21999 <= port <= 22999:
                    proxy_types.add('HTTP')
                elif 31999 <= port <= 32999:
                    proxy_types.add('SOCKS5')
            
            # 如果有多个类型，用逗号分隔；如果没有，显示为空
            item.proxy_type = ','.join(sorted(proxy_types)) if proxy_types else None
            
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
        - 如果用户已有账号，返回现有账号（包含解密后的密码）
        - 如果没有，创建新账号
        - 用户名格式：user_{user_id前8位}，如果重复则添加随机后缀
        - 密码：随机生成12位强密码
        - 加密方式：AES-CBC，key=MD5(user_id+"9527")，iv=MD5("9527"+user_id)前16位
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
            # 解密密码并直接替换 password 字段
            try:
                decrypted_password = aes_decrypt(existing_account.password, str(user_id))
                result.password = decrypted_password  # 直接替换 password 字段
            except Exception:
                # 解密失败，保持原密文
                pass
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
        
        # 生成随机密码：12位，包含大小写字母和数字
        password_chars = string.ascii_letters + string.digits
        raw_password = ''.join(secrets.choice(password_chars) for _ in range(12))
        
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
        result.password = raw_password  # 直接替换 password 字段为明文
        
        return result


server_account_crud = CRUD()
