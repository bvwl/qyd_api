from uuid import UUID
from typing import List

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.project.account import Create, Update, Out, OutList
from app.crud.project.account import project_account_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut


from app.apis.deps import get_current_user, get_admin_user, get_gm_user

app = APIRouter()


@app.post("", response_model=Out, description="创建项目账号", summary="创建项目账号")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
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
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个项目账号记录
    """
    try:
        obj = await project_account_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
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
    server_id: UUID | None = Query(None, description="关联服务器信息ID"),
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
    current_user: dict = Depends(get_current_user)
):
    """
    分页查询项目账号列表
    根据用户角色返回不同的数据：
    - ADMIN/GM: 返回所有项目的账号
    - IT/MANUAL: 只返回分配给该用户的项目的账号
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
                from app.schemas.project.account import OutList
                return OutList(message='成功', count=0, num=0, items=[])
        
        return await project_account_crud.get_multi(
            account=account,
            status=status,
            account_type=account_type,
            project_id=project_id,
            server_id=server_id,
            order_by=order_by or "-create_time",
            create_time_start=parse_time(create_time_start),
            create_time_end=parse_time(create_time_end, True),
            update_time_start=parse_time(update_time_start),
            update_time_end=parse_time(update_time_end, True),
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


@app.put("/{id}", response_model=Out, description="更新项目账号", summary="更新项目账号")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新项目账号，只更新传入的非空字段
    """
    try:
        return await project_account_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除项目账号", summary="删除项目账号")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    删除项目账号
    - 用户可以删除自己有权限的项目下的账号
    - 管理员可以删除所有账号
    """
    try:
        from app.utils.data_permission import filter_by_user_projects, has_resource_access
        
        user_id = current_user['user_id']
        user_roles = current_user.get('roles', [])
        
        # 检查是否有访问项目的权限（项目账号属于项目资源）
        if not has_resource_access(user_roles, 'project'):
            raise HTTPException(status_code=403, detail="没有访问项目的权限")
        
        # 获取要删除的账号
        account = await project_account_crud.get(id)
        if not account:
            raise HTTPException(status_code=404, detail="账号不存在")
        
        # 检查项目权限
        allowed_project_ids = await filter_by_user_projects(user_id)
        
        # 如果不是全局权限（ADMIN/GM），检查是否有该项目的权限
        if allowed_project_ids is not None:
            if str(account.project_id) not in [str(pid) for pid in allowed_project_ids]:
                raise HTTPException(status_code=403, detail="没有权限删除该项目下的账号")
        
        # 执行删除
        await project_account_crud.delete(id)
        return BaseOut(message="成功", count=1)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=BaseOut, description="创建或更新项目账号（使用Redis队列）", summary="创建或更新项目账号")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新项目账号（使用Redis队列异步处理）
    根据 account 和 project_id 判断是否存在：
    - 如果存在，只更新传入的非空字段
    - 如果不存在，创建新记录
    
    数据会被添加到Redis队列，由后台worker异步处理
    """
    try:
        from app.utils.project_account_queue import project_account_queue
        from app.core.settings import REDIS_ENABLED
        
        if not REDIS_ENABLED:
            raise HTTPException(status_code=503, detail="Redis未启用，无法使用队列处理功能")
        
        # 转换为字典，使用mode='json'确保UUID和Enum都能被序列化
        data = item.model_dump(mode='json')
        
        # 添加到队列
        if await project_account_queue.add_to_queue(data):
            # 获取当前队列大小
            queue_size = await project_account_queue.get_queue_size()
            return BaseOut(
                message=f"成功添加到队列，当前队列大小: {queue_size}",
                count=1
            )
        else:
            raise HTTPException(status_code=500, detail="添加到队列失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch-upsert", response_model=BaseOut, description="批量创建或更新项目账号（使用Redis队列）", summary="批量创建或更新项目账号")
async def batch_upsert(
    items: List[Create] = Body(..., description="批量创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    批量创建或更新项目账号
    使用Redis队列异步处理，避免数据库压力和接口长时间占用
    """
    try:
        from app.utils.project_account_queue import project_account_queue
        from app.core.settings import REDIS_ENABLED
        
        if not REDIS_ENABLED:
            raise HTTPException(status_code=503, detail="Redis未启用，无法使用批量处理功能")
        
        # 将数据添加到Redis队列
        success_count = 0
        fail_count = 0
        
        for item in items:
            # 转换为字典，使用mode='json'确保UUID和Enum都能被序列化
            data = item.model_dump(mode='json')
            # 添加到队列
            if await project_account_queue.add_to_queue(data):
                success_count += 1
            else:
                fail_count += 1
        
        # 获取当前队列大小
        queue_size = await project_account_queue.get_queue_size()
        
        return BaseOut(
            message=f"成功添加 {success_count} 条数据到队列，失败 {fail_count} 条，当前队列大小: {queue_size}",
            count=success_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

