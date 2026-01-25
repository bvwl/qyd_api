"""
测试 XUI 入站账号 404 错误处理
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, close_db
from app.crud.xui.user import xui_inbound_account_crud
from fastapi import HTTPException


async def test_get_inbound_accounts_404():
    """测试获取不存在的入站账号列表"""
    print("=" * 60)
    print("测试 XUI 入站账号 404 错误处理")
    print("=" * 60)
    
    # 初始化数据库
    await init_db()
    
    try:
        # 测试 1: 不存在的入站 ID
        print("\n📋 测试 1: 查询不存在的入站")
        from uuid import uuid4
        fake_inbound_id = uuid4()
        
        try:
            result = await xui_inbound_account_crud.get_inbound_accounts(
                inbound_id=fake_inbound_id,
                page=1,
                limit=10
            )
            print(f"   ❌ 应该抛出 404 错误，但返回了结果")
        except HTTPException as e:
            if e.status_code == 404:
                print(f"   ✅ 正确抛出 404: {e.detail}")
            else:
                print(f"   ❌ 错误的状态码: {e.status_code}")
        
        # 测试 2: 存在的入站但没有账号
        print("\n📋 测试 2: 查询存在的入站但没有账号")
        from app.models.xui import XuiInbound
        
        # 获取第一个入站
        inbound = await XuiInbound.first()
        
        if not inbound:
            print("   ⚠️  数据库中没有入站，跳过此测试")
        else:
            print(f"   入站 ID: {inbound.id}")
            print(f"   入站地址: {inbound.listen_host}:{inbound.listen_port}")
            
            # 清空该入站的账号关联（用于测试）
            await inbound.accounts.clear()
            print(f"   已清空入站的账号关联")
            
            try:
                result = await xui_inbound_account_crud.get_inbound_accounts(
                    inbound_id=inbound.id,
                    page=1,
                    limit=10
                )
                print(f"   ❌ 应该抛出 404 错误，但返回了结果")
                print(f"   返回数据: {result}")
            except HTTPException as e:
                if e.status_code == 404:
                    print(f"   ✅ 正确抛出 404: {e.detail}")
                else:
                    print(f"   ❌ 错误的状态码: {e.status_code}")
        
        # 测试 3: 存在的入站且有账号
        print("\n📋 测试 3: 查询存在的入站且有账号")
        
        if inbound:
            # 添加一个测试账号
            from app.models.server import ServerAccount
            from app.core.tools import aes_encrypt
            
            # 创建测试账号
            test_account = await ServerAccount.create(
                username='test_user_404',
                password=aes_encrypt('test_password', 'test_user_404')
            )
            print(f"   创建测试账号: {test_account.username}")
            
            # 关联到入站
            await inbound.accounts.add(test_account)
            print(f"   已关联账号到入站")
            
            try:
                result = await xui_inbound_account_crud.get_inbound_accounts(
                    inbound_id=inbound.id,
                    page=1,
                    limit=10
                )
                print(f"   ✅ 成功返回账号列表")
                print(f"   账号数量: {result.num}")
                print(f"   账号列表: {[item.username for item in result.items]}")
            except HTTPException as e:
                print(f"   ❌ 不应该抛出错误: {e.status_code} - {e.detail}")
            
            # 清理测试数据
            await inbound.accounts.remove(test_account)
            await test_account.delete()
            print(f"   已清理测试数据")
        
        print(f"\n✅ 测试完成！")
    
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        await close_db()


async def test_api_endpoint():
    """测试 API 端点"""
    print("\n" + "=" * 60)
    print("API 端点测试说明")
    print("=" * 60)
    
    print("\n📝 测试命令:")
    print("\n1. 测试不存在的入站 ID:")
    print("   curl -X GET 'http://127.0.0.1:6080/v1/xui/account/inbound/00000000-0000-0000-0000-000000000000' \\")
    print("     -H 'Authorization: Bearer YOUR_TOKEN'")
    print("   预期: 404 - 入站不存在")
    
    print("\n2. 测试存在的入站但没有账号:")
    print("   curl -X GET 'http://127.0.0.1:6080/v1/xui/account/inbound/{INBOUND_ID}' \\")
    print("     -H 'Authorization: Bearer YOUR_TOKEN'")
    print("   预期: 404 - 未查询到数据")
    
    print("\n3. 测试存在的入站且有账号:")
    print("   # 先添加账号到入站")
    print("   curl -X POST 'http://127.0.0.1:6080/v1/xui/account/add' \\")
    print("     -H 'Authorization: Bearer YOUR_TOKEN' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"inbound_id\": \"{INBOUND_ID}\", \"account_id\": \"{ACCOUNT_ID}\"}'")
    print("\n   # 然后查询账号列表")
    print("   curl -X GET 'http://127.0.0.1:6080/v1/xui/account/inbound/{INBOUND_ID}' \\")
    print("     -H 'Authorization: Bearer YOUR_TOKEN'")
    print("   预期: 200 - 返回账号列表")


if __name__ == '__main__':
    # 测试 CRUD 层
    asyncio.run(test_get_inbound_accounts_404())
    
    # 显示 API 测试说明
    asyncio.run(test_api_endpoint())
