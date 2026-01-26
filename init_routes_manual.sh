#!/bin/bash

# ==========================================
# 手动初始化路由
# ==========================================

echo "=========================================="
echo "手动初始化路由"
echo "=========================================="

cd /opt/zy/qyd_api

# 1. 执行路由初始化
echo ""
echo "[1/3] 执行路由初始化..."
docker compose exec backend-api python db/init_routes.py

# 2. 检查路由数据
echo ""
echo "[2/3] 检查路由数据..."
docker compose exec backend-api python3 << 'EOF'
import asyncio
from tortoise import Tortoise
from app.core import settings

async def check():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    from app.models.user import FrontendRoute
    
    # 查找所有路由
    all_routes = await FrontendRoute.all().order_by('sort')
    print(f"\n总共 {len(all_routes)} 个路由")
    
    # 查找 API 文档路由
    api_docs = await FrontendRoute.filter(name__contains="api-docs").all()
    print(f"\nAPI 文档路由: {len(api_docs)} 个")
    for route in api_docs:
        print(f"  - {route.name}: {route.title} ({route.path})")
    
    # 查找一级菜单
    parents = await FrontendRoute.filter(parent_id=None).order_by('sort')
    print(f"\n一级菜单: {len(parents)} 个")
    for p in parents:
        print(f"  - {p.title} ({p.path})")
    
    await Tortoise.close_connections()

asyncio.run(check())
EOF

# 3. 检查 ADMIN 角色权限
echo ""
echo "[3/3] 检查 ADMIN 角色权限..."
docker compose exec backend-api python3 << 'EOF'
import asyncio
from tortoise import Tortoise
from app.core import settings

async def check():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    from app.models.user import UserRole
    
    admin = await UserRole.get_or_none(code="ADMIN").prefetch_related('routes')
    if admin:
        routes = await admin.routes.all()
        print(f"\nADMIN 角色拥有 {len(routes)} 个路由权限")
        
        # 检查是否包含 API 文档
        api_docs = [r for r in routes if 'api-docs' in r.name]
        print(f"其中 API 文档路由: {len(api_docs)} 个")
        
        if len(api_docs) == 0:
            print("\n⚠️  警告：ADMIN 角色没有 API 文档权限！")
            print("   需要在权限管理页面手动分配")
    
    await Tortoise.close_connections()

asyncio.run(check())
EOF

echo ""
echo "=========================================="
echo "完成"
echo "=========================================="
echo ""
echo "如果 API 文档路由已创建但 ADMIN 没有权限："
echo "  1. 登录系统"
echo "  2. 进入 用户管理 -> 权限管理"
echo "  3. 选择 ADMIN 角色"
echo "  4. 勾选 API文档 及其子菜单"
echo "  5. 点击保存"
