"""
XUI 入站 CRUD
"""
from uuid import UUID
from fastapi import HTTPException
from typing import List

from app.models.xui import XuiInbound, XuiServer, XuiProtocol
from app.schemas.xui.inbound import XuiInboundCreate, XuiInboundUpdate, XuiInboundOut, XuiInboundOutList
from app.schemas.base import BaseOut
from app.utils.time_tool import parse_time
from app.core.tools import aes_encrypt, aes_decrypt
from app.clients.xui import XuiClient
from app.utils.logs import getLogger

logger = getLogger('app')


class XuiInboundCRUD:
    """XUI 入站 CRUD 操作"""
    
    async def _get_xui_client(self, server_id: UUID) -> XuiClient:
        """获取 XUI 客户端实例"""
        server = await XuiServer.get_or_none(id=server_id)
        if not server:
            raise HTTPException(status_code=404, detail='XUI 服务器不存在')
        
        # 优先使用 domain，如果没有则使用 host
        connect_host = server.domain if server.domain else server.host
        
        # 解密密码（使用 host 作为加密 key）
        try:
            password = aes_decrypt(server.password, server.host)
        except Exception as e:
            logger.error(f'解密 XUI 密码失败: {e}')
            raise HTTPException(status_code=500, detail='解密密码失败')
        
        return XuiClient(
            host=connect_host,
            port=server.port,
            username=server.username,
            password=password,
            is_ssl=server.is_ssl,
            web_path=server.web_path
        )
    
    async def create(self, item: XuiInboundCreate) -> XuiInboundOut:
        """创建 XUI 入站"""
        # 检查是否已存在
        is_exist = await XuiInbound.get_or_none(
            server_id=item.server_id,
            listen_host=item.listen_host,
            listen_port=item.listen_port
        )
        if is_exist:
            raise HTTPException(
                status_code=400,
                detail=f'入站 {item.listen_host}:{item.listen_port} 已存在'
            )
        
        # 获取 XUI 客户端
        client = await self._get_xui_client(item.server_id)
        
        # 确定协议
        protocol_map = {1: 'http', 2: 'socks'}
        protocol = protocol_map.get(item.protocol, 'auto')
        
        # 在 XUI 面板中添加入站
        try:
            # 使用默认账号密码
            default_username = item.default_username if item.default_username else 'cqrxy'
            default_password = item.default_password if item.default_password else 'Zpaily88'
            
            inbound_id = await client.add_inbound(
                host=item.listen_host,
                port=item.listen_port,
                protocol=protocol,
                username=default_username,
                password=default_password,
                remark=item.remark
            )
            
            if inbound_id is None:
                raise HTTPException(status_code=400, detail='端口已被占用')
        
        except Exception as e:
            logger.error(f'添加入站失败: {e}')
            raise HTTPException(status_code=500, detail=f'添加入站失败: {str(e)}')
        
        # 加密默认密码
        data = item.model_dump()
        if data.get('default_password'):
            data['default_password'] = aes_encrypt(
                data['default_password'],
                f"{item.listen_host}:{item.listen_port}"
            )
        
        data['inbound_id'] = inbound_id
        
        # 创建数据库记录
        inbound = await XuiInbound.create(**data)
        if not inbound:
            raise HTTPException(status_code=500, detail='创建数据库记录失败')
        
        return XuiInboundOut.model_validate(inbound)
    
    async def get(self, id: UUID) -> XuiInboundOut:
        """获取单个入站"""
        inbound = await XuiInbound.get_or_none(id=id)
        if not inbound:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        return XuiInboundOut.model_validate(inbound)
    
    async def get_multi(
        self,
        server_id: UUID | None = None,
        listen_host: str | None = None,
        listen_port: int | None = None,
        protocol: int | None = None,
        status: int | None = None,
        page: int = 1,
        limit: int = 10,
        res_count: bool = False,
        order_by: str = '-create_time',
        create_time_start: str | int | None = None,
        create_time_end: str | int | None = None
    ) -> XuiInboundOutList:
        """获取入站列表"""
        query = XuiInbound.all()
        
        # 条件过滤
        if server_id:
            query = query.filter(server_id=server_id)
        if listen_host:
            query = query.filter(listen_host__icontains=listen_host)
        if listen_port:
            query = query.filter(listen_port=listen_port)
        if protocol:
            query = query.filter(protocol=protocol)
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
        inbounds = await query.limit(limit).offset(offset)
        
        if not inbounds:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        items = [XuiInboundOut.model_validate(inbound) for inbound in inbounds]
        
        return XuiInboundOutList(
            message='成功',
            count=count,
            num=len(items),
            items=items
        )
    
    async def update(self, id: UUID, item: XuiInboundUpdate) -> XuiInboundOut:
        """更新入站"""
        inbound = await XuiInbound.get_or_none(id=id)
        if not inbound:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        update_data = item.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail='没有更新数据')
        
        # 加密默认密码
        if 'default_password' in update_data and update_data['default_password']:
            update_data['default_password'] = aes_encrypt(
                update_data['default_password'],
                f"{inbound.listen_host}:{inbound.listen_port}"
            )
        
        # 更新
        await inbound.update_from_dict(update_data)
        await inbound.save()
        
        return XuiInboundOut.model_validate(inbound)
    
    async def delete(self, id: UUID) -> BaseOut:
        """删除入站"""
        inbound = await XuiInbound.get_or_none(id=id)
        if not inbound:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        # 检查是否有关联的账号
        account_count = await inbound.accounts.all().count()
        if account_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f'该入站下还有 {account_count} 个账号，请先移除账号'
            )
        
        # TODO: 从 XUI 面板中删除入站（可选）
        
        await inbound.delete()
        return BaseOut(message='成功', count=1)
    
    async def batch_create(self, server_id: UUID, inbounds: List[XuiInboundCreate]) -> List[XuiInboundOut]:
        """批量创建入站"""
        results = []
        for inbound_data in inbounds:
            inbound_data.server_id = server_id
            try:
                result = await self.create(inbound_data)
                results.append(result)
            except Exception as e:
                logger.error(f'批量创建入站失败: {inbound_data.dict()}, 错误: {e}')
                # 继续处理下一个
        
        return results


xui_inbound_crud = XuiInboundCRUD()
