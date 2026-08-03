"""
XUI 入站账号管理 API
"""
from uuid import UUID
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends, BackgroundTasks
from typing import List

from app.schemas.xui.user import (
    XuiInboundAccountAdd,
    XuiInboundAccountRemove,
    XuiInboundAccountOut,
    XuiInboundAccountOutList,
    XuiInboundAccountBatchAdd
)
from app.schemas.base import BaseOut
from app.crud.xui.user import xui_inbound_account_crud
from app.apis.deps import get_current_user, get_admin_user
from app.utils.logs import getLogger, safe_repr

app = APIRouter()
logger = getLogger("app")


# 后台任务：添加账号到所有入站
async def add_account_to_all_inbounds_task(account_id: UUID):
    """
    后台任务：将账号添加到所有入站
    """
    try:
        logger.info(f'开始后台任务：添加账号到所有入站, account_id={account_id}')
        await xui_inbound_account_crud.add_account_to_all_inbounds(account_id)
        logger.info('后台任务完成：添加账号到所有入站, account_id=%s', account_id)
    except Exception as e:
        logger.error(
            '后台任务失败：添加账号到所有入站, account_id=%s, 错误=%s',
            account_id,
            safe_repr(e),
            exc_info=True,
        )


# 后台任务：从所有入站删除账号
async def remove_account_from_all_inbounds_task(account_id: UUID):
    """
    后台任务：从所有入站删除账号
    """
    try:
        logger.info(f'开始后台任务：从所有入站删除账号, account_id={account_id}')
        await xui_inbound_account_crud.remove_account_from_all_inbounds(account_id)
        logger.info('后台任务完成：从所有入站删除账号, account_id=%s', account_id)
    except Exception as e:
        logger.error(
            '后台任务失败：从所有入站删除账号, account_id=%s, 错误=%s',
            account_id,
            safe_repr(e),
            exc_info=True,
        )



@app.post("/add", response_model=XuiInboundAccountOut, summary='添加账号到入站')
async def add_account_to_inbound(
    item: XuiInboundAccountAdd = Body(..., description='添加数据'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    添加服务器账号到 XUI 入站
    
    权限要求：ADMIN
    """
    try:
        result = await xui_inbound_account_crud.add_account_to_inbound(
            item.inbound_id,
            item.account_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-add", summary='批量添加账号到入站')
async def batch_add_accounts(
    item: XuiInboundAccountBatchAdd = Body(..., description='批量添加数据'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    批量添加服务器账号到 XUI 入站
    
    返回详细的成功和失败列表
    
    权限要求：ADMIN
    """
    try:
        results = await xui_inbound_account_crud.batch_add_accounts(
            item.inbound_id,
            item.account_ids
        )
        return {
            'code': 200,
            'message': f'批量添加完成: 成功 {results["success"]} 个, 失败 {results["failed"]} 个',
            'data': results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/remove", response_model=BaseOut, summary='从入站移除账号')
async def remove_account_from_inbound(
    item: XuiInboundAccountRemove = Body(..., description='移除数据'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    从 XUI 入站移除服务器账号
    
    权限要求：ADMIN
    """
    try:
        result = await xui_inbound_account_crud.remove_account_from_inbound(
            item.inbound_id,
            item.account_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/inbound/{inbound_id}", response_model=XuiInboundAccountOutList, summary='获取入站的账号列表')
async def get_inbound_accounts(
    inbound_id: UUID = Path(..., description='入站 ID'),
    page: int = Query(1, ge=1, description='页码'),
    limit: int = Query(10, ge=1, le=1000, description='每页数量'),
    res_count: bool = Query(False, description='是否返回总数'),
    current_user: dict = Depends(get_current_user)
):
    """
    获取入站关联的账号列表
    
    权限要求：登录用户
    """
    try:
        return await xui_inbound_account_crud.get_inbound_accounts(
            inbound_id=inbound_id,
            page=page,
            limit=limit,
            res_count=res_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/failed-logs", summary='获取失败的操作日志')
async def get_failed_logs(
    inbound_id: UUID = Query(None, description='入站 ID'),
    page: int = Query(1, ge=1, description='页码'),
    limit: int = Query(10, ge=1, le=1000, description='每页数量'),
    res_count: bool = Query(False, description='是否返回总数'),
    current_user: dict = Depends(get_current_user)
):
    """
    获取失败的 XUI 添加账号日志
    
    用于查看添加账号失败的记录,方便重试
    
    权限要求：登录用户
    """
    try:
        result = await xui_inbound_account_crud.get_failed_logs(
            inbound_id=inbound_id,
            page=page,
            limit=limit,
            res_count=res_count
        )
        return {
            'code': 200,
            'message': result['message'],
            'count': result['count'],
            'num': result['num'],
            'data': result['items']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retry-failed/{log_id}", summary='重试失败的操作')
async def retry_failed_log(
    log_id: UUID = Path(..., description='日志 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    重试失败的 XUI 操作
    
    权限要求：ADMIN
    """
    try:
        result = await xui_inbound_account_crud.retry_failed_log(log_id)
        return {
            'code': 200,
            'message': result['message'],
            'data': result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-retry-failed", summary='批量重试失败的操作')
async def batch_retry_failed_logs(
    inbound_id: UUID = Query(None, description='入站 ID(不传则重试所有)'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    批量重试失败的 XUI 操作
    
    权限要求：ADMIN
    """
    try:
        result = await xui_inbound_account_crud.batch_retry_failed_logs(inbound_id)
        return {
            'code': 200,
            'message': f'批量重试完成: 成功 {result["success"]} 个, 失败 {result["failed"]} 个',
            'data': result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-to-all-inbounds/{account_id}", summary='将账号添加到所有入站（后台任务）')
async def add_account_to_all_inbounds(
    background_tasks: BackgroundTasks,
    account_id: UUID = Path(..., description='账号 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    将服务器账号添加到所有 XUI 入站（后台任务执行）
    
    权限要求：ADMIN
    
    说明：
    - 此操作会在后台异步执行，不会阻塞接口响应
    - 可以通过日志查看执行进度和结果
    - 建议在 XUI 账号列表页面查看账号的 is_all_inbound_added 状态
    """
    try:
        # 先验证账号是否存在
        from app.models.server import ServerAccount
        from app.core.database import db_read
        
        account = await db_read(ServerAccount).get_or_none(id=account_id)
        if not account:
            raise HTTPException(status_code=404, detail='服务器账号不存在')
        
        # 添加后台任务
        background_tasks.add_task(add_account_to_all_inbounds_task, account_id)
        
        return {
            'code': 200,
            'message': '已提交后台任务，正在添加账号到所有入站，请稍后查看结果',
            'data': {
                'account_id': str(account_id),
                'account_username': account.username,
                'status': 'processing'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/remove-from-all-inbounds/{account_id}", summary='从所有入站删除账号（后台任务）')
async def remove_account_from_all_inbounds(
    background_tasks: BackgroundTasks,
    account_id: UUID = Path(..., description='账号 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    从所有 XUI 入站删除服务器账号（后台任务执行）
    
    权限要求：ADMIN
    
    说明：
    - 此操作会在后台异步执行，不会阻塞接口响应
    - 可以通过日志查看执行进度和结果
    - 建议在 XUI 账号列表页面查看账号的 is_all_inbound_added 状态
    """
    try:
        # 先验证账号是否存在
        from app.models.server import ServerAccount
        from app.core.database import db_read
        
        account = await db_read(ServerAccount).get_or_none(id=account_id)
        if not account:
            raise HTTPException(status_code=404, detail='服务器账号不存在')
        
        # 添加后台任务
        background_tasks.add_task(remove_account_from_all_inbounds_task, account_id)
        
        return {
            'code': 200,
            'message': '已提交后台任务，正在从所有入站删除账号，请稍后查看结果',
            'data': {
                'account_id': str(account_id),
                'account_username': account.username,
                'status': 'processing'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
