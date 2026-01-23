"""
初始化 RBAC v2 数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 加载环境变量
from dotenv import load_dotenv
env_path = backend_dir / '.env'
load_dotenv(env_path)

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM
from app.models.rbac_v2 import Menu, Permission, Role, DataScope, PermissionType, Status
from app.models.user import UserInfo
from app.core.tools import hashing


async def init_menus():
    """初始化菜单"""
    print("初始化菜单...")
    
    menus_data = [
        # 一级菜单
        {
            'code': 'dashboard',
            'title': '仪表盘',
            'path': '/dashboard',
            'component': 'views/Dashboard',
            'icon': 'DashboardOutlined',
            'sort': 1,
            'parent': None,
        },
        {
            'code': 'user-management',
            'title': '用户管理',
            'path': '/user',
            'icon': 'UserOutlined',
            'sort': 2,
            'parent': None,
        },
        {
            'code': 'project-management',
            'title': '项目管理',
            'path': '/project',
            'icon': 'ProjectOutlined',
            'sort': 3,
            'parent': None,
        },
        {
            'code': 'server-management',
            'title': '服务器管理',
            'path': '/server',
            'icon': 'ServerOutlined',
            'sort': 4,
            'parent': None,
        },
        {
            'code': 'mail-management',
            'title': '邮件管理',
            'path': '/mail',
            'icon': 'MailOutlined',
            'sort': 5,
            'parent': None,
        },
    ]
    
    # 创建一级菜单
    menu_map = {}
    for data in menus_data:
        menu = await Menu.create(**data)
        menu_map[data['code']] = menu
        print(f"  ✓ 创建菜单: {data['title']}")
    
    # 二级菜单
    sub_menus_data = [
        # 用户管理
        {
            'code': 'user-list',
            'title': '用户列表',
            'path': '/user/list',
            'component': 'views/User/List',
            'sort': 1,
            'parent': 'user-management',
        },
        {
            'code': 'role-list',
            'title': '角色管理',
            'path': '/user/role',
            'component': 'views/User/Role',
            'sort': 2,
            'parent': 'user-management',
        },
        {
            'code': 'menu-list',
            'title': '菜单管理',
            'path': '/user/menu',
            'component': 'views/User/Menu',
            'sort': 3,
            'parent': 'user-management',
        },
        {
            'code': 'permission-list',
            'title': '权限管理',
            'path': '/user/permission',
            'component': 'views/User/Permission',
            'sort': 4,
            'parent': 'user-management',
        },
        
        # 项目管理
        {
            'code': 'project-list',
            'title': '项目列表',
            'path': '/project/list',
            'component': 'views/Project/List',
            'sort': 1,
            'parent': 'project-management',
        },
        {
            'code': 'account-list',
            'title': '账号管理',
            'path': '/project/account',
            'component': 'views/Project/Account',
            'sort': 2,
            'parent': 'project-management',
        },
        {
            'code': 'wallet-list',
            'title': '钱包管理',
            'path': '/project/wallet',
            'component': 'views/Project/Wallet',
            'sort': 3,
            'parent': 'project-management',
        },
        
        # 服务器管理
        {
            'code': 'server-list',
            'title': '服务器列表',
            'path': '/server/list',
            'component': 'views/Server/List',
            'sort': 1,
            'parent': 'server-management',
        },
        {
            'code': 'country-list',
            'title': '国家管理',
            'path': '/server/country',
            'component': 'views/Server/Country',
            'sort': 2,
            'parent': 'server-management',
        },
        {
            'code': 'group-list',
            'title': '分组管理',
            'path': '/server/group',
            'component': 'views/Server/Group',
            'sort': 3,
            'parent': 'server-management',
        },
        
        # 邮件管理
        {
            'code': 'mail-list',
            'title': '邮件列表',
            'path': '/mail/list',
            'component': 'views/Mail/List',
            'sort': 1,
            'parent': 'mail-management',
        },
    ]
    
    for data in sub_menus_data:
        parent_code = data.pop('parent')
        parent_menu = menu_map[parent_code]
        menu = await Menu.create(**data, parent_id=parent_menu.id)
        print(f"  ✓ 创建子菜单: {data['title']}")
    
    print(f"✓ 菜单初始化完成，共创建 {len(menus_data) + len(sub_menus_data)} 个菜单\n")


async def init_permissions():
    """初始化权限"""
    print("初始化权限...")
    
    # 定义权限
    permissions_data = {
        'user': {
            'name': '用户',
            'actions': ['view', 'create', 'edit', 'delete', 'export'],
        },
        'role': {
            'name': '角色',
            'actions': ['view', 'create', 'edit', 'delete'],
        },
        'menu': {
            'name': '菜单',
            'actions': ['view', 'create', 'edit', 'delete'],
        },
        'permission': {
            'name': '权限',
            'actions': ['view', 'create', 'edit', 'delete'],
        },
        'project': {
            'name': '项目',
            'actions': ['view', 'create', 'edit', 'delete', 'export'],
        },
        'account': {
            'name': '账号',
            'actions': ['view', 'create', 'edit', 'delete', 'export'],
        },
        'wallet': {
            'name': '钱包',
            'actions': ['view', 'create', 'edit', 'delete'],
        },
        'server': {
            'name': '服务器',
            'actions': ['view', 'create', 'edit', 'delete', 'export'],
        },
        'country': {
            'name': '国家',
            'actions': ['view', 'create', 'edit', 'delete'],
        },
        'group': {
            'name': '分组',
            'actions': ['view', 'create', 'edit', 'delete'],
        },
        'mail': {
            'name': '邮件',
            'actions': ['view', 'create', 'edit', 'delete', 'export'],
        },
    }
    
    action_names = {
        'view': '查看',
        'create': '创建',
        'edit': '编辑',
        'delete': '删除',
        'export': '导出',
        'import': '导入',
    }
    
    total = 0
    for resource, config in permissions_data.items():
        resource_name = config['name']
        for action in config['actions']:
            code = f"{resource}:{action}"
            name = f"{action_names[action]}{resource_name}"
            
            await Permission.create(
                code=code,
                name=name,
                resource=resource,
                action=action,
                permission_type=PermissionType.FUNCTION,
                group=resource
            )
            print(f"  ✓ 创建权限: {name} ({code})")
            total += 1
    
    print(f"✓ 权限初始化完成，共创建 {total} 个权限\n")


async def init_roles():
    """初始化角色"""
    print("初始化角色...")
    
    roles_data = [
        {
            'code': 'ADMIN',
            'name': '系统管理员',
            'description': '拥有所有权限',
            'level': 100,
            'data_scope': DataScope.ALL,
            'is_system': True,
        },
        {
            'code': 'GM',
            'name': '项目经理',
            'description': '管理项目相关数据',
            'level': 50,
            'data_scope': DataScope.DEPT_AND_CHILD,
            'is_system': True,
        },
        {
            'code': 'IT',
            'name': '技术人员',
            'description': '管理服务器相关数据',
            'level': 30,
            'data_scope': DataScope.DEPT,
            'is_system': True,
        },
        {
            'code': 'MANUAL',
            'name': '手动操作员',
            'description': '只能查看和编辑',
            'level': 10,
            'data_scope': DataScope.SELF,
            'is_system': True,
        },
    ]
    
    role_map = {}
    for data in roles_data:
        role = await Role.create(**data)
        role_map[data['code']] = role
        print(f"  ✓ 创建角色: {data['name']} ({data['code']})")
    
    print(f"✓ 角色初始化完成，共创建 {len(roles_data)} 个角色\n")
    
    return role_map


async def assign_permissions():
    """分配权限"""
    print("分配权限...")
    
    # ADMIN 拥有所有权限
    admin_role = await Role.get(code='ADMIN')
    all_permissions = await Permission.all()
    await admin_role.permissions.add(*all_permissions)
    print(f"  ✓ ADMIN 分配 {len(all_permissions)} 个权限")
    
    # GM 权限
    gm_role = await Role.get(code='GM')
    gm_permissions = await Permission.filter(
        resource__in=['user', 'project', 'account', 'wallet']
    ).exclude(action='delete').all()
    await gm_role.permissions.add(*gm_permissions)
    print(f"  ✓ GM 分配 {len(gm_permissions)} 个权限")
    
    # IT 权限
    it_role = await Role.get(code='IT')
    it_permissions = await Permission.filter(
        resource__in=['server', 'country', 'group']
    ).all()
    await it_role.permissions.add(*it_permissions)
    print(f"  ✓ IT 分配 {len(it_permissions)} 个权限")
    
    # MANUAL 权限
    manual_role = await Role.get(code='MANUAL')
    manual_permissions = await Permission.filter(
        action__in=['view', 'edit']
    ).all()
    await manual_role.permissions.add(*manual_permissions)
    print(f"  ✓ MANUAL 分配 {len(manual_permissions)} 个权限")
    
    print("✓ 权限分配完成\n")


async def assign_menus():
    """分配菜单"""
    print("分配菜单...")
    
    # ADMIN 拥有所有菜单
    admin_role = await Role.get(code='ADMIN')
    all_menus = await Menu.all()
    await admin_role.menus.add(*all_menus)
    print(f"  ✓ ADMIN 分配 {len(all_menus)} 个菜单")
    
    # GM 菜单
    gm_role = await Role.get(code='GM')
    gm_menus = await Menu.filter(
        code__in=[
            'dashboard',
            'user-management', 'user-list', 'role-list',
            'project-management', 'project-list', 'account-list', 'wallet-list',
        ]
    ).all()
    await gm_role.menus.add(*gm_menus)
    print(f"  ✓ GM 分配 {len(gm_menus)} 个菜单")
    
    # IT 菜单
    it_role = await Role.get(code='IT')
    it_menus = await Menu.filter(
        code__in=[
            'dashboard',
            'server-management', 'server-list', 'country-list', 'group-list',
        ]
    ).all()
    await it_role.menus.add(*it_menus)
    print(f"  ✓ IT 分配 {len(it_menus)} 个菜单")
    
    # MANUAL 菜单
    manual_role = await Role.get(code='MANUAL')
    manual_menus = await Menu.filter(
        code__in=[
            'dashboard',
            'project-management', 'project-list',
        ]
    ).all()
    await manual_role.menus.add(*manual_menus)
    print(f"  ✓ MANUAL 分配 {len(manual_menus)} 个菜单")
    
    print("✓ 菜单分配完成\n")


async def create_admin_user():
    """创建管理员用户"""
    print("创建管理员用户...")
    
    # 检查是否已存在
    existing = await UserInfo.filter(email='zhiyu').first()
    if existing:
        print("  ! 管理员用户已存在，跳过创建")
        admin_user = existing
    else:
        # 创建管理员
        admin_user = await UserInfo.create(
            email='zhiyu',
            password=hashing.hash('2201101122@qq.com'),
            nickname='系统管理员',
        )
        print("  ✓ 创建管理员用户: zhiyu")
    
    # 分配 ADMIN 角色
    admin_role = await Role.get(code='ADMIN')
    await admin_user.roles_v2.add(admin_role)
    print("  ✓ 分配 ADMIN 角色")
    
    print("✓ 管理员用户创建完成\n")


async def main():
    """主函数"""
    print("=" * 60)
    print("初始化 RBAC v2 数据")
    print("=" * 60)
    print()
    
    # 初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    
    try:
        # 初始化菜单
        await init_menus()
        
        # 初始化权限
        await init_permissions()
        
        # 初始化角色
        await init_roles()
        
        # 分配权限
        await assign_permissions()
        
        # 分配菜单
        await assign_menus()
        
        # 创建管理员
        await create_admin_user()
        
        print("=" * 60)
        print("✓ RBAC v2 数据初始化完成！")
        print("=" * 60)
        print()
        print("默认管理员账号：")
        print("  邮箱: zhiyu")
        print("  密码: 2201101122@qq.com")
        print()
        
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
