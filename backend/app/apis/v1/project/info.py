from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.project.info import Create, Update, Out, OutList
from app.crud.project.info import project_info_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut
from app.apis.deps import get_current_user, get_admin_user, get_gm_user


app = APIRouter()


@app.post("", response_model=Out, description="创建项目信息", summary="创建项目信息")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建项目记录
    """
    try:
        return await project_info_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取项目信息", summary="获取项目信息")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个项目记录
    """
    try:
        obj = await project_info_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取项目信息列表", summary="获取项目信息列表")
async def gets(
    name: str | None = Query(None, description="项目名称"),
    status: int | None = Query(None, description="项目状态"),
    user_id: UUID | None = Query(None, description="关联用户ID（筛选该用户的项目）"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|name|status|create_time|update_time)$",
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
    分页查询项目列表
    根据用户角色返回不同的数据：
    - ADMIN/GM: 返回所有项目（可选择按用户筛选）
    - IT/MANUAL: 只返回分配给该用户的项目
    """
    try:
        from app.models.user import UserInfo
        
        # 获取当前登录用户ID
        current_user_id = current_user.get('user_id') or current_user.get('id')
        
        # 获取当前用户角色
        user = await UserInfo.get(id=current_user_id).prefetch_related('roles')
        user_roles = [role.code for role in user.roles]
        
        # 判断是否有全局查看权限（ADMIN或GM）
        has_global_access = any(role in ['ADMIN', 'GM'] for role in user_roles)
        
        # 确定要查询的用户项目范围
        filter_user_id = None
        user_project_ids = None
        
        if has_global_access:
            # 管理员/GM：如果指定了user_id参数，则按该用户筛选
            if user_id:
                filter_user_id = user_id
        else:
            # 非管理员：只能查看自己的项目，忽略user_id参数
            await user.fetch_related('projects')
            user_project_ids = [str(project.id) for project in user.projects]
        
        if res_count:
            count = await project_info_crud.get_count(
                name=name,
                status=status,
                create_time_start=parse_time(create_time_start),
                create_time_end=parse_time(create_time_end, True),
                update_time_start=parse_time(update_time_start),
                update_time_end=parse_time(update_time_end, True),
                user_id=filter_user_id,
                user_project_ids=user_project_ids,
            )
        else:
            count = -1
        return await project_info_crud.get_multi(
            name=name,
            status=status,
            order_by=order_by or "-create_time",
            create_time_start=parse_time(create_time_start),
            create_time_end=parse_time(create_time_end, True),
            update_time_start=parse_time(update_time_start),
            update_time_end=parse_time(update_time_end, True),
            page=page,
            limit=limit,
            res_count=res_count,
            user_id=filter_user_id,
            user_project_ids=user_project_ids,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新项目信息", summary="更新项目信息")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新项目信息，只更新传入的非空字段
    """
    try:
        return await project_info_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除项目信息", summary="删除项目信息")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    gm_user: dict = Depends(get_gm_user)
):
    """
    删除项目信息（需要GM或管理员权限）
    """
    try:
        await project_info_crud.delete(id)
        return BaseOut(message="成功", count=1)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新项目信息", summary="创建或更新项目信息")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新项目信息
    """
    try:
        return await project_info_crud.upsert(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

