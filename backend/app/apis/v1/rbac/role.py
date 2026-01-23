"""
角色管理 API
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List

from app.apis.deps import get_current_user, get_admin_user
from app.models.rbac_v2 import Role, Menu, DataScope, Status
from app.core.database import db_read, db_write
from app.schemas.base import BaseOut

app = APIRouter()


@app.get("", summary="获取角色列表")
async def get_roles(
    code: Optional[str] = Query(None, description="角色编码"),
    name: Optional[str] = Query(None, description="角色名称"),
    status: Optional[int] = Query(None, description="状态"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(10, ge=1, le=1000, description="每页数量"),
    current_user: dict = Depends(get_current_user)
):
    """
    获取角色列表（分页）
    """
    query = db_read(Role)
    
    if code:
        query = query.filter(code__icontains=code)
    if name:
        query = query.filter(name__icontains=name)
    if status is not None:
        query = query.filter(status=status)
    
    # 总数
    total = await query.count()
    
    # 分页
    offset = (page - 1) * limit
    roles = await query.offset(offset).limit(limit).all()
    
    # 构建返回数据
    items = []
    for role in roles:
        items.append({
            'id': str(role.id),
            'code': role.code,
            'name': role.name,
            'description': role.description,
            'level': role.level,
            'data_scope': role.data_scope,
            'is_system': role.is_system,
            'status': role.status,
            'create_time': role.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'update_time': role.update_time.strftime("%Y-%m-%d %H:%M:%S"),
        })
    
    return BaseOut(data={'items': items, 'total': total})


@app.get("/{id}", summary="获取角色详情")
async def get_role(
    id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    获取单个角色详情
    """
    role = await db_read(Role).get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    return BaseOut(data={
        'id': str(role.id),
        'code': role.code,
        'name': role.name,
        'description': role.description,
        'level': role.level,
        'data_scope': role.data_scope,
        'is_system': role.is_system,
        'status': role.status,
        'create_time': role.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        'update_time': role.update_time.strftime("%Y-%m-%d %H:%M:%S"),
    })


@app.get("/{id}/menus", summary="获取角色的菜单")
async def get_role_menus(
    id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """
    获取角色关联的所有菜单
    
    返回格式：
    {
        "tree": [...],  # 完整的菜单树结构
        "checked_keys": [...]  # 只包含叶子节点的ID列表（用于Tree的checkedKeys）
    }
    
    策略：
    - tree: 返回完整的菜单树结构供显示
    - checked_keys: 只返回叶子节点（没有子节点的节点），让Tree组件自动计算父节点的半选状态
    """
    role = await db_read(Role).get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 获取角色的所有菜单
    menus = await role.menus.all()
    
    # 构建菜单树
    def build_tree(parent_id=None):
        """递归构建菜单树"""
        result = []
        for menu in menus:
            if menu.parent_id == parent_id:
                menu_dict = {
                    'id': str(menu.id),
                    'code': menu.code,
                    'name': menu.name,
                    'title': menu.title,
                    'path': menu.path,
                    'component': menu.component,
                    'icon': menu.icon,
                    'sort': menu.sort,
                    'type': menu.type,
                    'is_hidden': menu.is_hidden,
                    'is_cache': menu.is_cache,
                    'is_affix': menu.is_affix,
                    'status': menu.status,
                    'parent_id': str(menu.parent_id) if menu.parent_id else None,
                    'create_time': menu.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'update_time': menu.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                children = build_tree(menu.id)
                if children:
                    menu_dict['children'] = children
                result.append(menu_dict)
        return result
    
    tree = build_tree(None)
    
    # 找出所有叶子节点（没有子节点的节点）
    def find_leaf_nodes(menu_list):
        """递归查找所有叶子节点"""
        leaf_ids = []
        for menu in menu_list:
            if 'children' in menu and menu['children']:
                # 有子节点，继续递归
                leaf_ids.extend(find_leaf_nodes(menu['children']))
            else:
                # 没有子节点，是叶子节点
                leaf_ids.append(menu['id'])
        return leaf_ids
    
    checked_keys = find_leaf_nodes(tree)
    
    return BaseOut(data={
        'tree': tree,
        'checked_keys': checked_keys
    })


@app.post("/{id}/menus", summary="设置角色的菜单")
async def set_role_menus(
    id: UUID,
    menu_ids: List[str],
    admin_user: dict = Depends(get_admin_user)
):
    """
    设置角色的菜单
    
    策略：
    1. 接收前端传来的所有选中的菜单ID（包括半选的父节点）
    2. 自动补全所有父级菜单（确保菜单树完整）
    3. 保存完整的菜单列表
    
    参数：
        menu_ids: 选中的菜单ID列表（包括半选节点）
    """
    role = await db_read(Role).get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 清除现有菜单关联
    await role.menus.clear()
    
    if not menu_ids:
        return BaseOut(message="菜单设置成功", count=0)
    
    # 获取所有选中的菜单
    selected_menus = await db_read(Menu).filter(id__in=menu_ids).all()
    if len(selected_menus) != len(menu_ids):
        raise HTTPException(status_code=400, detail="部分菜单ID无效")
    
    # 收集所有需要保存的菜单（包括父级）
    all_menu_ids = set(menu_ids)
    
    # 递归查找所有父级菜单
    async def add_parent_menus(menu_list):
        parent_ids = set()
        for menu in menu_list:
            if menu.parent_id and str(menu.parent_id) not in all_menu_ids:
                parent_ids.add(str(menu.parent_id))
                all_menu_ids.add(str(menu.parent_id))
        
        if parent_ids:
            parents = await db_read(Menu).filter(id__in=list(parent_ids)).all()
            if parents:
                await add_parent_menus(parents)
    
    # 补全父级菜单
    await add_parent_menus(selected_menus)
    
    # 获取所有菜单（包括补全的父级）
    all_menus = await db_read(Menu).filter(id__in=list(all_menu_ids)).all()
    
    # 保存菜单关联
    await role.menus.add(*all_menus)
    
    return BaseOut(message="菜单设置成功", count=len(all_menus))

@app.post("", summary="创建角色")
async def create_role(
    code: str,
    name: str,
    description: Optional[str] = None,
    level: int = 0,
    data_scope: int = DataScope.SELF,
    admin_user: dict = Depends(get_admin_user)
):
    """
    创建新角色（仅管理员）
    """
    # 检查编码是否已存在
    existing = await db_read(Role).filter(code=code).exists()
    if existing:
        raise HTTPException(status_code=400, detail="角色编码已存在")
    
    # 创建角色
    role = await db_write(Role).create(
        code=code,
        name=name,
        description=description,
        level=level,
        data_scope=data_scope,
    )
    
    return BaseOut(message="角色创建成功", data={'id': str(role.id)})


@app.put("/{id}", summary="更新角色")
async def update_role(
    id: UUID,
    code: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    level: Optional[int] = None,
    data_scope: Optional[int] = None,
    status: Optional[int] = None,
    admin_user: dict = Depends(get_admin_user)
):
    """
    更新角色（仅管理员）
    """
    role = await db_read(Role).get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 系统角色不允许修改编码
    if role.is_system and code and code != role.code:
        raise HTTPException(status_code=400, detail="系统角色不允许修改编码")
    
    # 检查编码是否重复
    if code and code != role.code:
        existing = await db_read(Role).filter(code=code).exists()
        if existing:
            raise HTTPException(status_code=400, detail="角色编码已存在")
    
    # 更新字段
    update_data = {}
    if code is not None:
        update_data['code'] = code
    if name is not None:
        update_data['name'] = name
    if description is not None:
        update_data['description'] = description
    if level is not None:
        update_data['level'] = level
    if data_scope is not None:
        update_data['data_scope'] = data_scope
    if status is not None:
        update_data['status'] = status
    
    if update_data:
        await db_write(Role).filter(id=id).update(**update_data)
    
    return BaseOut(message="角色更新成功")


@app.delete("/{id}", summary="删除角色")
async def delete_role(
    id: UUID,
    admin_user: dict = Depends(get_admin_user)
):
    """
    删除角色（仅管理员）
    """
    role = await db_read(Role).get_or_none(id=id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 系统角色不允许删除
    if role.is_system:
        raise HTTPException(status_code=400, detail="系统角色不允许删除")
    
    # 删除角色
    await db_write(Role).filter(id=id).delete()
    
    return BaseOut(message="角色删除成功")
