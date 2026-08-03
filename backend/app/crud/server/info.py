from uuid import UUID
from fastapi import HTTPException

from app.models.server import ServerInfo
from app.schemas.server.info import Create, Update, Out, OutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time
from app.core.tools import aes_encrypt, aes_decrypt


class CRUD:
    async def _generate_proxy_url(self, server: ServerInfo, current_user: dict | None = None) -> tuple[str, str]:
        """
        生成代理URL和代理类型，使用固定的服务器账号密码
        
        Args:
            server: 服务器信息对象
            current_user: JWT 用户信息字典（已不使用，保留参数以兼容）
        
        Returns:
            tuple[str, str]: (proxy_url, proxy_type)
        """
        if server.port is None:
            return "", ""
        
        # 根据端口范围判断代理类型
        port = server.port
        if 21999 < port < 29999:
            proxy_type = "http"
            protocol = "http"
        elif 31999 < port < 39999:
            proxy_type = "socks5"
            protocol = "socks5"
        else:
            # 默认为 socks5
            proxy_type = "socks5"
            protocol = "socks5"
        
        # 使用固定账号密码
        username = "cqrxy"
        password = "Zpaily88"
        
        # 生成代理URL
        host = server.domain if server.domain else server.host
        proxy_url = f"{protocol}://{username}:{password}@{host}:{server.port}"
        
        return proxy_url, proxy_type
    
    # 创建
    async def create(self, item: Create, current_user: dict | None = None) -> Out:
        is_exist = await ServerInfo.get_or_none(host=item.host)
        if is_exist:
            raise HTTPException(status_code=400, detail='服务器地址已存在')
        
        # 处理密码加密
        data = item.model_dump()
        if data.get('password'):
            # 使用 AES 加密密码，key=MD5(host+"9527"), iv=MD5("9527"+host)前16位
            data['password'] = aes_encrypt(data['password'], item.host)
        
        res = await ServerInfo.create(**data)
        if not res:
            raise HTTPException(status_code=500, detail='创建失败')
        await res.fetch_related('group', 'group__country')
        
        result = Out.model_validate(res)
        
        # 生成 proxy_url 和 proxy_type
        result.proxy_url, result.proxy_type = await self._generate_proxy_url(res, current_user)
        
        return result

    # 查询
    async def get(self, id: UUID, is_admin: bool = False, current_user: dict | None = None) -> Out:
        res = await ServerInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        await res.fetch_related('group', 'group__country')
        
        item = Out.model_validate(res)
        
        # 如果是管理员，解密密码
        if is_admin and res.password and res.host:
            try:
                decrypted_password = aes_decrypt(res.password, res.host)
                item.password = decrypted_password
            except Exception:
                # 解密失败，保持原密文
                pass
        
        # 生成 proxy_url 和 proxy_type
        item.proxy_url, item.proxy_type = await self._generate_proxy_url(res, current_user)
        
        return item

    # 条件查询
    async def get_multi(self,
                        host: str | None = None,
                        domain: str | None = None,
                        port: int | None = None,
                        proxy_type: str | None = None,
                        group_id: UUID | None = None,
                        page: int = 1,
                        limit: int = 10,
                        res_count: bool = False,
                        order_by: str = '-create_time',
                        create_time_start: str | int | None = None,
                        create_time_end: str | int | None = None,
                        update_time_start: str | int | None = None,
                        update_time_end: str | int | None = None,
                        is_admin: bool = False,
                        current_user: dict | None = None
                        ) -> OutList:
        query = ServerInfo.all()
        if host:
            query = query.filter(host__icontains=host)
        if domain:
            query = query.filter(domain__icontains=domain)
        if port is not None:
            query = query.filter(port=port)
        if group_id is not None:
            query = query.filter(group_id=group_id)
        
        # 根据代理类型过滤
        if proxy_type:
            if proxy_type.lower() == 'http':
                # HTTP 代理端口范围：22000-29999
                query = query.filter(port__gte=22000, port__lt=30000)
            elif proxy_type.lower() == 'socks5':
                # SOCKS5 代理端口范围：32000-39999
                query = query.filter(port__gte=32000, port__lt=40000)
        
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
        
        # 使用 prefetch_related 预加载关联数据（包括嵌套关联）
        res = await query.prefetch_related('group', 'group__country')
        
        if not res:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        num = len(res)
        items = []
        
        # 如果是管理员，解密所有密码
        for obj in res:
            item = Out.model_validate(obj)
            if is_admin and obj.password and obj.host:
                try:
                    decrypted_password = aes_decrypt(obj.password, obj.host)
                    item.password = decrypted_password
                except Exception:
                    # 解密失败，保持原密文
                    pass
            
            # 生成 proxy_url 和 proxy_type
            item.proxy_url, item.proxy_type = await self._generate_proxy_url(obj, current_user)
            
            items.append(item)
        
        return OutList(message='成功', count=count, num=num, items=items)

    # 更新
    async def update(self, id: UUID, item: Update, is_admin: bool = False, current_user: dict | None = None) -> Out:
        res = await ServerInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        if 'host' in update_data:
            new_host = update_data['host']
            is_exist = await ServerInfo.get_or_none(host=new_host)
            if is_exist and is_exist.id != id:
                raise HTTPException(status_code=400, detail=f'服务器地址 {new_host} 已被占用')
        
        # 如果更新了密码，需要加密
        if 'password' in update_data and update_data['password']:
            # 使用新的 host（如果有）或原来的 host
            host_for_encrypt = update_data.get('host', res.host)
            update_data['password'] = aes_encrypt(update_data['password'], host_for_encrypt)

        await res.update_from_dict(update_data)
        await res.save()
        await res.fetch_related('group', 'group__country')
        
        result = Out.model_validate(res)
        
        # 如果是管理员，解密密码
        if is_admin and res.password and res.host:
            try:
                decrypted_password = aes_decrypt(res.password, res.host)
                result.password = decrypted_password
            except Exception:
                # 解密失败，保持原密文
                pass
        
        # 生成 proxy_url 和 proxy_type
        result.proxy_url, result.proxy_type = await self._generate_proxy_url(res, current_user)
        
        return result

    # 删除
    async def delete(self, id: UUID) -> BaseOut:
        res = await ServerInfo.get_or_none(id=id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')

        # 删除代理节点时只解除关联，保留项目账号和邮箱业务数据。
        # 显式置空可兼容尚未执行 SET NULL 外键迁移的部署环境。
        from tortoise.transactions import in_transaction
        from app.models.mail import EmailInfo
        from app.models.project import ProjectAccount

        async with in_transaction(connection_name="default") as connection:
            await ProjectAccount.filter(server_id=id).using_db(connection).update(server_id=None)
            await EmailInfo.filter(server_id=id).using_db(connection).update(server_id=None)
            await ServerInfo.filter(id=id).using_db(connection).delete()

        return BaseOut(message='成功', count=1)

    # 创建或更新
    async def upsert(self, item: Create, current_user: dict | None = None) -> Out:
        record, created = await ServerInfo.get_or_create(
            defaults=item.model_dump(),
            host=item.host
        )
        if not created:
            await record.update_from_dict(item.model_dump(exclude_unset=True))
            await record.save()
        await record.fetch_related('group', 'group__country')
        
        result = Out.model_validate(record)
        
        # 生成 proxy_url 和 proxy_type
        result.proxy_url, result.proxy_type = await self._generate_proxy_url(record, current_user)
        
        return result


server_info_crud = CRUD()
