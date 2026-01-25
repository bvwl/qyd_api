from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.user.route import Create, Update, Out, OutList
from app.crud.user.route import route_crud
from app.schemas.base import BaseOut
from app.apis.deps import get_current_user, get_admin_user
from app.utils.time_tool import parse_time


app = APIRouter()


@app.get("/tree", response_model=list, description="获取路由树", summary="获取路由树")
async def get_tree(
    status: int | None = Query(None, description="状态筛选"),
    route_type: int | None = Query(None, description="路由类型筛选"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取路由树形结构
    """
    try:
        from app.models.user import FrontendRoute
        
        # 构建查询条件
        query = FrontendRoute.all()
        if status is not None:
            query = query.filter(status=status)
        if route_type is not None:
            query = query.filter(route_type=route_type)
        
        # 获取所有路由，预加载关联数据
        routes = await query.prefetch_related('roles').order_by('sort', 'create_time')
        
        # 构建路由树
        def build_tree(parent_id=None):
            """递归构建路由树"""
            result = []
            for route in routes:
                if route.parent_id == parent_id:
                    # 手动构建字典，避免Pydantic验证问题
                    route_dict = {
                        'id': str(route.id),
                        'name': route.name,
                        'path': route.path,
                        'component': route.component,
                        'title': route.title,
                        'icon': route.icon,
                        'sort': route.sort,
                        'redirect': route.redirect,
                        'is_hidden': route.is_hidden,
                        'is_cache': route.is_cache,
                        'is_affix': route.is_affix,
                        'route_type': route.route_type,
                        'permission': route.permission,
                        'api_method': route.api_method,
                        'api_path': route.api_path,
                        'status': route.status,
                        'parent_id': str(route.parent_id) if route.parent_id else None,
                        'create_time': route.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'update_time': route.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    children = build_tree(route.id)
                    if children:
                        route_dict['children'] = children
                    result.append(route_dict)
            return result
        
        return build_tree(None)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user-routes", response_model=list, description="获取当前用户的路由权限", summary="获取当前用户的路由权限")
async def get_user_routes(
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前登录用户的路由权限（树形结构）
    根据用户的角色，返回该用户有权访问的所有路由
    """
    try:
        from app.models.user import UserInfo, FrontendRoute
        
        # 获取用户ID（兼容两种格式）
        user_id = current_user.get('user_id') or current_user.get('id')
        if not user_id:
            raise HTTPException(status_code=401, detail="无法获取用户ID")
        
        # 获取当前用户及其角色和路由
        user = await UserInfo.get(id=user_id).prefetch_related('roles__routes')
        
        # 收集所有路由ID（去重）
        route_ids = set()
        for role in user.roles:
            for route in role.routes:
                if route.status == 1:  # 只包含正常状态的路由
                    route_ids.add(route.id)
        
        if not route_ids:
            return []
        
        # 获取所有相关路由
        routes = await FrontendRoute.filter(id__in=list(route_ids)).order_by('sort', 'create_time')
        
        # 构建路由树
        def build_tree(parent_id=None):
            """递归构建路由树"""
            result = []
            for route in routes:
                if route.parent_id == parent_id:
                    route_dict = {
                        'id': str(route.id),
                        'name': route.name,
                        'path': route.path,
                        'component': route.component,
                        'title': route.title,
                        'icon': route.icon,
                        'sort': route.sort,
                        'redirect': route.redirect,
                        'is_hidden': route.is_hidden,
                        'is_cache': route.is_cache,
                        'is_affix': route.is_affix,
                        'route_type': route.route_type,
                        'permission': route.permission,
                        'api_method': route.api_method,
                        'api_path': route.api_path,
                        'status': route.status,
                        'parent_id': str(route.parent_id) if route.parent_id else None,
                        'create_time': route.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'update_time': route.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    children = build_tree(route.id)
                    if children:
                        route_dict['children'] = children
                    result.append(route_dict)
            return result
        
        return build_tree(None)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("", response_model=Out, description="创建路由", summary="创建路由")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建路由记录
    """
    try:
        return await route_crud.create(item)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取路由信息", summary="获取路由信息")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个路由记录
    """
    try:
        obj = await route_crud.get(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取路由列表", summary="获取路由列表")
async def gets(
    name: str | None = Query(None, description="路由名称"),
    path: str | None = Query(None, description="路由路径"),
    status: int | None = Query(None, description="状态"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|name|path|status|sort|create_time|update_time)$",
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
    分页查询路由列表
    """
    try:
        return await route_crud.get_multi(
            name=name,
            path=path,
            status=status,
            order_by=order_by or "-create_time",
            res_count=res_count,
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
            page=page,
            limit=limit,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新路由信息", summary="更新路由信息")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新路由信息，只更新传入的非空字段
    """
    try:
        return await route_crud.update(id, item)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除路由", summary="删除路由")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除路由
    """
    try:
        return await route_crud.delete(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新路由", summary="创建或更新路由")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新路由
    """
    try:
        return await route_crud.upsert(item)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
