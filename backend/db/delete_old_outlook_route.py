"""
删除旧的 Outlook授权 路由
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
from app.models.user import FrontendRoute


async def delete_old_route():
    """
    删除旧的 Outlook授权 路由
    """
    print("=" * 60)
    print("删除旧的 Outlook授权 路由")
    print("=" * 60)
    print()
    
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.get_tortoise_config())
        print("✓ 数据库连接成功")
        print()
        
        # 查找旧的 Outlook授权 路由
        old_route = await FrontendRoute.get_or_none(name='mail-outlook')
        
        if old_route:
            print(f"找到旧路由: {old_route.title} ({old_route.path})")
            await old_route.delete()
            print("✓ 已删除旧路由")
        else:
            print("✗ 未找到旧路由 (name='mail-outlook')")
        
        print()
        print("=" * 60)
        print("操作完成！")
        print("=" * 60)
        print()
        
    except Exception as e:
        print(f"✗ 操作失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(delete_old_route())
