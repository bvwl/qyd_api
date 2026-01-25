"""
XUI 入站 API
"""
from uuid import UUID
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.xui.inbound import (
    XuiInboundCreate,
    XuiInboundUpdate,
    XuiInboundOut,
    XuiInboundOutList,
    XuiInboundBatchCreate
)
from app.schemas.base import BaseOut
from app.crud.xui.inbound import xui_inbound_crud
from app.apis.deps import get_current_user, get_admin_user

app = APIRouter()


@app.post("", response_model=XuiInboundOut, summary='创建入站')
async def create_inbound(
    item: XuiInboundCreate = Body(..., description='创建数据'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    创建 XUI 入站配置
    
    权限要求：ADMIN
    """
    try:
        result = await xui_inbound_crud.create(item)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch", response_model=list[XuiInboundOut], summary='批量创建入站')
async def batch_create_inbound(
    item: XuiInboundBatchCreate = Body(..., description='批量创建数据'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    批量创建 XUI 入站配置
    
    权限要求：ADMIN
    """
    try:
        results = await xui_inbound_crud.batch_create(item.server_id, item.inbounds)
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=XuiInboundOut, summary='获取入站')
async def get_inbound(
    id: UUID = Path(..., description='入站 ID'),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个入站配置
    
    权限要求：登录用户
    """
    try:
        result = await xui_inbound_crud.get(id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("", response_model=XuiInboundOutList, summary='获取入站列表')
async def get_inbounds(
    server_id: UUID | None = Query(None, description='服务器 ID'),
    listen_host: str | None = Query(None, description='监听地址'),
    listen_port: int | None = Query(None, description='监听端口'),
    protocol: int | None = Query(None, description='协议类型(1:HTTP,2:SOCKS)'),
    status: int | None = Query(None, description='状态(1:正常,2:停用,3:异常)'),
    order_by: str | None = Query(
        '-create_time',
        description='排序字段',
        pattern='^(?:-)?(?:id|listen_host|listen_port|protocol|status|create_time|update_time)$'
    ),
    res_count: bool = Query(False, description='是否返回总数'),
    create_time_start: str | int | None = Query(
        None,
        description='创建时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'
    ),
    create_time_end: str | int | None = Query(
        None,
        description='创建时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'
    ),
    page: int = Query(1, ge=1, description='页码'),
    limit: int = Query(10, ge=1, le=1000, description='每页数量'),
    current_user: dict = Depends(get_current_user)
):
    """
    获取入站列表
    
    权限要求：登录用户
    """
    try:
        return await xui_inbound_crud.get_multi(
            server_id=server_id,
            listen_host=listen_host,
            listen_port=listen_port,
            protocol=protocol,
            status=status,
            page=page,
            limit=limit,
            res_count=res_count,
            order_by=order_by,
            create_time_start=create_time_start,
            create_time_end=create_time_end
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=XuiInboundOut, summary='更新入站')
async def update_inbound(
    id: UUID = Path(..., description='入站 ID'),
    item: XuiInboundUpdate = Body(..., description='更新数据'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    更新入站配置
    
    权限要求：ADMIN
    """
    try:
        result = await xui_inbound_crud.update(id, item)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, summary='删除入站')
async def delete_inbound(
    id: UUID = Path(..., description='入站 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除入站配置
    
    权限要求：ADMIN
    """
    try:
        return await xui_inbound_crud.delete(id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
