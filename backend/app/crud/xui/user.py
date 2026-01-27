"""
XUI 入站账号关联 CRUD (简化版)
只记录添加账号失败的情况
"""
from uuid import UUID
from fastapi import HTTPException
from typing import List, Dict, Any

from app.models.xui import XuiInbound
from app.models.server import ServerAccount
from app.models.user import XuiOperationLog
from app.schemas.xui.user import (
    XuiInboundAccountAdd,
    XuiInboundAccountRemove,
    XuiInboundAccountOut,
    XuiInboundAccountOutList
)
from app.schemas.base import BaseOut
from app.core.tools import aes_decrypt
from app.clients.xui import XuiClient
from app.utils.logs import getLogger

logger = getLogger('app')


class XuiInboundAccountCRUD:
    """XUI 入站账号关联 CRUD 操作"""
    
    async def _get_xui_client_for_inbound(self, inbound_id: UUID) -> tuple[XuiClient, XuiInbound]:
        """获取入站对应的 XUI 客户端实例"""
        inbound = await XuiInbound.get_or_none(id=inbound_id).prefetch_related('server')
        if not inbound:
            raise HTTPException(status_code=404, detail='入站不存在')
        
        server = inbound.server
        
        # 优先使用 domain，如果没有则使用 host
        connect_host = server.domain if server.domain else server.host
        
        # 解密密码（使用 host 作为加密 key）
        try:
            password = aes_decrypt(server.password, server.host)
        except Exception as e:
            logger.error(f'解密 XUI 密码失败: {e}')
            raise HTTPException(status_code=500, detail='解密密码失败')
        
        client = XuiClient(
            host=connect_host,
            port=server.port,
            username=server.username,
            password=password,
            is_ssl=server.is_ssl,
            web_path=server.web_path
        )
        
        return client, inbound
    
    async def _update_account_inbound_status(self, account_id: UUID):
        """
        检查并更新账号的 is_all_inbound_added 状态
        
        逻辑：
        - 如果账号已添加到所有入站，设置为 True
        - 否则设置为 False
        """
        from app.core.database import db_read, db_write
        
        # 获取账号（使用 db_write 因为需要修改）
        account = await db_write(ServerAccount).get_or_none(id=account_id)
        if not account:
            return
        
        # 获取所有入站数量
        total_inbounds = await db_read(XuiInbound).all().count()
        
        if total_inbounds == 0:
            # 没有入站，设置为 False
            account.is_all_inbound_added = False
            await account.save()
            logger.info(f'更新账号入站状态: account={account.username}, is_all_added=False (无入站)')
            return
        
        # 获取账号已添加的入站数量
        added_inbounds = await db_read(XuiInbound).filter(accounts__id=account_id).count()
        
        # 判断是否已添加到所有入站
        is_all_added = (added_inbounds == total_inbounds)
        
        # 更新状态
        if account.is_all_inbound_added != is_all_added:
            account.is_all_inbound_added = is_all_added
            await account.save()
            logger.info(f'更新账号入站状态: account={account.username}, is_all_added={is_all_added}, added={added_inbounds}/{total_inbounds}')
    
    async def add_account_to_inbound(self, inbound_id: UUID, account_id: UUID, skip_if_exists: bool = False) -> XuiInboundAccountOut:
        """
        添加账号到入站
        
        Args:
            inbound_id: 入站 ID
            account_id: 账号 ID
            skip_if_exists: 如果已存在是否跳过(True: 跳过, False: 抛出异常)
        """
        # 获取入站和账号
        inbound = await XuiInbound.get_or_none(id=inbound_id).prefetch_related('server')
        if not inbound:
            raise HTTPException(status_code=404, detail='入站不存在')
        
        account = await ServerAccount.get_or_none(id=account_id)
        if not account:
            raise HTTPException(status_code=404, detail='服务器账号不存在')
        
        # 检查是否已经关联
        existing = await inbound.accounts.filter(id=account_id).exists()
        if existing:
            if skip_if_exists:
                # 跳过已存在的关联
                logger.info(f'账号已关联到入站,跳过: account={account.username}, inbound={inbound.listen_host}:{inbound.listen_port}')
                return XuiInboundAccountOut(
                    inbound_id=inbound_id,
                    account_id=account_id,
                    username=account.username,
                    user_id=account.user_id
                )
            else:
                raise HTTPException(status_code=400, detail='该账号已添加到此入站')
        
        # 获取 XUI 客户端
        client, inbound = await self._get_xui_client_for_inbound(inbound_id)
        
        inbound_info = f"{inbound.listen_host}:{inbound.listen_port}"
        
        # 使用固定账号密码
        username = "cqrxy"
        password = "Zpaily88"
        
        # 在 XUI 面板中添加用户
        try:
            success = await client.add_user_to_inbound(
                host=inbound.listen_host,
                port=inbound.listen_port,
                username=username,
                password=password
            )
            
            if not success:
                # 记录失败日志
                await XuiOperationLog.create(
                    inbound_id=inbound_id,
                    inbound_info=inbound_info,
                    account_id=account_id,
                    account_username=account.username,
                    error_message='XUI 面板返回失败'
                )
                raise HTTPException(status_code=500, detail='添加用户到 XUI 面板失败')
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f'添加用户失败: {e}')
            # 记录失败日志
            await XuiOperationLog.create(
                inbound_id=inbound_id,
                inbound_info=inbound_info,
                account_id=account_id,
                account_username=account.username,
                error_message=str(e)
            )
            raise HTTPException(status_code=500, detail=f'添加用户失败: {str(e)}')
        
        # 添加关联关系
        await inbound.accounts.add(account)
        
        # 检查并更新账号的 is_all_inbound_added 状态
        await self._update_account_inbound_status(account_id)
        
        return XuiInboundAccountOut(
            inbound_id=inbound_id,
            account_id=account_id,
            username=account.username,
            user_id=account.user_id
        )
    
    async def remove_account_from_inbound(self, inbound_id: UUID, account_id: UUID) -> BaseOut:
        """从入站移除账号"""
        # 获取入站和账号
        inbound = await XuiInbound.get_or_none(id=inbound_id)
        if not inbound:
            raise HTTPException(status_code=404, detail='入站不存在')
        
        account = await ServerAccount.get_or_none(id=account_id)
        if not account:
            raise HTTPException(status_code=404, detail='服务器账号不存在')
        
        # 检查是否已关联
        existing = await inbound.accounts.filter(id=account_id).exists()
        if not existing:
            raise HTTPException(status_code=400, detail='该账号未添加到此入站')
        
        # 获取 XUI 客户端
        client, inbound = await self._get_xui_client_for_inbound(inbound_id)
        
        # 使用固定账号密码
        username = "cqrxy"
        password = "Zpaily88"
        
        # 从 XUI 面板中删除用户
        try:
            await client.remove_user_from_inbound(
                host=inbound.listen_host,
                port=inbound.listen_port,
                username=username,
                password=password
            )
        except Exception as e:
            logger.error(f'从 XUI 面板删除用户失败: {e}')
            # 继续删除关联关系
        
        # 删除关联关系
        await inbound.accounts.remove(account)
        
        # 检查并更新账号的 is_all_inbound_added 状态
        await self._update_account_inbound_status(account_id)
        
        return BaseOut(message='成功', count=1)
    
    async def get_inbound_accounts(
        self,
        inbound_id: UUID,
        page: int = 1,
        limit: int = 10,
        res_count: bool = False
    ) -> XuiInboundAccountOutList:
        """获取入站的账号列表"""
        inbound = await XuiInbound.get_or_none(id=inbound_id)
        if not inbound:
            raise HTTPException(status_code=404, detail='入站不存在')
        
        # 获取关联的账号
        query = inbound.accounts.all()
        
        # 计数
        if res_count:
            count = await query.count()
        else:
            count = -1
        
        # 分页
        offset = (page - 1) * limit
        accounts = await query.limit(limit).offset(offset)
        
        # 如果没有查询到数据，抛出 404
        if not accounts:
            raise HTTPException(status_code=404, detail='未查询到数据')
        
        items = [
            XuiInboundAccountOut(
                inbound_id=inbound_id,
                account_id=account.id,
                username=account.username,
                user_id=account.user_id
            )
            for account in accounts
        ]
        
        return XuiInboundAccountOutList(
            message='成功',
            count=count,
            num=len(items),
            items=items
        )
    
    async def get_failed_logs(
        self,
        inbound_id: UUID = None,
        page: int = 1,
        limit: int = 10,
        res_count: bool = False
    ) -> Dict[str, Any]:
        """获取失败的操作日志"""
        query = XuiOperationLog.filter(is_resolved=False)
        
        if inbound_id:
            query = query.filter(inbound_id=inbound_id)
        
        # 计数
        if res_count:
            count = await query.count()
        else:
            count = -1
        
        # 分页
        offset = (page - 1) * limit
        logs = await query.limit(limit).offset(offset).order_by('-create_time')
        
        items = []
        for log in logs:
            items.append({
                'id': str(log.id),
                'inbound_id': str(log.inbound_id),
                'inbound_info': log.inbound_info,
                'account_id': str(log.account_id),
                'account_username': log.account_username,
                'error_message': log.error_message,
                'retry_count': log.retry_count,
                'is_resolved': log.is_resolved,
                'create_time': log.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            })
        
        return {
            'message': '成功',
            'count': count,
            'num': len(items),
            'items': items
        }
    
    async def retry_failed_log(self, log_id: UUID) -> Dict[str, Any]:
        """重试失败的操作"""
        log = await XuiOperationLog.get_or_none(id=log_id)
        if not log:
            raise HTTPException(status_code=404, detail='日志不存在')
        
        if log.is_resolved:
            raise HTTPException(status_code=400, detail='该操作已解决')
        
        # 更新重试次数
        log.retry_count += 1
        await log.save()
        
        try:
            # 重新执行添加操作
            result = await self.add_account_to_inbound(log.inbound_id, log.account_id)
            
            # 标记为已解决
            log.is_resolved = True
            await log.save()
            
            return {
                'success': True,
                'message': '重试成功',
                'result': {
                    'username': result.username
                }
            }
        
        except Exception as e:
            # 更新错误信息
            log.error_message = f'重试失败({log.retry_count}次): {str(e)}'
            await log.save()
            
            return {
                'success': False,
                'message': f'重试失败: {str(e)}'
            }
    
    async def batch_retry_failed_logs(self, inbound_id: UUID = None) -> Dict[str, Any]:
        """批量重试失败的操作"""
        query = XuiOperationLog.filter(is_resolved=False)
        
        if inbound_id:
            query = query.filter(inbound_id=inbound_id)
        
        logs = await query.all()
        
        success_count = 0
        failed_count = 0
        
        for log in logs:
            try:
                result = await self.retry_failed_log(log.id)
                if result['success']:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f'批量重试失败: log_id={log.id}, 错误: {e}')
                failed_count += 1
        
        return {
            'total': len(logs),
            'success': success_count,
            'failed': failed_count
        }
    
    async def add_account_to_all_inbounds(self, account_id: UUID) -> Dict[str, Any]:
        """将账号添加到所有入站"""
        from app.core.database import db_read, db_write
        
        # 获取账号
        account = await db_read(ServerAccount).get_or_none(id=account_id)
        if not account:
            raise HTTPException(status_code=404, detail='服务器账号不存在')
        
        # 获取所有入站
        inbounds = await db_read(XuiInbound).all()
        
        if not inbounds:
            raise HTTPException(status_code=404, detail='没有可用的入站')
        
        success_count = 0
        failed_count = 0
        failed_list = []
        
        for inbound in inbounds:
            try:
                # 添加到入站(如果已存在则跳过)
                await self.add_account_to_inbound(inbound.id, account_id, skip_if_exists=True)
                success_count += 1
                
            except Exception as e:
                logger.error(f'添加账号到入站失败: inbound_id={inbound.id}, 错误: {e}')
                failed_count += 1
                failed_list.append({
                    'inbound_id': str(inbound.id),
                    'inbound_info': f'{inbound.listen_host}:{inbound.listen_port}',
                    'error': str(e)
                })
        
        # 更新账号状态
        if failed_count == 0:
            account.is_all_inbound_added = True
            await account.save()
        
        return {
            'total': len(inbounds),
            'success': success_count,
            'failed': failed_count,
            'failed_list': failed_list,
            'is_all_added': failed_count == 0
        }
    
    async def remove_account_from_all_inbounds(self, account_id: UUID) -> Dict[str, Any]:
        """从所有入站删除账号"""
        from app.core.database import db_read, db_write
        
        # 获取账号
        account = await db_read(ServerAccount).get_or_none(id=account_id)
        if not account:
            raise HTTPException(status_code=404, detail='服务器账号不存在')
        
        # 获取所有入站
        inbounds = await db_read(XuiInbound).all()
        
        if not inbounds:
            raise HTTPException(status_code=404, detail='没有可用的入站')
        
        success_count = 0
        failed_count = 0
        failed_list = []
        
        for inbound in inbounds:
            try:
                # 检查是否已经关联
                existing = await inbound.accounts.filter(id=account_id).exists()
                if not existing:
                    # 如果未关联,视为成功(已经是删除状态)
                    success_count += 1
                    continue
                
                # 从入站删除
                await self.remove_account_from_inbound(inbound.id, account_id)
                success_count += 1
                
            except Exception as e:
                logger.error(f'从入站删除账号失败: inbound_id={inbound.id}, 错误: {e}')
                failed_count += 1
                failed_list.append({
                    'inbound_id': str(inbound.id),
                    'inbound_info': f'{inbound.listen_host}:{inbound.listen_port}',
                    'error': str(e)
                })
        
        # 更新账号状态
        if failed_count == 0:
            account.is_all_inbound_added = False
            await account.save()
        
        return {
            'total': len(inbounds),
            'success': success_count,
            'failed': failed_count,
            'failed_list': failed_list,
            'is_all_removed': failed_count == 0
        }


xui_inbound_account_crud = XuiInboundAccountCRUD()
