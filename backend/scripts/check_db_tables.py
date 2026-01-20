"""
检查数据库表是否存在
"""
import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# 添加 backend 到 Python 路径
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# 加载 .env 文件
env_path = backend_path / '.env'
load_dotenv(env_path)

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM


async def check_tables():
    """检查数据库中的表"""
    try:
        print("=" * 60)
        print("正在连接数据库...")
        print(f"数据库: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
        print("=" * 60)
        
        await Tortoise.init(config=TORTOISE_ORM)
        conn = Tortoise.get_connection("default")
        
        # 查询所有表
        result = await conn.execute_query_dict(
            "SELECT TABLE_NAME FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME",
            [os.getenv('DB_NAME', 'qyd')]
        )
        
        if result:
            print(f"\n✅ 找到 {len(result)} 个表:\n")
            for idx, row in enumerate(result, 1):
                print(f"  {idx:2d}. {row['TABLE_NAME']}")
        else:
            print("\n❌ 数据库中没有找到任何表！")
            print("\n可能的原因:")
            print("  1. 迁移脚本没有真正执行")
            print("  2. 连接到了错误的数据库")
            print("  3. 数据库权限不足")
        
        print("\n" + "=" * 60)
        
        # 检查 aerich 迁移记录
        try:
            aerich_result = await conn.execute_query_dict(
                "SELECT * FROM aerich ORDER BY id DESC LIMIT 5"
            )
            if aerich_result:
                print("\n📋 最近的迁移记录:")
                for record in aerich_result:
                    print(f"  - {record['app']}: {record['version']}")
            else:
                print("\n⚠️  aerich 表存在但没有迁移记录")
        except Exception as e:
            print(f"\n⚠️  无法读取 aerich 表: {e}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请检查:")
        print("  1. 数据库服务是否运行")
        print("  2. .env 文件中的数据库配置是否正确")
        print("  3. 数据库用户是否有足够的权限")
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(check_tables())
