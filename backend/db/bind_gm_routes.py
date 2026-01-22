"""
为GM角色绑定路由权限（除了用户管理相关的路由）
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


async def bind_gm_routes():
    """
    为GM角色绑定路由权限
    GM可以访问除了用户管理之外的所有功能
    """
    print("=" * 60)
    print("为GM角色绑定路由权限")
    print("=" * 60)
    print()
    
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.get_tortoise_config())
        print("✓ 数据库连接成功")
        print()
        
        # 获取GM角色
        gm_role = await UserRole.filter(code='GM').prefetch_related('routes').first()
        if not gm_role:
            print('✗ 未找到GM角色')
            return
        
        print(f"✓ 找到GM角色: {gm_role.name}")
        print(f"  当前拥有 {len(gm_role.routes)} 个路由权限")
        print()
        
        # 获取所有路由，排除用户管理相关的路由
        all_routes = await FrontendRoute.all()
        
        # 过滤掉用户管理的路由（/user开头的）
        gm_routes = [r for r in all_routes if not r.path.startswith('/user')]
        
        print(f"✓ 数据库中共有 {len(all_routes)} 个路由")
        print(f"✓ GM角色应该拥有 {len(gm_routes)} 个路由权限（排除用户管理）")
        print()
        
        # 清空现有权限并重新绑定
        await gm_role.routes.clear()
        await gm_role.routes.add(*gm_routes)
        
        print("✓ 已为GM角色绑定路由权限")
        print()
        print("绑定的路由:")
        
        # 按一级菜单分组显示
        parent_routes = [r for r in gm_routes if r.parent_id is None]
        for parent in sorted(parent_routes, key=lambda x: x.sort):
            print(f"  📁 {parent.title} ({parent.path})")
            children = [r for r in gm_routes if r.parent_id == parent.id]
            for child in sorted(children, key=lambda x: x.sort):
                print(f"    └─ {child.title} ({child.path})")
        
        print()
        print("=" * 60)
        print("绑定完成！")
        print("=" * 60)
        print()
        
        # 显示最终统计
        gm_role = await UserRole.filter(code='GM').prefetch_related('routes').first()
        print(f"GM角色最终拥有 {len(gm_role.routes)} 个路由权限")
        print()
        
    except Exception as e:
        print(f"✗ 绑定失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(bind_gm_routes())
