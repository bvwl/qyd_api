"""
XUI 服务器 API
"""
from uuid import UUID
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.xui.server import XuiServerCreate, XuiServerUpdate, XuiServerOut, XuiServerOutList
from app.schemas.base import BaseOut
from app.crud.xui.server import xui_server_crud
from app.apis.deps import get_current_user, get_admin_user

app = APIRouter()


@app.post("", response_model=XuiServerOut, summary='创建 XUI 服务器')
async def create_server(
    item: XuiServerCreate = Body(..., description='创建数据'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    创建 XUI 服务器配置
    
    权限要求：ADMIN
    """
    try:
        result = await xui_server_crud.create(item, is_admin=True)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=XuiServerOut, summary='获取 XUI 服务器')
async def get_server(
    id: UUID = Path(..., description='服务器 ID'),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个 XUI 服务器配置
    
    权限要求：登录用户
    """
    try:
        user_roles = current_user.get('roles', [])
        is_admin = 'ADMIN' in user_roles
        
        result = await xui_server_crud.get(id, is_admin=is_admin)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("", response_model=XuiServerOutList, summary='获取 XUI 服务器列表')
async def get_servers(
    name: str | None = Query(None, description='服务器名称'),
    host: str | None = Query(None, description='服务器地址'),
    status: int | None = Query(None, description='状态(1:正常,2:停用,3:异常)'),
    order_by: str | None = Query(
        '-create_time',
        description='排序字段',
        pattern='^(?:-)?(?:id|name|host|status|create_time|update_time)$'
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
    获取 XUI 服务器列表
    
    权限要求：登录用户
    """
    try:
        user_roles = current_user.get('roles', [])
        is_admin = 'ADMIN' in user_roles
        
        return await xui_server_crud.get_multi(
            name=name,
            host=host,
            status=status,
            page=page,
            limit=limit,
            res_count=res_count,
            order_by=order_by,
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            is_admin=is_admin
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=XuiServerOut, summary='更新 XUI 服务器')
async def update_server(
    id: UUID = Path(..., description='服务器 ID'),
    item: XuiServerUpdate = Body(..., description='更新数据'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    更新 XUI 服务器配置
    
    权限要求：ADMIN
    """
    try:
        result = await xui_server_crud.update(id, item, is_admin=True)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, summary='删除 XUI 服务器')
async def delete_server(
    id: UUID = Path(..., description='服务器 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除 XUI 服务器配置
    
    权限要求：ADMIN
    """
    try:
        return await xui_server_crud.delete(id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
