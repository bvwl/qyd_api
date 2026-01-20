from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path

from app.schemas.user.route import Create, Update, Out, OutList
from app.crud.user.route import route_crud
from app.schemas.base import BaseOut


app = APIRouter()


@app.post("", response_model=Out, description="创建路由", summary="创建路由")
async def post(item: Create = Body(..., description="创建数据")):
    """
    创建路由记录
    """
    try:
        return await route_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取路由信息", summary="获取路由信息")
async def get(id: UUID = Path(..., description="ID")):
    """
    获取单个路由记录
    """
    try:
        obj = await route_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取路由列表", summary="获取路由列表")
async def gets(
    name: str | None = Query(None, description="路由名称"),
    path: str | None = Query(None, description="路由路径"),
    status: int | None = Query(None, description="状态"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|name|path|status|sort|create_time|update_time)$",
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
):
    """
    分页查询路由列表
    """
    try:
        return await route_crud.get_multi(
            name=name,
            path=path,
            status=status,
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新路由信息", summary="更新路由信息")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
):
    """
    部分更新路由信息，只更新传入的非空字段
    """
    try:
        return await route_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除路由", summary="删除路由")
async def delete(id: UUID = Path(..., description="主键ID")):
    """
    删除路由
    """
    try:
        return await route_crud.delete(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新路由", summary="创建或更新路由")
async def post_or_put(item: Create = Body(..., description="创建或更新数据")):
    """
    创建或更新路由
    """
    try:
        return await route_crud.upsert(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
