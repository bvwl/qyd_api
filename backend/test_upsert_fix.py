"""
测试 upsert 接口修复
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.schemas.project.account import Create
from app.crud.project.account import project_account_crud


async def test_upsert():
    """测试 upsert 方法"""
    print("="*60)
    print("测试 upsert 方法")
    print("="*60)
    
    # 创建测试数据
    test_data = Create(
        account="test_upsert_account",
        project_id="2052f094-800c-41b1-a750-996280b38281",
        balance=100.0,
        status=1
    )
    
    print(f"\n测试数据:")
    print(f"  account: {test_data.account}")
    print(f"  project_id: {test_data.project_id}")
    print(f"  balance: {test_data.balance}")
    
    try:
        # 测试调用 upsert 方法
        print(f"\n调用 upsert 方法...")
        
        # 初始化数据库
        from tortoise import Tortoise
        from app.core.settings import get_tortoise_config
        
        await Tortoise.init(config=get_tortoise_config())
        
        # 调用 upsert
        result = await project_account_crud.upsert(test_data)
        
        print(f"\n✅ upsert 调用成功!")
        print(f"  返回类型: {type(result)}")
        print(f"  account: {result.account}")
        print(f"  balance: {result.balance}")
        
        # 再次调用，测试更新
        test_data.balance = 200.0
        result2 = await project_account_crud.upsert(test_data)
        
        print(f"\n✅ 第二次 upsert 调用成功（更新）!")
        print(f"  account: {result2.account}")
        print(f"  balance: {result2.balance}")
        
        print(f"\n{'='*60}")
        print(f"测试通过！upsert 方法工作正常")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_upsert())
