from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.project.wallet import Create, Update, Out, OutList
from app.crud.project.wallet import project_wallet_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut
from app.apis.deps import get_current_user, get_admin_user


app = APIRouter()


@app.post("", response_model=Out, description="创建项目钱包", summary="创建项目钱包")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建项目钱包记录
    """
    try:
        return await project_wallet_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取项目钱包", summary="获取项目钱包")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个项目钱包记录
    """
    try:
        obj = await project_wallet_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取项目钱包列表", summary="获取项目钱包列表")
async def gets(
    project_id: UUID | None = Query(None, description="所属项目ID"),
    chain: str | None = Query(None, description="链名称"),
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
    分页查询项目钱包列表
    根据用户角色返回不同的数据：
    - ADMIN/GM: 返回所有项目的钱包
    - IT/MANUAL: 只返回分配给该用户的项目的钱包
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
        
        return await project_wallet_crud.get_multi(
            project_id=project_id,
            chain=chain,
            order_by=order_by or "-create_time",
            res_count=res_count,
            create_time_start=parse_time(create_time_start),
            create_time_end=parse_time(create_time_end, True),
            update_time_start=parse_time(update_time_start),
            update_time_end=parse_time(update_time_end, True),
            page=page,
            limit=limit,
            user_project_ids=user_project_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新项目钱包", summary="更新项目钱包")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新项目钱包，只更新传入的非空字段
    """
    try:
        return await project_wallet_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除项目钱包", summary="删除项目钱包")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除项目钱包（仅管理员）
    """
    try:
        return await project_wallet_crud.delete(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新项目钱包", summary="创建或更新项目钱包")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新项目钱包（根据公钥唯一性）
    
    如果公钥已存在，则更新该钱包信息；否则创建新钱包
    """
    try:
        return await project_wallet_crud.upsert(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

