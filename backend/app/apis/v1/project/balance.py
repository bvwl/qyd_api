from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.project.balance import Create, Update, Out, OutList
from app.crud.project.balance import project_balance_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut


from app.apis.deps import get_current_user, get_admin_user, get_gm_user

app = APIRouter()


@app.post("", response_model=Out, description="创建项目余额", summary="创建项目余额")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建项目余额记录
    """
    try:
        return await project_balance_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取项目余额", summary="获取项目余额")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个项目余额记录
    """
    try:
        obj = await project_balance_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取项目余额列表", summary="获取项目余额列表")
async def gets(
    account_id: UUID | None = Query(None, description="关联账号ID"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|create_time|update_time)$",
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
    分页查询项目余额列表
    """
    try:
        if res_count:
            count = await project_balance_crud.get_count(
                account_id=account_id,
                create_time_start=create_time_start,
                create_time_end=create_time_end,
                update_time_start=update_time_start,
                update_time_end=update_time_end,
            )
        else:
            count = -1
        return await project_balance_crud.get_multi(
            account_id=account_id,
            order_by=order_by or "-create_time",
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
            page=page,
            limit=limit,
            res_count=res_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新项目余额", summary="更新项目余额")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新项目余额，只更新传入的非空字段
    """
    try:
        return await project_balance_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除项目余额", summary="删除项目余额")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    gm_user: dict = Depends(get_gm_user)
):
    """
    删除项目余额（需要GM或管理员权限）
    """
    try:
        await project_balance_crud.delete(id)
        return BaseOut(message="成功", count=1)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

