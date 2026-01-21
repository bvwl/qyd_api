from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.user.info import Create, Update, Out, OutList
from app.crud.user.user import user_crud
from app.utils.time_tool import parse_time
from app.schemas.base import BaseOut
from app.apis.deps import get_current_user
from app.core.tools import hashing


app = APIRouter()


@app.post("", response_model=Out, description="创建用户", summary="创建用户")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建用户记录
    - 自动使用bcrypt加密密码
    """
    try:
        data = item.model_dump()
        # 加密密码
        if 'password' in data and data['password']:
            data['password'] = hashing.hash(data['password'])
        return await user_crud.create(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取用户信息", summary="获取用户信息")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个用户记录
    """
    try:
        obj = await user_crud.get(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取用户列表", summary="获取用户列表")
async def gets(
    email: str | None = Query(None, description="邮箱"),
    status: int | None = Query(None, description="用户状态"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|email|status|create_time|update_time)$",
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
    分页查询用户列表
    """
    try:
        return await user_crud.get_multi(
            email=email,
            status=status,
            order_by=order_by or "-create_time",
            res_count=res_count,
            create_time_start=parse_time(create_time_start),
            create_time_end=parse_time(create_time_end, True),
            update_time_start=parse_time(update_time_start),
            update_time_end=parse_time(update_time_end, True),
            page=page,
            limit=limit,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新用户信息", summary="更新用户信息")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新用户信息，只更新传入的非空字段
    - 如果更新密码，自动使用bcrypt加密
    """
    try:
        data = item.model_dump(exclude_unset=True)
        # 如果包含密码，加密它
        if 'password' in data and data['password']:
            data['password'] = hashing.hash(data['password'])
        
        # 创建新的Update对象
        from pydantic import BaseModel
        class UpdateWithEncryptedPassword(BaseModel):
            pass
        
        # 直接传递加密后的数据
        res = await user_crud.get(id)
        if not res:
            raise HTTPException(status_code=404, detail='数据不存在')
        
        from app.models.user import UserInfo
        user = await UserInfo.get(id=id)
        
        # 分离关联字段
        role_ids = data.pop('role_ids', None)
        
        # 更新基本字段
        if data:
            await user.update_from_dict(data)
            await user.save()
        
        # 处理多对多关系
        if role_ids is not None:
            await user.roles.clear()
            if role_ids:
                from app.models.user import UserRole
                roles = []
                for role_id in role_ids:
                    role = await UserRole.get_or_none(id=role_id)
                    if role:
                        roles.append(role)
                if roles:
                    await user.roles.add(*roles)
        
        await user.fetch_related('roles', 'projects')
        return Out.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除用户", summary="删除用户")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    删除用户
    """
    try:
        return await user_crud.delete(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新用户", summary="创建或更新用户")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新用户
    - 自动使用bcrypt加密密码
    """
    try:
        data = item.model_dump()
        # 加密密码
        if 'password' in data and data['password']:
            data['password'] = hashing.hash(data['password'])
        
        # 分离关联字段
        role_ids = data.pop('role_ids', None)
        
        from app.models.user import UserInfo
        record, created = await UserInfo.get_or_create(
            defaults=data,
            email=item.email
        )
        
        if not created:
            update_data = {k: v for k, v in data.items() if k != 'email'}
            if update_data:
                await record.update_from_dict(update_data)
                await record.save()
        
        # 处理多对多关系
        if role_ids is not None:
            await record.roles.clear()
            if role_ids:
                from app.models.user import UserRole
                roles = []
                for role_id in role_ids:
                    role = await UserRole.get_or_none(id=role_id)
                    if role:
                        roles.append(role)
                if roles:
                    await record.roles.add(*roles)
        
        await record.fetch_related('roles', 'projects')
        return Out.model_validate(record)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

