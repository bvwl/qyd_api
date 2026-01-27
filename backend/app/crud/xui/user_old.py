"""
XUI 入站账号关联 CRUD
"""
from uuid import UUID
from fastapi import HTTPException
from typing import List, Dict, Any
from datetime import datetime

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
    
    async def add_account_to_inbound(self, inbound_id: UUID, account_id: UUID) -> XuiInboundAccountOut:
        """添加账号到入站"""
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
                    operation_type=XuiOperationType.ADD_ACCOUNT,
                    status=XuiOperationStatus.FAILED,
                    inbound_id=inbound_id,
                    account_id=account_id,
                    inbound_info=inbound_info,
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
                operation_type=XuiOperationType.ADD_ACCOUNT,
                status=XuiOperationStatus.FAILED,
                inbound_id=inbound_id,
                account_id=account_id,
                inbound_info=inbound_info,
                account_username=account.username,
                error_message=str(e)
            )
            raise HTTPException(status_code=500, detail=f'添加用户失败: {str(e)}')
        
        # 添加关联关系
        await inbound.accounts.add(account)
        
        # 记录成功日志
        await XuiOperationLog.create(
            operation_type=XuiOperationType.ADD_ACCOUNT,
            status=XuiOperationStatus.SUCCESS,
            inbound_id=inbound_id,
            account_id=account_id,
            inbound_info=inbound_info,
            account_username=account.username
        )
        
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
    
    async def batch_add_accounts(
        self,
        inbound_id: UUID,
        account_ids: List[UUID]
    ) -> Dict[str, Any]:
        """批量添加账号到入站"""
        success_list = []
        failed_list = []
        
        # 获取入站信息
        inbound = await XuiInbound.get_or_none(id=inbound_id)
        if not inbound:
            raise HTTPException(status_code=404, detail='入站不存在')
        
        inbound_info = f"{inbound.listen_host}:{inbound.listen_port}"
        
        for account_id in account_ids:
            try:
                result = await self.add_account_to_inbound(inbound_id, account_id)
                success_list.append({
                    'account_id': str(account_id),
                    'username': result.username
                })
            except HTTPException as e:
                # 获取账号信息用于日志
                account = await ServerAccount.get_or_none(id=account_id)
                username = account.username if account else str(account_id)
                
                failed_list.append({
                    'account_id': str(account_id),
                    'username': username,
                    'error': e.detail
                })
                logger.error(f'批量添加账号失败: account_id={account_id}, 错误: {e.detail}')
            except Exception as e:
                # 获取账号信息用于日志
                account = await ServerAccount.get_or_none(id=account_id)
                username = account.username if account else str(account_id)
                
                failed_list.append({
                    'account_id': str(account_id),
                    'username': username,
                    'error': str(e)
                })
                logger.error(f'批量添加账号失败: account_id={account_id}, 错误: {e}')
        
        # 记录批量操作日志
        await XuiOperationLog.create(
            operation_type=XuiOperationType.BATCH_ADD,
            status=XuiOperationStatus.SUCCESS if len(failed_list) == 0 else XuiOperationStatus.FAILED,
            inbound_id=inbound_id,
            inbound_info=inbound_info,
            error_message=f'成功={len(success_list)}, 失败={len(failed_list)}' if len(failed_list) > 0 else None
        )
        
        return {
            'total': len(account_ids),
            'success': len(success_list),
            'failed': len(failed_list),
            'success_list': success_list,
            'failed_list': failed_list
        }
    
    async def get_failed_logs(
        self,
        inbound_id: UUID = None,
        operation_type: XuiOperationType = None,
        page: int = 1,
        limit: int = 10,
        res_count: bool = False
    ) -> Dict[str, Any]:
        """获取失败的操作日志"""
        query = XuiOperationLog.filter(status=XuiOperationStatus.FAILED)
        
        if inbound_id:
            query = query.filter(inbound_id=inbound_id)
        
        if operation_type:
            query = query.filter(operation_type=operation_type)
        
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
                'operation_type': log.operation_type,
                'status': log.status,
                'inbound_id': str(log.inbound_id) if log.inbound_id else None,
                'account_id': str(log.account_id) if log.account_id else None,
                'inbound_info': log.inbound_info,
                'account_username': log.account_username,
                'error_message': log.error_message,
                'retry_count': log.retry_count,
                'last_retry_time': log.last_retry_time.strftime("%Y-%m-%d %H:%M:%S") if log.last_retry_time else None,
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
        
        if log.status != XuiOperationStatus.FAILED:
            raise HTTPException(status_code=400, detail='只能重试失败的操作')
        
        # 更新状态为重试中
        log.status = XuiOperationStatus.RETRYING
        log.retry_count += 1
        log.last_retry_time = datetime.now()
        await log.save()
        
        try:
            # 根据操作类型执行重试
            if log.operation_type == XuiOperationType.ADD_ACCOUNT:
                if not log.inbound_id or not log.account_id:
                    raise HTTPException(status_code=400, detail='日志数据不完整')
                
                result = await self.add_account_to_inbound(log.inbound_id, log.account_id)
                
                # 更新日志状态为成功
                log.status = XuiOperationStatus.SUCCESS
                log.error_message = None
                await log.save()
                
                return {
                    'success': True,
                    'message': '重试成功',
                    'result': {
                        'username': result.username
                    }
                }
            else:
                raise HTTPException(status_code=400, detail='不支持的操作类型')
        
        except Exception as e:
            # 更新日志状态为失败
            log.status = XuiOperationStatus.FAILED
            log.error_message = f'重试失败: {str(e)}'
            await log.save()
            
            return {
                'success': False,
                'message': f'重试失败: {str(e)}'
            }
    
    async def batch_retry_failed_logs(self, inbound_id: UUID = None) -> Dict[str, Any]:
        """批量重试失败的操作"""
        query = XuiOperationLog.filter(
            status=XuiOperationStatus.FAILED,
            operation_type=XuiOperationType.ADD_ACCOUNT
        )
        
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


xui_inbound_account_crud = XuiInboundAccountCRUD()
