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
    try:
        return await server_account_crud.get_multi(
            username=username,
            page=page,
            limit=limit,
            res_count=res_count,
            order_by=order_by or "-create_time",
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
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
