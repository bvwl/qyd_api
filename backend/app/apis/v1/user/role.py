from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.user.role import Create, Update, Out, OutList
from app.crud.user.role import role_crud
from app.schemas.base import BaseOut
from app.core.verify import get_current_user, get_admin_user


app = APIRouter()


@app.post("", response_model=Out, description="创建角色", summary="创建角色")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建角色记录
    """
    try:
        return await role_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取角色信息", summary="获取角色信息")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个角色记录
    """
    try:
        obj = await role_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取角色列表", summary="获取角色列表")
async def gets(
    name: str | None = Query(None, description="角色名称"),
    code: str | None = Query(None, description="角色标识"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|name|code|create_time|update_time)$",
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
    分页查询角色列表
    """
    try:
        return await role_crud.get_multi(
            name=name,
            code=code,
            order_by=order_by or "-create_time",
            res_count=res_count,
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
            page=page,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新角色信息", summary="更新角色信息")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新角色信息，只更新传入的非空字段
    """
    try:
        return await role_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除角色", summary="删除角色")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除角色
    """
    try:
        return await role_crud.delete(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新角色", summary="创建或更新角色")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新角色
    """
    try:
        return await role_crud.upsert(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
