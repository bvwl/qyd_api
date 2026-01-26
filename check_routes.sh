#!/bin/bash

# ==========================================
# 检查路由数据
# ==========================================

echo "=========================================="
echo "检查路由数据"
echo "=========================================="

# 加载环境变量
if [ -f .env.high_concurrency ]; then
    export $(grep -v '^#' .env.high_concurrency | xargs)
fi

cd backend

echo ""
echo "检查数据库中的路由数据..."
python3 << 'EOF'
import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from tortoise import Tortoise
from app.core import settings

async def check_routes():
    # 初始化数据库
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    from app.models.user import FrontendRoute, UserRole
    
    # 获取所有路由
    routes = await FrontendRoute.all().order_by('sort')
    
    print(f"\n总共 {len(routes)} 个路由：")
    print("-" * 80)
    
    # 按层级显示
    root_routes = [r for r in routes if r.parent_id is None]
    
    for root in root_routes:
        print(f"\n📁 {root.title} ({root.name})")
        print(f"   路径: {root.path}")
        
        # 查找子路由
        children = [r for r in routes if r.parent_id == root.id]
        if children:
            for child in children:
                print(f"   └─ {child.title} ({child.name})")
                print(f"      路径: {child.path}")
    
    # 检查 ADMIN 角色的权限
    print("\n" + "=" * 80)
    print("检查 ADMIN 角色的权限")
    print("=" * 80)
    
    admin_role = await UserRole.get_or_none(code="ADMIN").prefetch_related('routes')
    if admin_role:
        admin_routes = await admin_role.routes.all()
        print(f"\nADMIN 角色拥有 {len(admin_routes)} 个路由权限")
        
        # 检查是否包含 API 文档路由
        api_docs_routes = [r for r in admin_routes if 'api-docs' in r.name or 'api-docs' in r.path]
        print(f"其中 API 文档相关路由: {len(api_docs_routes)} 个")
        
        if api_docs_routes:
            print("\nAPI 文档路由列表：")
            for route in api_docs_routes:
                print(f"  - {route.title} ({route.name})")
        else:
            print("\n⚠️  警告：ADMIN 角色没有 API 文档路由权限！")
            print("   需要重新初始化路由权限")
    
    await Tortoise.close_connections()

asyncio.run(check_routes())
EOF

echo ""
echo "=========================================="
echo "检查完成"
echo "=========================================="
