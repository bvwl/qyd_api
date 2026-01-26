from uuid import UUID

from app.schemas.server.account import Create, Update, Out, OutList
from app.crud.server.account import server_account_crud
from app.schemas.base import BaseOut
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends
from app.apis.deps import get_current_user, get_admin_user

app = APIRouter()


@app.post("", response_model=Out, description="创建代理账号", summary="创建代理账号")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await server_account_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取代理账号", summary="获取代理账号")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await server_account_crud.get(id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("", response_model=OutList, description="获取代理账号", summary="获取代理账号")
async def gets(
    username: str | None = Query(None, description="用户名"),
    user_id: UUID | None = Query(None, description="用户ID（管理员可用）"),
    proxy_type: str | None = Query(None, description="代理类型（HTTP/SOCKS5）", pattern="^(HTTP|SOCKS5)$"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|username|create_time|update_time)$",
    ),
    res_count: bool = Query(False, description="是否返回总数"),
    create_time_start: str | int | None = Query(
        None,
        description="创建时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    create_time_end: str | int | None = Query(
        None,
        description="创建时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    update_time_start: str | int | None = Query(
        None,
        description="更新时间开始 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    update_time_end: str | int | None = Query(
        None,
        description="更新时间结束 (支持 YYYY-MM-DD / YYYY-MM-DD HH:mm:ss / 13位时间戳)",
    ),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=1000, description="每页数量"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取服务器账号列表
    - 管理员：可以查看所有用户的服务器账号（自动解密密码）
    - 普通用户：只能查看自己的服务器账号
    """
    try:
        # 检查是否是管理员
        user_roles = current_user.get('roles', [])
        is_admin = 'ADMIN' in user_roles
        
        # 非管理员只能查看自己的账号
        if not is_admin:
            user_id = UUID(current_user.get('user_id') or current_user.get('id'))
        # 管理员如果没有指定 user_id，则查看所有账号
        # 如果指定了 user_id，则只查看该用户的账号
        
        return await server_account_crud.get_multi(
            username=username,
            user_id=user_id if user_id or not is_admin else None,
            proxy_type=proxy_type,
            page=page,
            limit=limit,
            res_count=res_count,
            order_by=order_by or "-create_time",
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
            is_admin=is_admin
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新代理账号", summary="更新代理账号")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await server_account_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除代理账号", summary="删除代理账号")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    admin_user: dict = Depends(get_admin_user)
):
    try:
        return await server_account_crud.delete(id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新代理账号", summary="创建或更新代理账号")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    try:
        return await server_account_crud.upsert(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate", response_model=Out, description="生成服务器账号", summary="生成服务器账号")
async def generate(
    current_user: dict = Depends(get_current_user)
):
    """
    为当前用户生成服务器账号（SOCKS5代理账号）
    - 如果用户已有账号，返回现有账号（包含解密后的密码）
    - 如果没有，创建新账号（用户名：user_{user_id前8位}，密码：随机16位）
    - 一个用户只能有一个服务器账号
    - 密码使用AES加密存储，每个用户使用不同的密钥
    """
    try:
        user_id = UUID(current_user.get('user_id') or current_user.get('id'))
        return await server_account_crud.generate_account(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}/password", response_model=Out, description="获取解密后的密码", summary="获取解密后的密码")
async def get_password(
    id: UUID = Path(..., description="账号ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取服务器账号的解密密码
    - 管理员：可以查看所有用户的账号密码
    - 普通用户：只能查看自己的账号密码
    """
    try:
        # 先获取账号信息
        account = await server_account_crud.get(id)
        
        # 权限检查：非管理员只能查看自己的账号
        user_roles = current_user.get('roles', [])
        is_admin = 'ADMIN' in user_roles
        current_user_id = UUID(current_user.get('user_id') or current_user.get('id'))
        
        if not is_admin and str(account.user_id) != str(current_user_id):
            raise HTTPException(status_code=403, detail='无权查看此账号密码')
        
        # 获取解密后的密码
        return await server_account_crud.get_with_password(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
