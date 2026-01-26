"""
初始化前端路由数据
将前端菜单结构同步到数据库
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# 加载环境变量
env_path = backend_dir / '.env'
load_dotenv(env_path)
print(f"✓ 已加载环境变量: {env_path}")
print()

from tortoise import Tortoise
from app.core import settings
from app.models.user import FrontendRoute, Status

# 路由数据结构
ROUTES_DATA = [
    {
        "name": "dashboard",
        "path": "/dashboard",
        "title": "仪表盘",
        "icon": "DashboardOutlined",
        "component": "Dashboard",
        "sort": 1,
        "status": Status.OK,
    },
    {
        "name": "user",
        "path": "/user",
        "title": "用户管理",
        "icon": "UserOutlined",
        "sort": 2,
        "status": Status.OK,
        "children": [
            {
                "name": "user-list",
                "path": "/user/list",
                "title": "用户列表",
                "component": "UserList",
                "sort": 1,
            },
            {
                "name": "user-role",
                "path": "/user/role",
                "title": "角色管理",
                "component": "RoleList",
                "sort": 2,
            },
            {
                "name": "user-route",
                "path": "/user/route",
                "title": "路由管理",
                "component": "RouteList",
                "sort": 3,
            },
            {
                "name": "user-permission",
                "path": "/user/permission",
                "title": "权限管理",
                "component": "PermissionManage",
                "sort": 4,
            },
            {
                "name": "user-token",
                "path": "/user/token",
                "title": "Token管理",
                "component": "TokenList",
                "sort": 5,
            },
            {
                "name": "user-log",
                "path": "/user/log",
                "title": "操作日志",
                "component": "LogList",
                "sort": 6,
            },
        ],
    },
    {
        "name": "project",
        "path": "/project",
        "title": "项目管理",
        "icon": "ProjectOutlined",
        "sort": 3,
        "status": Status.OK,
        "children": [
            {
                "name": "project-list",
                "path": "/project/list",
                "title": "项目列表",
                "component": "ProjectList",
                "sort": 1,
            },
            {
                "name": "project-account",
                "path": "/project/account",
                "title": "项目账号",
                "component": "ProjectAccount",
                "sort": 2,
            },
            {
                "name": "project-wallet",
                "path": "/project/wallet",
                "title": "项目钱包",
                "component": "ProjectWallet",
                "sort": 3,
            },
            {
                "name": "project-wallet-batch-create",
                "path": "/project/wallet/batch-create",
                "title": "批量创建钱包",
                "component": "WalletBatchCreate",
                "sort": 4,
            },
        ],
    },
    {
        "name": "server",
        "path": "/server",
        "title": "服务器管理",
        "icon": "CloudServerOutlined",
        "sort": 4,
        "status": Status.OK,
        "children": [
            {
                "name": "server-country",
                "path": "/server/country",
                "title": "国家管理",
                "component": "CountryList",
                "sort": 1,
            },
            {
                "name": "server-group",
                "path": "/server/group",
                "title": "分组管理",
                "component": "GroupList",
                "sort": 2,
            },
            {
                "name": "server-list",
                "path": "/server/list",
                "title": "服务器列表",
                "component": "ServerList",
                "sort": 3,
            },
            {
                "name": "server-account",
                "path": "/server/account",
                "title": "服务器账号",
                "component": "ServerAccount",
                "sort": 4,
            },
        ],
    },
    {
        "name": "mail",
        "path": "/mail",
        "title": "邮箱管理",
        "icon": "MailOutlined",
        "sort": 5,
        "status": Status.OK,
        "children": [
            {
                "name": "mail-list",
                "path": "/mail/list",
                "title": "邮箱列表",
                "component": "MailList",
                "sort": 1,
            },
            {
                "name": "mail-viewer",
                "path": "/mail/viewer",
                "title": "邮件查看",
                "component": "MailViewer",
                "sort": 2,
            },
            {
                "name": "mail-send",
                "path": "/mail/send",
                "title": "发送邮件",
                "component": "MailSend",
                "sort": 3,
            },
        ],
    },
    {
        "name": "xui",
        "path": "/xui",
        "title": "XUI管理",
        "icon": "CloudOutlined",
        "sort": 6,
        "status": Status.OK,
        "children": [
            {
                "name": "xui-server",
                "path": "/xui/server",
                "title": "服务器列表",
                "component": "XuiServerList",
                "sort": 1,
            },
            {
                "name": "xui-inbound",
                "path": "/xui/inbound",
                "title": "入站列表",
                "component": "XuiInboundList",
                "sort": 2,
            },
            {
                "name": "xui-account",
                "path": "/xui/account",
                "title": "账号管理",
                "component": "XuiAccountList",
                "sort": 3,
            },
            {
                "name": "xui-log",
                "path": "/xui/log",
                "title": "操作日志",
                "component": "XuiOperationLog",
                "sort": 4,
            },
        ],
    },
    {
        "name": "api-docs",
        "path": "/api-docs",
        "title": "API文档",
        "icon": "ApiOutlined",
        "sort": 7,
        "status": Status.OK,
        "children": [
            {
                "name": "api-docs-user",
                "path": "/api-docs/user",
                "title": "用户列表",
                "component": "ApiDocsUser",
                "sort": 1,
            },
            {
                "name": "api-docs-user-create",
                "path": "/api-docs/user-create",
                "title": "创建用户",
                "component": "ApiDocsUserCreate",
                "sort": 2,
            },
            {
                "name": "api-docs-role",
                "path": "/api-docs/role",
                "title": "角色列表",
                "component": "ApiDocsRole",
                "sort": 3,
            },
            {
                "name": "api-docs-project",
                "path": "/api-docs/project",
                "title": "项目列表",
                "component": "ApiDocsProject",
                "sort": 4,
            },
            {
                "name": "api-docs-project-account",
                "path": "/api-docs/project-account",
                "title": "项目账号",
                "component": "ApiDocsProjectAccount",
                "sort": 5,
            },
            {
                "name": "api-docs-server",
                "path": "/api-docs/server",
                "title": "服务器列表",
                "component": "ApiDocsServer",
                "sort": 6,
            },
            {
                "name": "api-docs-mail",
                "path": "/api-docs/mail",
                "title": "邮箱列表",
                "component": "ApiDocsMail",
                "sort": 7,
            },
        ],
    },
]


async def create_route(route_data: dict, parent_id=None):
    """
    创建或更新路由
    """
    children = route_data.pop('children', [])
    
    # 检查路由是否已存在
    existing_route = await FrontendRoute.get_or_none(name=route_data['name'])
    
    if existing_route:
        # 更新现有路由
        for key, value in route_data.items():
            setattr(existing_route, key, value)
        if parent_id:
            existing_route.parent_id = parent_id
        await existing_route.save()
        print(f"  ✓ 更新路由: {route_data['title']} ({route_data['path']})")
        route = existing_route
    else:
        # 创建新路由
        route = await FrontendRoute.create(
            **route_data,
            parent_id=parent_id
        )
        print(f"  ✓ 创建路由: {route_data['title']} ({route_data['path']})")
    
    # 递归创建子路由
    for child_data in children:
        child_data.setdefault('status', Status.OK)
        await create_route(child_data, parent_id=route.id)
    
    return route


async def init_routes():
    """
    初始化路由数据
    """
    print("=" * 60)
    print("初始化前端路由数据")
    print("=" * 60)
    print()
    
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.get_tortoise_config())
        print("✓ 数据库连接成功")
        print()
        
        # 创建路由
        print("开始创建/更新路由...")
        for route_data in ROUTES_DATA:
            await create_route(route_data)
        
        print()
        print("=" * 60)
        print("路由初始化完成！")
        print("=" * 60)
        print()
        
        # 统计信息
        total_routes = await FrontendRoute.all().count()
        parent_routes = await FrontendRoute.filter(parent_id=None).count()
        child_routes = total_routes - parent_routes
        
        print(f"总路由数: {total_routes}")
        print(f"  - 一级菜单: {parent_routes}")
        print(f"  - 二级菜单: {child_routes}")
        print()
        
        # 显示路由树
        print("路由树结构:")
        print("-" * 60)
        parent_routes_list = await FrontendRoute.filter(parent_id=None).order_by('sort')
        for parent in parent_routes_list:
            print(f"📁 {parent.title} ({parent.path})")
            children = await FrontendRoute.filter(parent_id=parent.id).order_by('sort')
            for child in children:
                print(f"  └─ {child.title} ({child.path})")
        print()
        
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_routes())
