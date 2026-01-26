#!/bin/bash

# ==========================================
# 清除并重新初始化路由
# ==========================================

echo "=========================================="
echo "清除并重新初始化路由"
echo "=========================================="

cd /opt/zy/qyd_api

# 警告提示
echo ""
echo "⚠️  警告：此操作将删除所有现有路由数据！"
echo ""
read -p "确定要继续吗？(yes/no) " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "已取消"
    exit 0
fi

# 1. 清除所有路由数据
echo ""
echo "[1/4] 清除所有路由数据..."
docker compose exec backend-api python3 << 'EOF'
import asyncio
from tortoise import Tortoise
from app.core import settings

async def clear_routes():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    from app.models.user import FrontendRoute, UserRole
    
    # 获取所有角色，清除路由关联
    print("清除角色的路由关联...")
    roles = await UserRole.all().prefetch_related('routes')
    for role in roles:
        await role.routes.clear()
        print(f"  ✓ 已清除 {role.name} 的路由关联")
    
    # 删除所有路由
    print("\n删除所有路由...")
    count = await FrontendRoute.all().count()
    await FrontendRoute.all().delete()
    print(f"  ✓ 已删除 {count} 个路由")
    
    await Tortoise.close_connections()

asyncio.run(clear_routes())
EOF

# 2. 重新初始化路由
echo ""
echo "[2/4] 重新初始化路由..."
docker compose exec backend-api python db/init_routes.py

# 3. 将所有路由分配给 ADMIN 角色
echo ""
echo "[3/4] 将所有路由分配给 ADMIN 角色..."
docker compose exec backend-api python3 << 'EOF'
import asyncio
from tortoise import Tortoise
from app.core import settings

async def assign_routes():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    from app.models.user import FrontendRoute, UserRole
    
    # 获取 ADMIN 角色
    admin = await UserRole.get_or_none(code="ADMIN")
    if not admin:
        print("✗ 未找到 ADMIN 角色")
        return
    
    # 获取所有路由
    all_routes = await FrontendRoute.all()
    
    # 清除现有关联
    await admin.routes.clear()
    
    # 分配所有路由
    await admin.routes.add(*all_routes)
    
    print(f"✓ 已将 {len(all_routes)} 个路由分配给 ADMIN 角色")
    
    await Tortoise.close_connections()

asyncio.run(assign_routes())
EOF

# 4. 验证结果
echo ""
echo "[4/4] 验证结果..."
docker compose exec backend-api python3 << 'EOF'
import asyncio
from tortoise import Tortoise
from app.core import settings

async def verify():
    await Tortoise.init(config=settings.TORTOISE_ORM)
    from app.models.user import FrontendRoute, UserRole
    
    # 统计路由
    total = await FrontendRoute.all().count()
    parents = await FrontendRoute.filter(parent_id=None).count()
    children = total - parents
    
    print(f"\n路由统计：")
    print(f"  总路由数: {total}")
    print(f"  一级菜单: {parents}")
    print(f"  二级菜单: {children}")
    
    # 显示一级菜单
    print(f"\n一级菜单列表：")
    parent_routes = await FrontendRoute.filter(parent_id=None).order_by('sort')
    for route in parent_routes:
        children_count = await FrontendRoute.filter(parent_id=route.id).count()
        print(f"  {route.sort}. {route.title} ({route.path}) - {children_count} 个子菜单")
    
    # 检查 API 文档
    api_docs = await FrontendRoute.filter(name__contains="api-docs").all()
    print(f"\nAPI 文档路由: {len(api_docs)} 个")
    if api_docs:
        for route in api_docs[:5]:  # 只显示前5个
            print(f"  - {route.title} ({route.path})")
        if len(api_docs) > 5:
            print(f"  ... 还有 {len(api_docs) - 5} 个")
    
    # 检查 ADMIN 权限
    admin = await UserRole.get_or_none(code="ADMIN").prefetch_related('routes')
    if admin:
        admin_routes = await admin.routes.all()
        print(f"\nADMIN 角色权限: {len(admin_routes)} 个路由")
        
        # 检查是否包含 API 文档
        api_docs_in_admin = [r for r in admin_routes if 'api-docs' in r.name]
        print(f"  其中 API 文档: {len(api_docs_in_admin)} 个")
    
    await Tortoise.close_connections()

asyncio.run(verify())
EOF

echo ""
echo "=========================================="
echo "✅ 完成！"
echo "=========================================="
echo ""
echo "请刷新浏览器（Ctrl+Shift+R）查看更新后的菜单"
echo ""
echo "如果还是看不到 API 文档菜单："
echo "  1. 退出登录"
echo "  2. 重新登录（获取新的 Token）"
echo "  3. 检查左侧菜单"
