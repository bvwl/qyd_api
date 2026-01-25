"""
XUI 服务器 CRUD
"""
from uuid import UUID
from fastapi import HTTPException

from app.models.xui import XuiServer
from app.schemas.xui.server import XuiServerCreate, XuiServerUpdate, XuiServerOut, XuiServerOutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time
from app.core.tools import aes_encrypt, aes_decrypt
from app.utils.logs import getLogger

logger = getLogger('app')


class XuiServerCRUD:
    """XUI 服务器 CRUD 操作"""
    
    async def create(self, item: XuiServerCreate, is_admin: bool = False) -> XuiServerOut:
        """创建 XUI 服务器"""
        # 检查主机是否已存在
        is_exist = await XuiServer.get_or_none(host=item.host)
        if is_exist:
            raise HTTPException(status_code=400, detail=f'服务器地址 {item.host} 已存在')
        
        # 加密密码
        data = item.model_dump()
        if data.get('password'):
            data['password'] = aes_encrypt(data['password'], item.host)
        
        # 创建记录
        server = await XuiServer.create(**data)
        if not server:
            raise HTTPException(status_code=500, detail='创建失败')
        
        result = XuiServerOut.model_validate(server)
        
        # 管理员可以看到解密后的密码
        if is_admin and server.password:
            try:
                result.password = aes_decrypt(server.password, server.host)
            except Exception as e:
                logger.warning(f'解密密码失败: {e}')
        
        return result
    
    async def get(self, id: UUID, is_admin: bool = False) -> XuiServerOut:
        """获取单个 XUI 服务器"""
        server = await XuiServer.get_or_none(id=id)
        if not server:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        result = XuiServerOut.model_validate(server)
        
        # 管理员可以看到解密后的密码
        if is_admin and server.password:
            try:
                result.password = aes_decrypt(server.password, server.host)
            except Exception as e:
                logger.warning(f'解密密码失败: {e}')
        
        return result
    
    async def get_multi(
        self,
        name: str | None = None,
        host: str | None = None,
        status: int | None = None,
        page: int = 1,
        limit: int = 10,
        res_count: bool = False,
        order_by: str = '-create_time',
        create_time_start: str | int | None = None,
        create_time_end: str | int | None = None,
        is_admin: bool = False
    ) -> XuiServerOutList:
        """获取 XUI 服务器列表"""
        query = XuiServer.all()
        
        # 条件过滤
        if name:
            query = query.filter(name__icontains=name)
        if host:
            query = query.filter(host__icontains=host)
        if status:
            query = query.filter(status=status)
        if create_time_start:
            query = query.filter(create_time__gte=parse_time(create_time_start))
        if create_time_end:
            query = query.filter(create_time__lte=parse_time(create_time_end, is_end=True))
        
        # 排序
        if order_by:
            query = query.order_by(order_by)
        
        # 计数
        if res_count:
            count = await query.count()
        else:
            count = -1
        
        # 分页
        offset = (page - 1) * limit
        servers = await query.limit(limit).offset(offset)
        
        if not servers:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        items = []
        for server in servers:
            result = XuiServerOut.model_validate(server)
            
            # 管理员可以看到解密后的密码
            if is_admin and server.password:
                try:
                    result.password = aes_decrypt(server.password, server.host)
                except Exception as e:
                    logger.warning(f'解密密码失败: {e}')
            
            items.append(result)
        
        return XuiServerOutList(
            message='成功',
            count=count,
            num=len(items),
            items=items
        )
    
    async def update(self, id: UUID, item: XuiServerUpdate, is_admin: bool = False) -> XuiServerOut:
        """更新 XUI 服务器"""
        server = await XuiServer.get_or_none(id=id)
        if not server:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        
        # 检查主机是否重复
        if 'host' in update_data:
            new_host = update_data['host']
            is_exist = await XuiServer.get_or_none(host=new_host)
            if is_exist and is_exist.id != id:
                raise HTTPException(status_code=400, detail=f'服务器地址 {new_host} 已被占用')
        
        # 加密密码
        if 'password' in update_data and update_data['password']:
            host_for_encrypt = update_data.get('host', server.host)
            update_data['password'] = aes_encrypt(update_data['password'], host_for_encrypt)
        
        # 更新
        await server.update_from_dict(update_data)
        await server.save()
        
        result = XuiServerOut.model_validate(server)
        
        # 管理员可以看到解密后的密码
        if is_admin and server.password:
            try:
                result.password = aes_decrypt(server.password, server.host)
            except Exception as e:
                logger.warning(f'解密密码失败: {e}')
        
        return result
    
    async def delete(self, id: UUID) -> BaseOut:
        """删除 XUI 服务器"""
        server = await XuiServer.get_or_none(id=id)
        if not server:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        # 检查是否有关联的入站
        from app.models.xui import XuiInbound
        inbound_count = await XuiInbound.filter(server_id=id).count()
        if inbound_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f'该服务器下还有 {inbound_count} 个入站配置，请先删除入站'
            )
        
        await server.delete()
        return BaseOut(message='成功', count=1)


xui_server_crud = XuiServerCRUD()
