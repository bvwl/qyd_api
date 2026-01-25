"""
测试批量创建钱包修复
"""
import asyncio
from app.crud.project.wallet import project_wallet_crud
from app.schemas.project.wallet import BatchCreate


async def test():
    print("开始测试批量创建钱包...")
    
    item = BatchCreate(
        project_name='test',
        chain='eth',
        count=2,
        remark='测试批量创建'
    )
    
    try:
        result = await project_wallet_crud.batch_create(item)
        print(f'\n✅ 创建成功: {result.count} 个钱包')
        print(f'消息: {result.message}\n')
        
        for i, wallet in enumerate(result.items, 1):
            print(f'钱包 {i}:')
            print(f'  ID: {wallet.id}')
            print(f'  链: {wallet.chain}')
            print(f'  公钥: {wallet.public_key[:30]}...')
            print(f'  私钥: {wallet.private_key[:30]}...')
            if wallet.mnemonic:
                print(f'  助记词: {wallet.mnemonic[:50]}...')
            print(f'  创建时间: {wallet.create_time}')
            print(f'  project_id: {wallet.project_id}')
            print(f'  project: {wallet.project}')
            print()
        
        print("✅ 测试通过！")
        
    except Exception as e:
        print(f'\n❌ 测试失败: {str(e)}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(test())
