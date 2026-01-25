from uuid import UUID

from app.schemas.server.info import Create, Update, Out, OutList
from app.crud.server.info import server_info_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.apis.deps import get_current_user, get_admin_user

app = APIRouter()


# 创建服务器信息
@app.post("", response_model=Out, description='创建服务器信息', summary='创建服务器信息')
async def post(
    item: Create = Body(..., description='创建数据'),
    current_user: dict = Depends(get_current_user)
):
    """
    创建服务器信息记录
    """
    try:
        user_id = current_user.get('user_id') or current_user.get('id')
        result = await server_info_crud.create(item, current_user_id=UUID(user_id))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 查询服务器单个信息
@app.get("/{id}", response_model=Out, description='获取服务器信息', summary='获取服务器信息')
async def get(
    id: UUID = Path(..., description='ID'),
    current_user: dict = Depends(get_current_user)
):
    """
    获取服务器信息记录
    """
    try:
        # 检查是否是管理员
        user_roles = current_user.get('roles', [])
        is_admin = 'ADMIN' in user_roles
        user_id = current_user.get('user_id') or current_user.get('id')
        
        obj = await server_info_crud.get(id, is_admin=is_admin, current_user_id=UUID(user_id))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail='数据不存在')
    return obj


# 查询服务器信息
@app.get("", response_model=OutList, description='获取服务器信息', summary='获取服务器信息')
async def gets(
        host: str | None = Query(None, description='服务器地址'),
        domain: str | None = Query(None, description='域名'),
        port: int | None = Query(None, description='代理端口'),
        order_by: str | None = Query('-create_time', description='排序字段',
                                     pattern='^(?:-)?(?:id|host|domain|port|create_time|update_time)$'),
        res_count: bool = Query(False, description='是否返回总数'),
        create_time_start: str | int | None = Query(
            None, description='创建时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'),
        create_time_end: str | int | None = Query(
            None, description='创建时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'),
        update_time_start: str | int | None = Query(
            None, description='更新时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'),
        update_time_end: str | int | None = Query(
            None, description='更新时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)'),
        page: int = Query(1, ge=1, description='页码'),
        limit: int = Query(10, ge=1, le=1000, description='每页数量'),
    current_user: dict = Depends(get_current_user)
):
    """
    获取服务器信息列表
    权限要求：ADMIN, GM, IT 可以访问，MANUAL 不能访问
    """
    try:
        from app.utils.data_permission import get_user_data_scope, has_resource_access
        
        # 获取用户ID和角色
        user_id = current_user.get('user_id') or current_user.get('id')
        scope = await get_user_data_scope(user_id)
        
        # 检查是否有访问服务器资源的权限
        if not has_resource_access(scope['roles'], 'server'):
            raise HTTPException(status_code=403, detail='没有权限访问服务器资源')
        
        # 检查是否是管理员
        is_admin = 'ADMIN' in scope['roles']
        
        return await server_info_crud.get_multi(
            host=host,
            domain=domain,
            port=port,
            order_by=order_by,
            res_count=res_count,
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
            page=page,
            limit=limit,
            is_admin=is_admin,
            current_user_id=UUID(user_id)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 更新服务器信息
@app.put("/{id}", response_model=Out, description='更新服务器信息', summary='更新服务器信息')
async def put(id: UUID = Path(..., description='主键ID'),
              item: Update = Body(..., description='更新数据'),
    current_user: dict = Depends(get_current_user)
              ):
    """
    部分更新服务器信息，只更新传入的非空字段
    """
    try:
        # 检查是否是管理员
        user_roles = current_user.get('roles', [])
        is_admin = 'ADMIN' in user_roles
        user_id = current_user.get('user_id') or current_user.get('id')
        
        result = await server_info_crud.update(id, item, is_admin=is_admin, current_user_id=UUID(user_id))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 删除服务器信息
@app.delete("/{id}", response_model=BaseOut, description='删除服务器信息', summary='删除服务器信息')
async def delete(
    id: UUID = Path(..., description='主键ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除服务器信息
    """
    try:
        return await server_info_crud.delete(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 创建或更新服务器信息
@app.post("/upsert", response_model=Out, description='创建或更新服务器信息', summary='创建或更新服务器信息')
async def post_or_put(
    item: Create = Body(..., description='创建或更新数据'),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新服务器信息
    """
    try:
        filter_kwargs = {
            "host": item.host
        }
        user_id = current_user.get('user_id') or current_user.get('id')
        result = await server_info_crud.upsert(filter_kwargs, item, current_user_id=UUID(user_id))
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
