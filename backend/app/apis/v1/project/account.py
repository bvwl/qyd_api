from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path

from app.schemas.project.account import Create, Update, Out, OutList
from app.crud.project.account import project_account_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut


app = APIRouter()


@app.post("", response_model=Out, description="创建项目账号", summary="创建项目账号")
async def post(item: Create = Body(..., description="创建数据")):
    """
    创建项目账号记录
    """
    try:
        return await project_account_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取项目账号", summary="获取项目账号")
async def get(id: UUID = Path(..., description="ID")):
    """
    获取单个项目账号记录
    """
    try:
        obj = await project_account_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取项目账号列表", summary="获取项目账号列表")
async def gets(
    account: str | None = Query(None, description="账号"),
    status: int | None = Query(None, description="账号状态"),
    account_type: int | None = Query(None, description="账号类型"),
    project_id: UUID | None = Query(None, description="所属项目ID"),
    server_info_id: UUID | None = Query(None, description="关联服务器信息ID"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|account|status|create_time|update_time)$",
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
    分页查询项目账号列表
    """
    try:
        if res_count:
            count = await project_account_crud.get_count(
                account=account,
                status=status,
                account_type=account_type,
                project_id=project_id,
                server_info_id=server_info_id,
                create_time_start=parse_time(create_time_start),
                create_time_end=parse_time(create_time_end, True),
                update_time_start=parse_time(update_time_start),
                update_time_end=parse_time(update_time_end, True),
            )
        else:
            count = -1
        return await project_account_crud.get_multi(
            account=account,
            status=status,
            account_type=account_type,
            project_id=project_id,
            server_info_id=server_info_id,
            order_by=order_by or "-create_time",
            create_time_start=parse_time(create_time_start),
            create_time_end=parse_time(create_time_end, True),
            update_time_start=parse_time(update_time_start),
            update_time_end=parse_time(update_time_end, True),
            page=page,
            limit=limit,
            res_count=res_count,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新项目账号", summary="更新项目账号")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
):
    """
    部分更新项目账号，只更新传入的非空字段
    """
    try:
        return await project_account_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除项目账号", summary="删除项目账号")
async def delete(id: UUID = Path(..., description="主键ID")):
    """
    删除项目账号
    """
    try:
        await project_account_crud.delete(id)
        return BaseOut(message="成功", count=1)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新项目账号", summary="创建或更新项目账号")
async def post_or_put(item: Create = Body(..., description="创建或更新数据")):
    """
    创建或更新项目账号
    """
    try:
        filter_kwargs = {
            "account": item.account,
            "project_id": item.project_id,
        }
        return await project_account_crud.upsert(filter_kwargs, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

