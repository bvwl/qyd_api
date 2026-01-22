from uuid import UUID

from app.models.mail import EmailInfo
from app.schemas.mail.info import Create, Update, Out, OutList, EmailType
from app.crud.mail.info import email_info_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut
from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends
from app.apis.deps import get_current_user, get_admin_user

app = APIRouter()


def _mask_items(
        items: list[Out],
        hide_password: bool = True,
        hide_aux_password: bool = True,
        hide_server_ssh_port: bool = True,
) -> list[Out]:
    masked_items: list[Out] = []
    for item in items:
        data = Out.model_validate(item)
        if hide_password:
            data.password = ""
        if hide_aux_password:
            data.auxiliary_email_password = ""
        if hide_server_ssh_port and data.server is not None:
            data.server.ssh_port = None
        masked_items.append(data)
    return masked_items


# 创建邮箱信息
@app.post("", response_model=Out, description='创建邮箱信息', summary='创建邮箱信息')
async def post(
    item: Create = Body(..., description='创建数据'),
    current_user: dict = Depends(get_current_user)
):
    """
    创建邮箱信息记录
    """
    try:
        return await email_info_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 查询邮箱单个信息
@app.get("/{id}", response_model=Out, description='获取邮箱信息', summary='获取邮箱信息')
async def get(
    id: UUID = Path(..., description='ID'),
    current_user: dict = Depends(get_current_user)
):
    """
    获取邮箱信息记录
    """
    try:
        obj = await email_info_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail='数据不存在')
    return obj


# 查询邮箱信息
@app.get("", response_model=OutList, description='获取邮箱信息', summary='获取邮箱信息')
async def gets(
        email: str | None = Query(None, description='邮箱号'),
        status: int | None = Query(None, description='状态(1:正常,2:异常)'),
        server_id: UUID | None = Query(None, description='服务器ID'),
        email_type: EmailType | None = Query(None, description='邮箱类型'),
        order_by: str | None = Query('-create_time', description='排序字段',
                                     pattern='^(?:-)?(?:id|email|status|create_time|update_time)$'),
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
    try:
        result = await email_info_crud.get_multi(
            email=email,
            status=status,
            server_id=server_id,
            email_type=email_type,
            order_by=order_by,
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
            page=page,
            limit=limit,
            res_count=res_count
        )
        # 脱敏处理
        masked_items = _mask_items(
            result.items,
            hide_password=True,
            hide_aux_password=True,
            hide_server_ssh_port=True,
        )
        result.items = masked_items
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 更新邮箱信息
@app.put("/{id}", response_model=Out, description='更新邮箱信息', summary='更新邮箱信息')
async def put(
    id: UUID = Path(..., description='主键ID'),
    item: Update = Body(..., description='更新数据'),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新邮箱信息，只更新传入的非空字段
    """
    try:
        return await email_info_crud.update(id, item)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 删除邮箱信息
@app.delete("/{id}", response_model=BaseOut, description='删除邮箱信息', summary='删除邮箱信息')
async def delete(
    id: UUID = Path(..., description='主键ID'),
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除邮箱信息
    """
    try:
        await email_info_crud.delete(id)
        return BaseOut(message='成功', count=1)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 创建或更新邮箱信息
@app.post("/upsert", response_model=Out, description='创建或更新邮箱信息', summary='创建或更新邮箱信息')
async def post_or_put(
    item: Create = Body(..., description='创建或更新数据'),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新邮箱信息
    """
    try:
        return await email_info_crud.upsert(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 统一调整邮箱状态
@app.post("/status/batch-update", response_model=BaseOut, description="批量调整邮箱状态", summary="批量调整邮箱状态")
async def batch_update_status(
        from_status: int = Body(..., embed=True, description="原状态值"),
        to_status: int = Body(..., embed=True, description="目标状态值"),
        current_user: dict = Depends(get_current_user)
):
    """
    批量将邮箱状态从 from_status 调整为 to_status
    例如：统一将状态为 2 的邮箱调整为 1
    """
    try:
        updated = await EmailInfo.filter(status=from_status).update(status=to_status)
        return BaseOut(message="成功", count=updated)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
