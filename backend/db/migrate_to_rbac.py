"""
迁移到新的 RBAC 系统
"""
import asyncio
from uuid import UUID
from tortoise import Tortoise

# 导入旧模型
from app.models.user import FrontendRoute, UserRole as OldRole, RouteType

# 导入新模型
from app.models.rbac import Permission, Menu, Role, PermissionType, DataScope, Status
from app.core.settings import settings


async def init_db():
    """初始化数据库连接"""
    await Tortoise.init(
        db_url=f"mysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}",
        modules={"models": ["app.models.user", "app.models.rbac"]}
    )
    await Tortoise.generate_schemas()


async def migrate_routes_to_menus_and_permissions():
    """
    将现有的 frontend_routes 迁移到新的 menus 和 permissions
    """
    print("=" * 60)
    print("开始迁移路由到菜单和权限")
    print("=" * 60)
    
    routes = await FrontendRoute.all()
    print(f"找到 {len(routes)} 个路由")
    
    # 存储路由ID到菜单ID的映射
    route_to_menu = {}
    
    # 存储权限
    permissions_created = []
    
    # 第一遍：创建菜单和权限
    for route in routes:
        print(f"\n处理路由: {route.title} ({route.name})")
        
        # 创建菜单
        menu = await Menu.create(
            name=route.name,
            title=route.title,
            path=route.path,
            component=route.component,
            icon=route.icon,
            parent_id=None,  # 先不设置父级，第二遍处理
            sort=route.sort,
            is_hidden=route.is_hidden,
            is_cache=route.is_cache,
            is_affix=route.is_affix,
            redirect=route.redirect,
            status=route.status
        )
        route_to_menu[route.id] = menu.id
        print(f"  ✓ 创建菜单: {menu.title}")
        
        # 如果有权限标识，创建权限
        if route.permission:
            # 解析权限标识：user:create -> resource=user, action=create
            parts = route.permission.split(':')
            resource = parts[0] if len(parts) > 0 else 'unknown'
            action = parts[1] if len(parts) > 1 else 'view'
            
            # 检查权限是否已存在
            existing_perm = await Permission.get_or_none(code=route.permission)
            if existing_perm:
                print(f"  - 权限已存在: {route.permission}")
                permission = existing_perm
            else:
                # 确定权限类型
                if route.route_type == RouteType.API:
                    perm_type = PermissionType.API
                elif route.route_type == RouteType.BUTTON:
                    perm_type = PermissionType.BUTTON
                else:
                    perm_type = PermissionType.API
                
                permission = await Permission.create(
                    code=route.permission,
                    name=route.title,
                    resource=resource,
                    action=action,
                    permission_type=perm_type,
                    api_method=route.api_method,
                    api_path=route.api_path,
                    status=route.status
                )
                permissions_created.append(permission)
                print(f"  ✓ 创建权限: {permission.code}")
            
            # 菜单关联权限
            menu.required_permission = permission.code
            await menu.save()
            print(f"  ✓ 菜单关联权限: {permission.code}")
    
    # 第二遍：设置菜单的父级关系
    print("\n" + "=" * 60)
    print("设置菜单父级关系")
    print("=" * 60)
    
    for route in routes:
        if route.parent_id:
            menu_id = route_to_menu.get(route.id)
            parent_menu_id = route_to_menu.get(route.parent_id)
            
            if menu_id and parent_menu_id:
                menu = await Menu.get(id=menu_id)
                menu.parent_id = parent_menu_id
                await menu.save()
                print(f"✓ 设置 {menu.title} 的父级")
    
    print("\n" + "=" * 60)
    print("迁移完成！")
    print(f"  - 创建菜单: {len(route_to_menu)} 个")
    print(f"  - 创建权限: {len(permissions_created)} 个")
    print("=" * 60)


async def migrate_roles():
    """
    迁移角色
    """
    print("\n" + "=" * 60)
    print("开始迁移角色")
    print("=" * 60)
    
    old_roles = await OldRole.all()
    print(f"找到 {len(old_roles)} 个角色")
    
    role_mapping = {}
    
    for old_role in old_roles:
        print(f"\n处理角色: {old_role.name} ({old_role.code})")
        
        # 检查角色是否已存在
        existing_role = await Role.get_or_none(code=old_role.code)
        if existing_role:
            print(f"  - 角色已存在: {old_role.code}")
            role = existing_role
        else:
            # 确定数据范围
            if old_role.code == 'ADMIN':
                data_scope = DataScope.ALL
                level = 100
                is_system = True
            elif old_role.code == 'GM':
                data_scope = DataScope.DEPT_AND_CHILD
                level = 50
                is_system = True
            else:
                data_scope = DataScope.SELF
                level = 0
                is_system = False
            
            # 创建新角色
            role = await Role.create(
                name=old_role.name,
                code=old_role.code,
                description=old_role.description,
                data_scope=data_scope,
                level=level,
                is_system=is_system,
                status=Status.OK
            )
            print(f"  ✓ 创建角色: {role.name}")
        
        role_mapping[old_role.id] = role.id
        
        # 迁移角色的路由关联到菜单和权限
        old_routes = await old_role.routes.all()
        print(f"  - 角色有 {len(old_routes)} 个路由")
        
        for old_route in old_routes:
            # 查找对应的菜单
            menu = await Menu.get_or_none(name=old_route.name)
            if menu:
                await role.menus.add(menu)
                print(f"    ✓ 关联菜单: {menu.title}")
            
            # 查找对应的权限
            if old_route.permission:
                permission = await Permission.get_or_none(code=old_route.permission)
                if permission:
                    await role.permissions.add(permission)
                    print(f"    ✓ 关联权限: {permission.code}")
    
    print("\n" + "=" * 60)
    print("角色迁移完成！")
    print(f"  - 迁移角色: {len(role_mapping)} 个")
    print("=" * 60)
    
    return role_mapping


async def init_default_permissions():
    """
    初始化默认权限
    """
    print("\n" + "=" * 60)
    print("初始化默认权限")
    print("=" * 60)
    
    # 定义默认权限
    default_permissions = [
        # 用户管理
        {"code": "user:view", "name": "查看用户", "resource": "user", "action": "view"},
        {"code": "user:create", "name": "创建用户", "resource": "user", "action": "create"},
        {"code": "user:edit", "name": "编辑用户", "resource": "user", "action": "edit"},
        {"code": "user:delete", "name": "删除用户", "resource": "user", "action": "delete"},
        {"code": "user:export", "name": "导出用户", "resource": "user", "action": "export"},
        
        # 角色管理
        {"code": "role:view", "name": "查看角色", "resource": "role", "action": "view"},
        {"code": "role:create", "name": "创建角色", "resource": "role", "action": "create"},
        {"code": "role:edit", "name": "编辑角色", "resource": "role", "action": "edit"},
        {"code": "role:delete", "name": "删除角色", "resource": "role", "action": "delete"},
        
        # 权限管理
        {"code": "permission:view", "name": "查看权限", "resource": "permission", "action": "view"},
        {"code": "permission:assign", "name": "分配权限", "resource": "permission", "action": "assign"},
        
        # 菜单管理
        {"code": "menu:view", "name": "查看菜单", "resource": "menu", "action": "view"},
        {"code": "menu:create", "name": "创建菜单", "resource": "menu", "action": "create"},
        {"code": "menu:edit", "name": "编辑菜单", "resource": "menu", "action": "edit"},
        {"code": "menu:delete", "name": "删除菜单", "resource": "menu", "action": "delete"},
        
        # 项目管理
        {"code": "project:view", "name": "查看项目", "resource": "project", "action": "view"},
        {"code": "project:create", "name": "创建项目", "resource": "project", "action": "create"},
        {"code": "project:edit", "name": "编辑项目", "resource": "project", "action": "edit"},
        {"code": "project:delete", "name": "删除项目", "resource": "project", "action": "delete"},
        {"code": "project:export", "name": "导出项目", "resource": "project", "action": "export"},
        
        # 服务器管理
        {"code": "server:view", "name": "查看服务器", "resource": "server", "action": "view"},
        {"code": "server:create", "name": "创建服务器", "resource": "server", "action": "create"},
        {"code": "server:edit", "name": "编辑服务器", "resource": "server", "action": "edit"},
        {"code": "server:delete", "name": "删除服务器", "resource": "server", "action": "delete"},
        
        # 邮件管理
        {"code": "mail:view", "name": "查看邮件", "resource": "mail", "action": "view"},
        {"code": "mail:send", "name": "发送邮件", "resource": "mail", "action": "send"},
        {"code": "mail:delete", "name": "删除邮件", "resource": "mail", "action": "delete"},
    ]
    
    created_count = 0
    for perm_data in default_permissions:
        existing = await Permission.get_or_none(code=perm_data["code"])
        if not existing:
            await Permission.create(
                **perm_data,
                permission_type=PermissionType.API,
                status=Status.OK
            )
            created_count += 1
            print(f"  ✓ 创建权限: {perm_data['code']}")
        else:
            print(f"  - 权限已存在: {perm_data['code']}")
    
    print("\n" + "=" * 60)
    print(f"默认权限初始化完成！创建了 {created_count} 个权限")
    print("=" * 60)


async def main():
    """主函数"""
    try:
        # 初始化数据库
        await init_db()
        
        # 执行迁移
        await migrate_routes_to_menus_and_permissions()
        await migrate_roles()
        await init_default_permissions()
        
        print("\n" + "=" * 60)
        print("✅ 所有迁移完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
