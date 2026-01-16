from uuid import UUID

from app.schemas.server.country import Create, Update, Out, OutList
from app.crud.server.country import server_country_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut
from fastapi import APIRouter, Query, Body, HTTPException, Path

app = APIRouter()


# 创建国家信息
@app.post("", response_model=Out, description='创建国家信息', summary='创建国家信息')
async def post(item: Create = Body(..., description='创建数据')):
    """
    创建国家信息记录
    """
    try:
        item.short_name = item.short_name.upper()
        return await server_country_crud.create(item.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 查询国家单个信息
@app.get("/{id}", response_model=Out, description='获取国家信息', summary='获取国家信息')
async def get(id: UUID = Path(..., description='ID')):
    """
    获取国家信息记录
    """
    try:
        obj = await server_country_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail='数据不存在')
    return obj


# 查询国家信息
@app.get("", response_model=OutList, description='获取国家信息', summary='获取国家信息')
async def gets(
        short_name: str | None = Query(None, description='国家简称'),
        status: int | None = Query(None, description='状态(1:正常,2:异常)'),
        order_by: str | None = Query('-create_time', description='排序字段',
                                     pattern='^(?:-)?(?:id|short_name|status|create_time|update_time)$'),
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
):
    try:
        if res_count:
            count = await server_country_crud.get_count(
                short_name=short_name.upper() if short_name else None,
                status=status,
                create_time_start=parse_time(create_time_start),
                create_time_end=parse_time(create_time_end, True),
                update_time_start=parse_time(update_time_start),
                update_time_end=parse_time(update_time_end, True),
            )
        else:
            count = -1
        items = await server_country_crud.get_multi(
            short_name=short_name.upper() if short_name else None,
            status=status,
            order_by=order_by,
            create_time_start=parse_time(create_time_start),
            create_time_end=parse_time(create_time_end, True),
            update_time_start=parse_time(update_time_start),
            update_time_end=parse_time(update_time_end, True),
            page=page,
            limit=limit
        )
        return OutList(message='成功', count=count, num=len(items), items=items)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 更新国家信息
@app.put("/{id}", response_model=Out, description='更新国家信息', summary='更新国家信息')
async def put(id: UUID = Path(..., description='主键ID'),
              item: Update = Body(..., description='更新数据'),
              ):
    """
    部分更新国家信息，只更新传入的非空字段
    """
    try:
        return await server_country_crud.update(id, item.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 删除国家信息
@app.delete("/{id}", response_model=BaseOut, description='删除国家信息', summary='删除国家信息')
async def delete(id: UUID = Path(..., description='主键ID')):
    """
    删除国家信息
    """
    try:
        ok = await server_country_crud.delete(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail='数据不存在')
    return BaseOut(message='成功', count=1)


# 创建或更新国家信息
@app.post("/upsert", response_model=Out, description='创建或更新国家信息', summary='创建或更新国家信息')
async def post_or_put(item: Create = Body(..., description='创建或更新数据')):
    """
    创建或更新国家信息
    """
    try:
        filter_kwargs = {
            "short_name": item.short_name.upper()
        }
        item.short_name = item.short_name.upper()
        return await server_country_crud.upsert(filter_kwargs, item.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
