from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path

from app.schemas.user.log import Create, Update, Out, OutList
from app.crud.user.log import log_crud
from app.schemas.base import BaseOut


app = APIRouter()


@app.post("", response_model=Out, description="创建日志", summary="创建日志")
async def post(item: Create = Body(..., description="创建数据")):
    """
    创建日志记录
    """
    try:
        return await log_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取日志信息", summary="获取日志信息")
async def get(id: UUID = Path(..., description="ID")):
    """
    获取单个日志记录
    """
    try:
        obj = await log_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取日志列表", summary="获取日志列表")
async def gets(
    user_id: UUID | None = Query(None, description="用户ID"),
    action: int | None = Query(None, description="操作类型"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|user_id|action|create_time|update_time)$",
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
    分页查询日志列表
    """
    try:
        return await log_crud.get_multi(
            user_id=user_id,
            action=action,
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


@app.put("/{id}", response_model=Out, description="更新日志信息", summary="更新日志信息")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
):
    """
    部分更新日志信息，只更新传入的非空字段
    """
    try:
        return await log_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除日志", summary="删除日志")
async def delete(id: UUID = Path(..., description="主键ID")):
    """
    删除日志
    """
    try:
        return await log_crud.delete(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
