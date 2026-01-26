#!/usr/bin/env python3
"""
检查数据库数据脚本
"""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM
from app.models.user import UserInfo, UserRole, FrontendRoute


async def check_database():
    """检查数据库数据"""
    try:
        # 初始化数据库连接
        await Tortoise.init(config=TORTOISE_ORM)
        
        print("=" * 60)
        print("数据库数据检查")
        print("=" * 60)
        
        # 1. 检查角色
        print("\n1. 角色列表:")
        roles = await UserRole.all()
        for role in roles:
            print(f"  - {role.code}: {role.name} (状态: {role.status})")
        
        # 2. 检查路由
        print(f"\n2. 路由总数: {await FrontendRoute.all().count()}")
        print("   一级路由:")
        parent_routes = await FrontendRoute.filter(parent_id=None).all()
        for route in parent_routes:
            children_count = await FrontendRoute.filter(parent_id=route.id).count()
            print(f"  - {route.path}: {route.name} ({children_count} 个子路由)")
        
        # 3. 检查用户
        print(f"\n3. 用户总数: {await UserInfo.all().count()}")
        users = await UserInfo.all().prefetch_related('roles')
        for user in users:
            roles_str = ', '.join([r.code for r in user.roles])
            print(f"  - {user.email}: {user.nickname} (角色: {roles_str}, 状态: {user.status})")
        
        # 4. 检查管理员权限
        print("\n4. 管理员权限:")
        admin_role = await UserRole.filter(code='ADMIN').first()
        if admin_role:
            routes = await admin_role.routes.all()
            print(f"  - ADMIN 角色拥有 {len(routes)} 个路由权限")
            if len(routes) == 0:
                print("  ⚠️  警告: ADMIN 角色没有任何路由权限！")
        
        # 5. 检查 GM 权限
        print("\n5. GM 权限:")
        gm_role = await UserRole.filter(code='GM').first()
        if gm_role:
            routes = await gm_role.routes.all()
            print(f"  - GM 角色拥有 {len(routes)} 个路由权限")
        
        print("\n" + "=" * 60)
        print("检查完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(check_database())
