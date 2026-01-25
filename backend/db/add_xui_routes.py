"""
添加 XUI 管理路由到数据库
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

# XUI 路由数据
XUI_ROUTES_DATA = {
    "name": "xui",
    "path": "/xui",
    "title": "XUI管理",
    "icon": "CloudServerOutlined",
    "sort": 5,  # 在服务器管理(4)和邮箱管理(5)之间，需要调整其他路由的 sort
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
            "component": "XuiAccountManage",
            "sort": 3,
        },
    ],
}


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


async def adjust_other_routes_sort():
    """
    调整其他路由的 sort 值
    XUI 管理插入到 sort=5，需要将原来 sort>=5 的路由 +1
    """
    print("调整其他路由的排序...")
    
    # 获取需要调整的路由（sort >= 5 且不是 XUI 路由）
    routes_to_adjust = await FrontendRoute.filter(
        sort__gte=5,
        parent_id=None
    ).exclude(name='xui')
    
    for route in routes_to_adjust:
        old_sort = route.sort
        route.sort = old_sort + 1
        await route.save()
        print(f"  ✓ 调整路由排序: {route.title} ({old_sort} -> {route.sort})")
    
    print()


async def add_xui_routes():
    """
    添加 XUI 路由
    """
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
        existing_xui = await FrontendRoute.get_or_none(name='xui')
        if existing_xui:
            print("⚠️  XUI 路由已存在，将更新现有路由")
            print()
        
        # 调整其他路由的排序（仅在首次创建时）
        if not existing_xui:
            await adjust_other_routes_sort()
        
        # 创建 XUI 路由
        print("开始创建/更新 XUI 路由...")
        await create_route(XUI_ROUTES_DATA)
        
        print()
        print("=" * 60)
        print("XUI 路由添加完成！")
        print("=" * 60)
        print()
        
        # 显示 XUI 路由树
        print("XUI 路由结构:")
        print("-" * 60)
        xui_route = await FrontendRoute.get_or_none(name='xui')
        if xui_route:
            print(f"📁 {xui_route.title} ({xui_route.path})")
            children = await FrontendRoute.filter(parent_id=xui_route.id).order_by('sort')
            for child in children:
                print(f"  └─ {child.title} ({child.path})")
        print()
        
        # 显示完整的路由树
        print("完整路由树结构:")
        print("-" * 60)
        parent_routes = await FrontendRoute.filter(parent_id=None).order_by('sort')
        for parent in parent_routes:
            print(f"📁 {parent.title} ({parent.path}) [sort={parent.sort}]")
            children = await FrontendRoute.filter(parent_id=parent.id).order_by('sort')
            for child in children:
                print(f"  └─ {child.title} ({child.path})")
        print()
        
        # 统计信息
        total_routes = await FrontendRoute.all().count()
        parent_routes_count = await FrontendRoute.filter(parent_id=None).count()
        child_routes_count = total_routes - parent_routes_count
        
        print(f"总路由数: {total_routes}")
        print(f"  - 一级菜单: {parent_routes_count}")
        print(f"  - 二级菜单: {child_routes_count}")
        print()
        
    except Exception as e:
        print(f"✗ 添加失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(add_xui_routes())
