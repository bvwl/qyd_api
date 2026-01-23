#!/usr/bin/env python3
"""
测试权限管理API
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.models.user import UserRole, FrontendRoute


async def test_permission_api():
    """测试权限管理API"""
    print("=" * 60)
    print("测试权限管理API")
    print("=" * 60)
    
    # 1. 获取所有角色
    print("\n1. 获取所有角色")
    roles = await UserRole.all()
    print(f"   找到 {len(roles)} 个角色:")
    for role in roles:
        print(f"   - {role.name} ({role.code}) - ID: {role.id}")
    
    if not roles:
        print("   ❌ 没有找到角色，请先初始化数据")
        return
    
    # 2. 获取所有路由
    print("\n2. 获取所有路由")
    routes = await FrontendRoute.all()
    print(f"   找到 {len(routes)} 个路由:")
    for route in routes[:5]:  # 只显示前5个
        print(f"   - {route.title} ({route.path}) - ID: {route.id}")
    if len(routes) > 5:
        print(f"   ... 还有 {len(routes) - 5} 个路由")
    
    if not routes:
        print("   ❌ 没有找到路由，请先初始化数据")
        return
    
    # 3. 测试获取角色的路由权限
    print("\n3. 测试获取角色的路由权限")
    test_role = roles[0]
    print(f"   测试角色: {test_role.name} ({test_role.code})")
    
    await test_role.fetch_related('routes')
    role_routes = await test_role.routes.all()
    print(f"   该角色有 {len(role_routes)} 个路由权限:")
    for route in role_routes[:5]:  # 只显示前5个
        print(f"   - {route.title} ({route.path})")
    if len(role_routes) > 5:
        print(f"   ... 还有 {len(role_routes) - 5} 个路由")
    
    # 4. 测试设置角色的路由权限
    print("\n4. 测试设置角色的路由权限")
    if len(roles) > 1:
        test_role = roles[1]
        print(f"   测试角色: {test_role.name} ({test_role.code})")
        
        # 获取前3个路由的ID
        test_route_ids = [str(route.id) for route in routes[:3]]
        print(f"   设置 {len(test_route_ids)} 个路由权限")
        
        # 清除现有权限
        await test_role.routes.clear()
        
        # 添加新权限
        test_routes = await FrontendRoute.filter(id__in=test_route_ids).all()
        await test_role.routes.add(*test_routes)
        
        # 验证
        await test_role.fetch_related('routes')
        new_routes = await test_role.routes.all()
        print(f"   ✅ 成功设置 {len(new_routes)} 个路由权限")
        for route in new_routes:
            print(f"   - {route.title} ({route.path})")
    
    # 5. 测试路由树结构
    print("\n5. 测试路由树结构")
    top_routes = await FrontendRoute.filter(parent_id=None).all()
    print(f"   找到 {len(top_routes)} 个顶级路由:")
    
    async def print_tree(route, level=0):
        """递归打印路由树"""
        indent = "  " * level
        print(f"   {indent}- {route.title} ({route.path})")
        children = await FrontendRoute.filter(parent_id=route.id).all()
        for child in children:
            await print_tree(child, level + 1)
    
    for route in top_routes[:3]:  # 只显示前3个
        await print_tree(route)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    from tortoise import Tortoise
    from app.core.settings import TORTOISE_ORM
    
    async def main():
        await Tortoise.init(config=TORTOISE_ORM)
        await test_permission_api()
        await Tortoise.close_connections()
    
    asyncio.run(main())
