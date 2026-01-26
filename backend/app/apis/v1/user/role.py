from uuid import UUID

from fastapi import APIRouter, Query, Body, HTTPException, Path, Depends

from app.schemas.user.role import Create, Update, Out, OutList
from app.crud.user.role import role_crud
from app.schemas.base import BaseOut
from app.apis.deps import get_current_user, get_admin_user


app = APIRouter()


@app.get("/tree", response_model=list, description="获取角色树", summary="获取角色树")
async def get_tree(
    current_user: dict = Depends(get_current_user)
):
    """
    获取角色列表（树形结构，实际上角色是扁平的，但为了前端兼容性返回列表）
    """
    try:
        from app.models.user import UserRole
        
        # 获取所有角色
        roles = await UserRole.all().order_by('create_time')
        
        # 构建角色列表
        result = []
        for role in roles:
            role_dict = {
                'id': str(role.id),
                'code': role.code,
                'name': role.name,
                'description': role.description,
                'create_time': role.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                'update_time': role.update_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            result.append(role_dict)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}/routes", response_model=dict, description="获取角色的路由权限", summary="获取角色的路由权限")
async def get_role_routes(
    id: UUID = Path(..., description="角色ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取角色的路由权限列表（树形结构）
    
    返回格式：
    {
        "tree": [...],  # 完整的路由树结构
        "checked_keys": [...]  # 只包含叶子节点的ID列表（用于Tree的checkedKeys）
    }
    
    策略：
    - tree: 返回完整的路由树结构供显示
    - checked_keys: 只返回叶子节点（没有子节点的节点），让Tree组件自动计算父节点的半选状态
    """
    try:
        from app.models.user import UserRole, FrontendRoute
        
        # 获取角色及其关联的路由
        role = await UserRole.get_or_none(id=id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        # 获取角色的所有路由
        routes = await role.routes.all()
        route_ids = {str(route.id) for route in routes}
        
        # 构建路由树
        def build_tree(parent_id=None):
            """递归构建路由树"""
            result = []
            for route in routes:
                if route.parent_id == parent_id:
                    # 手动构建字典
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
        
        tree = build_tree(None)
        
        # 找出所有叶子节点（没有子节点的节点）
        def find_leaf_nodes(route_list):
            """递归查找所有叶子节点"""
            leaf_ids = []
            for route in route_list:
                if 'children' in route and route['children']:
                    # 有子节点，继续递归
                    leaf_ids.extend(find_leaf_nodes(route['children']))
                else:
                    # 没有子节点，是叶子节点
                    leaf_ids.append(route['id'])
            return leaf_ids
        
        checked_keys = find_leaf_nodes(tree)
        
        # 记录日志
        print(f"角色 {role.name} 权限查询：")
        print(f"  - 总共 {len(routes)} 个节点")
        print(f"  - 其中 {len(checked_keys)} 个叶子节点")
        
        return {
            'tree': tree,
            'checked_keys': checked_keys
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/{id}/routes", response_model=BaseOut, description="设置角色的路由权限", summary="设置角色的路由权限")
async def set_role_routes(
    id: UUID = Path(..., description="角色ID"),
    route_ids: list[str] = Body(..., description="路由ID列表"),
    current_user: dict = Depends(get_current_user)
):
    """
    设置角色的路由权限
    
    策略：自动补全父级菜单
    1. 接收前端传来的所有选中的路由ID
    2. 自动补全所有父级路由（确保菜单树完整）
    3. 保存完整的路由列表
    
    这样可以避免当用户只选择部分子菜单时，父级菜单丢失的问题
    """
    try:
        from app.models.user import UserRole, FrontendRoute
        
        # 获取角色
        role = await UserRole.get_or_none(id=id)
        if not role:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        # 清除现有路由关联
        await role.routes.clear()
        
        if not route_ids:
            return BaseOut(message="权限设置成功", count=0)
        
        # 获取所有选中的路由
        selected_routes = await FrontendRoute.filter(id__in=route_ids).all()
        if len(selected_routes) != len(route_ids):
            raise HTTPException(status_code=400, detail="部分路由ID无效")
        
        # 收集所有需要保存的路由（包括父级）
        all_route_ids = set(route_ids)
        
        # 递归查找所有父级路由
        async def add_parent_routes(route_list):
            parent_ids = set()
            for route in route_list:
                if route.parent_id and str(route.parent_id) not in all_route_ids:
                    parent_ids.add(str(route.parent_id))
                    all_route_ids.add(str(route.parent_id))
            
            if parent_ids:
                parents = await FrontendRoute.filter(id__in=list(parent_ids)).all()
                if parents:
                    await add_parent_routes(parents)
        
        # 补全父级路由
        await add_parent_routes(selected_routes)
        
        # 获取所有路由（包括补全的父级）
        all_routes = await FrontendRoute.filter(id__in=list(all_route_ids)).all()
        
        # 保存路由关联
        await role.routes.add(*all_routes)
        
        # 记录日志
        print(f"角色 {role.name} 权限更新：")
        print(f"  - 前端传递了 {len(route_ids)} 个节点")
        print(f"  - 自动补全后保存了 {len(all_routes)} 个节点")
        
        return BaseOut(message="权限设置成功", count=len(all_routes))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("", response_model=Out, description="创建角色", summary="创建角色")
async def post(
    item: Create = Body(..., description="创建数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建角色记录
    """
    try:
        return await role_crud.create(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{id}", response_model=Out, description="获取角色信息", summary="获取角色信息")
async def get(
    id: UUID = Path(..., description="ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个角色记录
    """
    try:
        obj = await role_crud.get(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not obj:
        raise HTTPException(status_code=404, detail="数据不存在")
    return obj


@app.get("", response_model=OutList, description="获取角色列表", summary="获取角色列表")
async def gets(
    name: str | None = Query(None, description="角色名称"),
    code: str | None = Query(None, description="角色标识"),
    order_by: str | None = Query(
        "-create_time",
        description="排序字段",
        pattern="^(?:-)?(?:id|name|code|create_time|update_time)$",
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
    分页查询角色列表
    """
    try:
        return await role_crud.get_multi(
            name=name,
            code=code,
            order_by=order_by or "-create_time",
            res_count=res_count,
            create_time_start=create_time_start,
            create_time_end=create_time_end,
            update_time_start=update_time_start,
            update_time_end=update_time_end,
            page=page,
            limit=limit,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/{id}", response_model=Out, description="更新角色信息", summary="更新角色信息")
async def put(
    id: UUID = Path(..., description="主键ID"),
    item: Update = Body(..., description="更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    部分更新角色信息，只更新传入的非空字段
    """
    try:
        return await role_crud.update(id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/{id}", response_model=BaseOut, description="删除角色", summary="删除角色")
async def delete(
    id: UUID = Path(..., description="主键ID"),
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除角色
    """
    try:
        return await role_crud.delete(id)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upsert", response_model=Out, description="创建或更新角色", summary="创建或更新角色")
async def post_or_put(
    item: Create = Body(..., description="创建或更新数据"),
    current_user: dict = Depends(get_current_user)
):
    """
    创建或更新角色
    """
    try:
        return await role_crud.upsert(item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
