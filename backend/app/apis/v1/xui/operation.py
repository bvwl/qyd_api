"""
XUI 操作 API（初始化、重启等）
"""
from uuid import UUID
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends
from typing import List

from app.schemas.xui.user import XuiInitializeRequest, XuiOperationResponse
from app.crud.xui.operation import xui_operation_crud
from app.apis.deps import get_admin_user

app = APIRouter()


@app.post("/initialize", response_model=XuiOperationResponse, summary='初始化 XUI 面板')
async def initialize_panel(
    item: XuiInitializeRequest = Body(..., description='初始化配置'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    一键初始化 XUI 面板
    
    包括：
    - 登录
    - 批量添加入站
    - 配置出站和路由
    - 配置 SSL 证书（可选）
    - 重启 Xray 服务
    - 重启面板（如果配置了证书）
    
    权限要求：ADMIN
    """
    try:
        # 转换 inbounds 为字典列表
        inbound_configs = [inbound.model_dump() for inbound in item.inbounds]
        
        result = await xui_operation_crud.initialize_panel(
            server_id=item.server_id,
            inbound_configs=inbound_configs,
            configure_cert=item.configure_cert
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restart-xray/{server_id}", response_model=XuiOperationResponse, summary='重启 Xray 服务')
async def restart_xray(
    server_id: UUID = Path(..., description='服务器 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    重启 Xray 服务
    
    权限要求：ADMIN
    """
    try:
        result = await xui_operation_crud.restart_xray(server_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restart-panel/{server_id}", response_model=XuiOperationResponse, summary='重启 XUI 面板')
async def restart_panel(
    server_id: UUID = Path(..., description='服务器 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    重启 XUI 面板
    
    权限要求：ADMIN
    """
    try:
        result = await xui_operation_crud.restart_panel(server_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/configure-cert/{server_id}", response_model=XuiOperationResponse, summary='配置 SSL 证书')
async def configure_certificate(
    server_id: UUID = Path(..., description='服务器 ID'),
    cert_file: str = Body(..., description='证书文件路径'),
    key_file: str = Body(..., description='私钥文件路径'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    配置 SSL 证书
    
    权限要求：ADMIN
    """
    try:
        result = await xui_operation_crud.configure_certificate(
            server_id=server_id,
            cert_file=cert_file,
            key_file=key_file
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/configure-routing/{server_id}", response_model=XuiOperationResponse, summary='配置出站和路由')
async def configure_routing(
    server_id: UUID = Path(..., description='服务器 ID'),
    inbound_ids: List[UUID] = Body(..., description='入站 ID 列表'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    配置出站和路由规则
    
    权限要求：ADMIN
    """
    try:
        result = await xui_operation_crud.configure_outbound_routing(
            server_id=server_id,
            inbound_ids=inbound_ids
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/server-status/{server_id}", response_model=XuiOperationResponse, summary='获取服务器状态')
async def get_server_status(
    server_id: UUID = Path(..., description='服务器 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    获取服务器状态信息
    
    权限要求：ADMIN
    """
    try:
        result = await xui_operation_crud.get_server_status(server_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-inbounds/{server_id}", response_model=XuiOperationResponse, summary='同步入站配置')
async def sync_inbounds_from_panel(
    server_id: UUID = Path(..., description='服务器 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    从 XUI 面板同步入站配置到数据库
    
    读取 XUI 面板中已配置的所有入站，并同步到数据库中。
    - 如果入站已存在，则更新信息
    - 如果入站不存在，则创建新记录
    
    权限要求：ADMIN
    """
    try:
        result = await xui_operation_crud.sync_inbounds_from_panel(server_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/xray-config/{server_id}", response_model=XuiOperationResponse, summary='获取 Xray 配置')
async def get_xray_config(
    server_id: UUID = Path(..., description='服务器 ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    从 XUI 面板获取 Xray 配置（出站和路由）
    
    返回 XUI 面板中的 Xray 配置信息，包括：
    - 出站配置列表
    - 路由规则列表
    - 完整的配置 JSON
    
    权限要求：ADMIN
    """
    try:
        result = await xui_operation_crud.get_xray_config_from_panel(server_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
