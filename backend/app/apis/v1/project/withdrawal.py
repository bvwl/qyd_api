"""
项目提现 API
"""
from uuid import UUID
from typing import List

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.project.withdrawal import Create, Update, Out, OutList
from app.crud.project.withdrawal import project_withdrawal_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut
from app.apis.deps import get_current_user, get_gm_user

app = APIRouter()


@app.post("", response_model=Out, description="创建项目提现记录", summary="创建项目提现记录")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建项目提现记录
    - 可以只传入部分字段（platform_coin、stable_coin、rmb）
    - 自动计算变动和记录历史
    """
    try:
        return await project_withdrawal_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取项目提现记录", summary="获取项目提现记录")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """获取单条项目提现记录"""
    try:
        obj = await project_withdrawal_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("/project/{project_id}", response_model=Out, description="根据项目ID获取提现记录", summary="根据项目ID获取提现记录")
async def get_by_project(
    project_id: UUID = Path(..., description="项目ID"),
    current_user: dict = Depends(get_current_user)
):
    """根据项目ID获取提现记录"""
    try:
        obj = await project_withdrawal_crud.get_by_project(project_id)
        if not obj:
            raise HTTPException(status_code=404, detail="该项目暂无提现记录")
        return obj
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("", response_model=OutList, description="获取项目提现记录列表", summary="获取项目提现记录列表")
async def gets(
    project_id: UUID | None = Query(None, description="项目ID"),
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
    分页查询项目提现记录列表
    根据用户角色返回不同的数据：
    - ADMIN/GM: 返回所有项目的提现记录
    - IT/MANUAL: 只返回分配给该用户的项目的提现记录
    """
    try:
        from app.utils.data_permission import filter_by_user_projects
        
        # 获取用户ID
        user_id = current_user.get('user_id') or current_user.get('id')
        
        # 根据用户权限过滤项目
        user_project_ids = await filter_by_user_projects(user_id)
        
        # 如果指定了project_id，需要检查用户是否有权限访问该项目
        if project_id and user_project_ids is not None:
            if str(project_id) not in user_project_ids:
                # 用户没有权限访问该项目
                return OutList(message='成功', count=0, num=0, items=[])
        
        return await project_withdrawal_crud.get_multi(
            project_id=project_id,
            order_by=order_by or "-create_time",
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
            page=page,
            limit=limit,
            res_count=res_count,
            user_project_ids=user_project_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新项目提现记录", summary="更新项目提现记录")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新项目提现记录，只更新传入的非空字段
    - 可以只更新部分字段（platform_coin、stable_coin、rmb）
    - 自动计算变动和记录历史
    """
    try:
        return await project_withdrawal_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除项目提现记录", summary="删除项目提现记录")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    current_user: dict = Depends(get_gm_user)
):
    """
    删除项目提现记录
    - 只有 ADMIN/GM 可以删除
    """
    try:
        await project_withdrawal_crud.delete(id)
        return BaseOut(message="成功", count=1)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
