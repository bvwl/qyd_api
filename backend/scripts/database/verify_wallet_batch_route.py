"""
验证批量创建钱包路由是否正确配置
"""
import asyncio
import os
from tortoise import Tortoise


async def verify_route():
    """验证路由配置"""
    # 初始化数据库
    db_url = f"mysql://{os.getenv('DB_USER', 'qyd')}:{os.getenv('DB_PASSWORD', '')}@{os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '3307')}/{os.getenv('DB_NAME', 'qyd')}"
    
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["app.models.user"]},
    )
    
    from app.models.user import FrontendRoute, Role
    
    print("="*60)
    print("验证批量创建钱包路由配置")
    print("="*60)
    
    # 1. 检查路由是否存在
    route = await FrontendRoute.get_or_none(path="/project/wallet/batch-create")
    if route:
        print(f"\n✓ 路由已创建:")
        print(f"  名称: {route.title}")
        print(f"  路径: {route.path}")
        print(f"  组件: {route.component}")
        print(f"  排序: {route.sort}")
    else:
        print("\n✗ 路由不存在")
        await Tortoise.close_connections()
        return
    
    # 2. 检查ADMIN角色是否有权限
    admin_role = await Role.get_or_none(code="ADMIN")
    if admin_role:
        await admin_role.fetch_related('routes')
        route_paths = [r.path for r in admin_role.routes]
        
        if "/project/wallet/batch-create" in route_paths:
            print(f"\n✓ ADMIN角色已绑定此路由")
            print(f"  ADMIN角色共有 {len(admin_role.routes)} 个路由权限")
        else:
            print(f"\n✗ ADMIN角色未绑定此路由")
    else:
        print("\n✗ ADMIN角色不存在")
    
    # 3. 检查父路由
    parent_route = await FrontendRoute.get_or_none(path="/project")
    if parent_route:
        children = await FrontendRoute.filter(parent_id=parent_route.id).order_by('sort').all()
        print(f"\n✓ 项目管理菜单下的子路由:")
        for child in children:
            print(f"  {child.sort}. {child.title} ({child.path})")
    
    print("\n" + "="*60)
    print("验证完成！")
    print("="*60)
    print("\n下一步:")
    print("1. 重启后端服务（如果正在运行）")
    print("2. 刷新前端页面（Ctrl+Shift+R 强制刷新）")
    print("3. 重新登录（清除缓存的路由数据）")
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(verify_route())
