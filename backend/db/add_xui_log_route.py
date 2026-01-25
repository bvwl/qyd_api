#!/usr/bin/env python3
"""
添加 XUI 操作日志路由到数据库
"""
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM
from app.models.user import FrontendRoute, UserRole


async def add_xui_log_route():
    """添加 XUI 操作日志路由"""
    await Tortoise.init(config=TORTOISE_ORM)
    
    print("=" * 80)
    print("添加 XUI 操作日志路由")
    print("=" * 80)
    
    try:
        # 1. 查找 XUI 管理父路由
        xui_parent = await FrontendRoute.get_or_none(path='/xui', parent_id=None)
        if not xui_parent:
            print("❌ 未找到 XUI 管理父路由")
            return
        
        print(f"\n✅ 找到 XUI 管理父路由: {xui_parent.title} (ID: {xui_parent.id})")
        
        # 2. 检查是否已存在操作日志路由
        existing = await FrontendRoute.get_or_none(path='/xui/log')
        if existing:
            print(f"\n⚠️  操作日志路由已存在: {existing.title}")
            return
        
        # 3. 获取当前最大排序值
        max_sort_route = await FrontendRoute.filter(
            parent_id=xui_parent.id
        ).order_by('-sort').first()
        
        next_sort = (max_sort_route.sort + 1) if max_sort_route else 1
        
        # 4. 创建操作日志路由
        log_route = await FrontendRoute.create(
            id=uuid4(),
            name='XuiOperationLog',
            path='/xui/log',
            component='views/Xui/XuiOperationLog',
            title='操作日志',
            icon='FileTextOutlined',
            parent_id=xui_parent.id,
            sort=next_sort,
            status=1,
            route_type=1,  # 菜单
            permission='xui:log:view'
        )
        
        print(f"\n✅ 创建操作日志路由成功:")
        print(f"   ID: {log_route.id}")
        print(f"   名称: {log_route.name}")
        print(f"   路径: {log_route.path}")
        print(f"   标题: {log_route.title}")
        print(f"   排序: {log_route.sort}")
        print(f"   权限: {log_route.permission}")
        
        # 5. 绑定到 ADMIN 角色
        admin_role = await UserRole.get_or_none(code='ADMIN')
        if admin_role:
            await admin_role.routes.add(log_route)
            print(f"\n✅ 已绑定到 ADMIN 角色")
        
        # 6. 绑定到 GM 角色
        gm_role = await UserRole.get_or_none(code='GM')
        if gm_role:
            await gm_role.routes.add(log_route)
            print(f"✅ 已绑定到 GM 角色")
        
        # 7. 统计
        total_routes = await FrontendRoute.all().count()
        xui_routes = await FrontendRoute.filter(parent_id=xui_parent.id).count()
        
        print(f"\n📊 统计信息:")
        print(f"   总路由数: {total_routes}")
        print(f"   XUI 子路由数: {xui_routes}")
        
        print("\n" + "=" * 80)
        print("✅ 添加完成!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 添加失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(add_xui_log_route())
