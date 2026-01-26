"""
专门添加 XUI 管理路由
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 加载环境变量
env_path = backend_dir / '.env'
load_dotenv(env_path)
print(f"✓ 已加载环境变量: {env_path}")
print()

from tortoise import Tortoise
from app.core import settings
from app.models.user import FrontendRoute, Status

# XUI 路由数据
XUI_ROUTE_DATA = {
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
            "status": Status.OK,
        },
        {
            "name": "xui-inbound",
            "path": "/xui/inbound",
            "title": "入站列表",
            "component": "XuiInboundList",
            "sort": 2,
            "status": Status.OK,
        },
        {
            "name": "xui-account",
            "path": "/xui/account",
            "title": "账号管理",
            "component": "XuiAccountList",
            "sort": 3,
            "status": Status.OK,
        },
        {
            "name": "xui-log",
            "path": "/xui/log",
            "title": "操作日志",
            "component": "XuiOperationLog",
            "sort": 4,
            "status": Status.OK,
        },
    ],
}


async def create_route(route_data: dict, parent_id=None):
    """创建或更新路由"""
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
        await create_route(child_data, parent_id=route.id)
    
    return route


async def add_xui_routes():
    """添加 XUI 管理路由"""
    print("=" * 60)
    print("添加 XUI 管理路由")
    print("=" * 60)
    print()
    
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.get_tortoise_config())
        print("✓ 数据库连接成功")
        print()
        
        # 检查 XUI 路由是否已存在
        existing_xui = await FrontendRoute.get_or_none(name="xui")
        if existing_xui:
            print("⚠️  XUI 管理路由已存在，将更新...")
        else:
            print("正在创建 XUI 管理路由...")
        print()
        
        # 创建/更新 XUI 路由
        await create_route(XUI_ROUTE_DATA)
        
        print()
        print("=" * 60)
        print("XUI 路由添加完成！")
        print("=" * 60)
        print()
        
        # 显示 XUI 路由树
        xui_route = await FrontendRoute.get(name="xui")
        children = await FrontendRoute.filter(parent_id=xui_route.id).order_by('sort')
        
        print("XUI 路由结构:")
        print("-" * 60)
        print(f"📁 {xui_route.title} ({xui_route.path})")
        for child in children:
            print(f"  └─ {child.title} ({child.path})")
        print()
        
        # 统计信息
        total_routes = await FrontendRoute.all().count()
        parent_routes = await FrontendRoute.filter(parent_id=None).count()
        
        print(f"数据库中总路由数: {total_routes}")
        print(f"  - 一级菜单: {parent_routes}")
        print()
        
        print("下一步:")
        print("  1. 刷新浏览器页面")
        print("  2. 进入 用户管理 -> 权限管理")
        print("  3. 选择 ADMIN 角色")
        print("  4. 勾选 XUI管理 及其所有子菜单")
        print("  5. 点击保存")
        print()
        
    except Exception as e:
        print(f"✗ 添加失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(add_xui_routes())
