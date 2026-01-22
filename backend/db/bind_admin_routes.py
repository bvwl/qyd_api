"""
为ADMIN角色绑定所有路由权限
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
from app.models.user import UserRole, FrontendRoute


async def bind_admin_routes():
    """
    为ADMIN角色绑定所有路由权限
    """
    print("=" * 60)
    print("为ADMIN角色绑定路由权限")
    print("=" * 60)
    print()
    
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.get_tortoise_config())
        print("✓ 数据库连接成功")
        print()
        
        # 获取ADMIN角色
        admin_role = await UserRole.filter(code='ADMIN').prefetch_related('routes').first()
        if not admin_role:
            print('✗ 未找到ADMIN角色')
            return
        
        print(f"✓ 找到ADMIN角色: {admin_role.name}")
        print(f"  当前拥有 {len(admin_role.routes)} 个路由权限")
        print()
        
        # 获取所有路由
        all_routes = await FrontendRoute.all()
        print(f"✓ 数据库中共有 {len(all_routes)} 个路由")
        print()
        
        # 检查是否需要添加路由
        current_route_ids = {r.id for r in admin_role.routes}
        all_route_ids = {r.id for r in all_routes}
        missing_route_ids = all_route_ids - current_route_ids
        
        if missing_route_ids:
            print(f"需要添加 {len(missing_route_ids)} 个路由权限:")
            # 添加缺失的路由
            missing_routes = [r for r in all_routes if r.id in missing_route_ids]
            for route in missing_routes:
                print(f"  + {route.title} ({route.path})")
            
            await admin_role.routes.add(*missing_routes)
            print()
            print("✓ 已添加所有路由权限到ADMIN角色")
        else:
            print("✓ ADMIN角色已拥有所有路由权限，无需添加")
        
        print()
        print("=" * 60)
        print("绑定完成！")
        print("=" * 60)
        print()
        
        # 显示最终统计
        admin_role = await UserRole.filter(code='ADMIN').prefetch_related('routes').first()
        print(f"ADMIN角色最终拥有 {len(admin_role.routes)} 个路由权限")
        print()
        
    except Exception as e:
        print(f"✗ 绑定失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(bind_admin_routes())
