"""
菜单管理 API
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.apis.deps import get_current_user, get_admin_user
from app.models.rbac_v2 import Menu, Status
from app.core.database import db_read, db_write
from app.schemas.base import BaseOut
from app.utils.rbac_v2 import build_menu_tree

app = APIRouter()


@app.get("/tree", summary="获取菜单树")
async def get_menu_tree(
    status: Optional[int] = Query(None, description="状态筛选"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取完整的菜单树
    """
    query = db_read(Menu)
    
    if status is not None:
        query = query.filter(status=status)
    
    menus = await query.all()
    tree = build_menu_tree(menus)
    
    return BaseOut(data=tree, count=len(menus))


@app.get("", summary="获取菜单列表")
async def get_menus(
    code: Optional[str] = Query(None, description="菜单编码"),
    title: Optional[str] = Query(None, description="菜单标题"),
    parent_id: Optional[str] = Query(None, description="父级菜单ID"),
    status: Optional[int] = Query(None, description="状态"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=1000, description="每页数量"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取菜单列表（分页）
    """
    query = db_read(Menu)
    
    if code:
        query = query.filter(code__icontains=code)
    if title:
        query = query.filter(title__icontains=title)
    if parent_id:
        query = query.filter(parent_id=parent_id)
    if status is not None:
        query = query.filter(status=status)
    
    # 总数
    total = await query.count()
    
    # 分页
    offset = (page - 1) * limit
    menus = await query.offset(offset).limit(limit).all()
    
    # 构建返回数据
    items = []
    for menu in menus:
        items.append({
            'id': str(menu.id),
            'code': menu.code,
            'title': menu.title,
            'path': menu.path,
            'component': menu.component,
            'icon': menu.icon,
            'sort': menu.sort,
            'parent_id': str(menu.parent_id) if menu.parent_id else None,
            'is_hidden': menu.is_hidden,
            'is_cache': menu.is_cache,
            'is_affix': menu.is_affix,
            'redirect': menu.redirect,
            'status': menu.status,
            'create_time': menu.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'update_time': menu.update_time.strftime("%Y-%m-%d %H:%M:%S"),
        })
    
    return BaseOut(data={'items': items, 'total': total})


@app.get("/{id}", summary="获取菜单详情")
async def get_menu(
    id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个菜单详情
    """
    menu = await db_read(Menu).get_or_none(id=id)
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    return BaseOut(data={
        'id': str(menu.id),
        'code': menu.code,
        'title': menu.title,
        'path': menu.path,
        'component': menu.component,
        'icon': menu.icon,
        'sort': menu.sort,
        'parent_id': str(menu.parent_id) if menu.parent_id else None,
        'is_hidden': menu.is_hidden,
        'is_cache': menu.is_cache,
        'is_affix': menu.is_affix,
        'redirect': menu.redirect,
        'status': menu.status,
        'create_time': menu.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        'update_time': menu.update_time.strftime("%Y-%m-%d %H:%M:%S"),
    })


@app.post("", summary="创建菜单")
async def create_menu(
    code: str,
    title: str,
    path: str,
    component: Optional[str] = None,
    icon: Optional[str] = None,
    sort: int = 0,
    parent_id: Optional[UUID] = None,
    is_hidden: bool = False,
    is_cache: bool = True,
    is_affix: bool = False,
    redirect: Optional[str] = None,
    admin_user: dict = Depends(get_admin_user)
):
    """
    创建新菜单（仅管理员）
    """
    # 检查编码是否已存在
    existing = await db_read(Menu).filter(code=code).exists()
    if existing:
        raise HTTPException(status_code=400, detail="菜单编码已存在")
    
    # 如果有父级菜单，检查是否存在
    if parent_id:
        parent = await db_read(Menu).get_or_none(id=parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="父级菜单不存在")
    
    # 创建菜单
    menu = await db_write(Menu).create(
        code=code,
        title=title,
        path=path,
        component=component,
        icon=icon,
        sort=sort,
        parent_id=parent_id,
        is_hidden=is_hidden,
        is_cache=is_cache,
        is_affix=is_affix,
        redirect=redirect,
    )
    
    return BaseOut(message="菜单创建成功", data={'id': str(menu.id)})


@app.put("/{id}", summary="更新菜单")
async def update_menu(
    id: UUID,
    code: Optional[str] = None,
    title: Optional[str] = None,
    path: Optional[str] = None,
    component: Optional[str] = None,
    icon: Optional[str] = None,
    sort: Optional[int] = None,
    parent_id: Optional[UUID] = None,
    is_hidden: Optional[bool] = None,
    is_cache: Optional[bool] = None,
    is_affix: Optional[bool] = None,
    redirect: Optional[str] = None,
    status: Optional[int] = None,
    admin_user: dict = Depends(get_admin_user)
):
    """
    更新菜单（仅管理员）
    """
    menu = await db_read(Menu).get_or_none(id=id)
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    # 检查编码是否重复
    if code and code != menu.code:
        existing = await db_read(Menu).filter(code=code).exists()
        if existing:
            raise HTTPException(status_code=400, detail="菜单编码已存在")
    
    # 更新字段
    update_data = {}
    if code is not None:
        update_data['code'] = code
    if title is not None:
        update_data['title'] = title
    if path is not None:
        update_data['path'] = path
    if component is not None:
        update_data['component'] = component
    if icon is not None:
        update_data['icon'] = icon
    if sort is not None:
        update_data['sort'] = sort
    if parent_id is not None:
        update_data['parent_id'] = parent_id
    if is_hidden is not None:
        update_data['is_hidden'] = is_hidden
    if is_cache is not None:
        update_data['is_cache'] = is_cache
    if is_affix is not None:
        update_data['is_affix'] = is_affix
    if redirect is not None:
        update_data['redirect'] = redirect
    if status is not None:
        update_data['status'] = status
    
    if update_data:
        await db_write(Menu).filter(id=id).update(**update_data)
    
    return BaseOut(message="菜单更新成功")


@app.delete("/{id}", summary="删除菜单")
async def delete_menu(
    id: UUID,
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除菜单（仅管理员）
    """
    menu = await db_read(Menu).get_or_none(id=id)
    if not menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    # 检查是否有子菜单
    has_children = await db_read(Menu).filter(parent_id=id).exists()
    if has_children:
        raise HTTPException(status_code=400, detail="该菜单下有子菜单，无法删除")
    
    # 删除菜单
    await db_write(Menu).filter(id=id).delete()
    
    return BaseOut(message="菜单删除成功")
