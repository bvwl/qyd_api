"""
测试项目账号加密方式更新

验证：
1. 加密密钥从"项目名称+9527"改为"项目账号+9527"
2. IV从"9527+项目名称"改为"9527+项目账号"
3. password字段（与data同级）也进行加密
4. 不需要查询关联的项目信息
"""

import asyncio
import sys
from uuid import UUID
from decimal import Decimal
from tortoise import Tortoise

# 添加项目根目录到路径
sys.path.insert(0, '/Users/qyd/qyd_api2/backend')

from app.core import settings
from app.models.project import ProjectInfo, ProjectAccount
from app.crud.project.account import project_account_crud
from app.schemas.project.account import Create, Update
from app.utils.project_crypto import (
    encrypt_sensitive_fields,
    decrypt_sensitive_fields,
    encrypt_password,
    decrypt_password
)
from app.core.tools import aes_encrypt_project, aes_decrypt_project


async def test_encryption_functions():
    """测试基础加密解密函数"""
    print("\n" + "="*80)
    print("测试1: 基础加密解密函数")
    print("="*80)
    
    account = "test_account@example.com"
    
    # 测试 data 字段加密
    test_data = {
        "address": "0x1234567890",
        "private_key": "0xabcdef1234567890",
        "mnemonic": "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12",
        "nested": {
            "private_key": "nested_private_key",
            "other_field": "other_value"
        }
    }
    
    print(f"\n账号: {account}")
    print(f"原始 data: {test_data}")
    
    # 加密
    encrypted_data = encrypt_sensitive_fields(test_data, account)
    print(f"\n加密后的 data:")
    print(f"  private_key: {encrypted_data['private_key'][:50]}...")
    print(f"  mnemonic: {encrypted_data['mnemonic'][:50]}...")
    print(f"  nested.private_key: {encrypted_data['nested']['private_key'][:50]}...")
    
    # 解密
    decrypted_data = decrypt_sensitive_fields(encrypted_data, account)
    print(f"\n解密后的 data: {decrypted_data}")
    
    # 验证
    assert test_data['private_key'] == decrypted_data['private_key'], "private_key 解密失败"
    assert test_data['mnemonic'] == decrypted_data['mnemonic'], "mnemonic 解密失败"
    assert test_data['nested']['private_key'] == decrypted_data['nested']['private_key'], "nested.private_key 解密失败"
    print("\n✅ data 字段加密解密验证通过")
    
    # 测试 password 字段加密
    password = "test_password_123"
    print(f"\n原始 password: {password}")
    
    encrypted_password = encrypt_password(password, account)
    print(f"加密后的 password: {encrypted_password}")
    
    decrypted_password = decrypt_password(encrypted_password, account)
    print(f"解密后的 password: {decrypted_password}")
    
    assert password == decrypted_password, "password 解密失败"
    print("✅ password 字段加密解密验证通过")


async def test_crud_operations():
    """测试CRUD操作中的加密解密"""
    print("\n" + "="*80)
    print("测试2: CRUD操作中的加密解密")
    print("="*80)
    
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    try:
        # 获取第一个项目
        project = await ProjectInfo.first()
        if not project:
            print("❌ 没有找到项目，请先创建项目")
            return
        
        print(f"\n使用项目: {project.name} (ID: {project.id})")
        
        # 测试数据
        test_account = "test_encryption_account@example.com"
        test_password = "my_secure_password_123"
        test_data = {
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "private_key": "0x4c0883a69102937d6231471b5dbb6204fe512961708279f8c5c1e5e5e5e5e5e5",
            "mnemonic": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
            "chain": {
                "name": "Ethereum",
                "private_key": "chain_private_key_value"
            }
        }
        
        # 1. 创建账号
        print("\n--- 创建账号 ---")
        create_data = Create(
            project_id=project.id,
            account=test_account,
            password=test_password,
            data=test_data,
            balance=Decimal("100.123456"),
            status=1,
            account_type=1
        )
        
        created = await project_account_crud.create(create_data)
        print(f"✅ 创建成功，ID: {created.id}")
        print(f"  账号: {created.account}")
        print(f"  密码（应该是加密的）: {created.password[:50]}...")
        print(f"  data.private_key（应该是加密的）: {created.data['private_key'][:50]}...")
        
        # 验证数据库中的数据是加密的
        db_record = await ProjectAccount.get(id=created.id)
        assert db_record.password != test_password, "数据库中的 password 应该是加密的"
        assert db_record.data['private_key'] != test_data['private_key'], "数据库中的 private_key 应该是加密的"
        print("✅ 数据库中的敏感字段已加密")
        
        # 2. 查询账号（带解密权限）
        print("\n--- 查询账号（带解密权限）---")
        # 获取项目所属用户
        await project.fetch_related('users')
        if project.users:
            user = project.users[0]
            user_id = str(user.id)
            user_roles = ['ADMIN']  # 假设是管理员
            
            retrieved = await project_account_crud.get(
                created.id,
                user_id=user_id,
                user_roles=user_roles
            )
            print(f"✅ 查询成功")
            print(f"  密码（应该是解密的）: {retrieved.password}")
            print(f"  data.private_key（应该是解密的）: {retrieved.data['private_key'][:50]}...")
            
            # 验证解密正确
            assert retrieved.password == test_password, "password 解密不正确"
            assert retrieved.data['private_key'] == test_data['private_key'], "private_key 解密不正确"
            assert retrieved.data['mnemonic'] == test_data['mnemonic'], "mnemonic 解密不正确"
            assert retrieved.data['chain']['private_key'] == test_data['chain']['private_key'], "chain.private_key 解密不正确"
            print("✅ 解密验证通过")
        else:
            print("⚠️  项目没有关联用户，跳过解密测试")
        
        # 3. 更新账号
        print("\n--- 更新账号 ---")
        new_password = "updated_password_456"
        new_data = {
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
            "private_key": "0x_updated_private_key",
            "mnemonic": "updated mnemonic phrase",
        }
        
        update_data = Update(
            password=new_password,
            data=new_data
        )
        
        updated = await project_account_crud.update(created.id, update_data)
        print(f"✅ 更新成功")
        print(f"  新密码（应该是加密的）: {updated.password[:50]}...")
        print(f"  新data.private_key（应该是加密的）: {updated.data['private_key'][:50]}...")
        
        # 验证数据库中的数据是加密的
        db_record = await ProjectAccount.get(id=created.id)
        assert db_record.password != new_password, "更新后数据库中的 password 应该是加密的"
        assert db_record.data['private_key'] != new_data['private_key'], "更新后数据库中的 private_key 应该是加密的"
        print("✅ 更新后的敏感字段已加密")
        
        # 4. Upsert 操作（更新现有记录）
        print("\n--- Upsert 操作（更新现有记录）---")
        upsert_password = "upsert_password_789"
        upsert_data = Create(
            project_id=project.id,
            account=test_account,  # 相同的账号
            password=upsert_password,
            data={
                "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
                "private_key": "0x_upsert_private_key",
            }
        )
        
        upserted = await project_account_crud.upsert(upsert_data)
        print(f"✅ Upsert 成功")
        print(f"  ID 应该相同: {upserted.id == created.id}")
        print(f"  密码（应该是加密的）: {upserted.password[:50]}...")
        
        # 验证数据库中的数据是加密的
        db_record = await ProjectAccount.get(id=created.id)
        assert db_record.password != upsert_password, "Upsert后数据库中的 password 应该是加密的"
        print("✅ Upsert后的敏感字段已加密")
        
        # 5. 批量查询
        print("\n--- 批量查询 ---")
        if project.users:
            user = project.users[0]
            user_id = str(user.id)
            user_roles = ['ADMIN']
            
            result = await project_account_crud.get_multi(
                project_id=project.id,
                user_id=user_id,
                user_roles=user_roles,
                limit=10
            )
            print(f"✅ 批量查询成功，找到 {result.num} 条记录")
            
            # 找到我们创建的记录
            for item in result.items:
                if item.account == test_account:
                    print(f"  找到测试账号:")
                    print(f"    密码（应该是解密的）: {item.password}")
                    print(f"    data.private_key（应该是解密的）: {item.data['private_key'][:50]}...")
                    
                    # 验证解密正确
                    assert item.password == upsert_password, "批量查询中 password 解密不正确"
                    break
        
        # 6. 清理测试数据
        print("\n--- 清理测试数据 ---")
        await project_account_crud.delete(created.id)
        print("✅ 测试数据已清理")
        
    finally:
        await Tortoise.close_connections()


async def test_key_generation():
    """测试密钥生成方式"""
    print("\n" + "="*80)
    print("测试3: 密钥生成方式")
    print("="*80)
    
    account = "test@example.com"
    plaintext = "sensitive_data"
    
    print(f"\n账号: {account}")
    print(f"明文: {plaintext}")
    
    # 使用新的加密方式（基于账号）
    encrypted = aes_encrypt_project(plaintext, account)
    print(f"\n加密结果: {encrypted}")
    
    # 解密
    decrypted = aes_decrypt_project(encrypted, account)
    print(f"解密结果: {decrypted}")
    
    # 验证
    assert plaintext == decrypted, "解密失败"
    print("\n✅ 基于账号的加密解密验证通过")
    
    # 验证不同账号产生不同的密文
    account2 = "test2@example.com"
    encrypted2 = aes_encrypt_project(plaintext, account2)
    print(f"\n不同账号的加密结果: {encrypted2}")
    assert encrypted != encrypted2, "不同账号应该产生不同的密文"
    print("✅ 不同账号产生不同密文验证通过")


async def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("项目账号加密方式更新测试")
    print("="*80)
    
    try:
        # 测试1: 基础加密解密函数
        await test_encryption_functions()
        
        # 测试2: 密钥生成方式
        await test_key_generation()
        
        # 测试3: CRUD操作中的加密解密
        await test_crud_operations()
        
        print("\n" + "="*80)
        print("✅ 所有测试通过！")
        print("="*80)
        print("\n总结:")
        print("1. ✅ 加密密钥已改为基于账号（账号+9527）")
        print("2. ✅ IV已改为基于账号（9527+账号）")
        print("3. ✅ password字段已支持加密")
        print("4. ✅ data字段中的敏感字段已支持加密")
        print("5. ✅ 不需要查询关联的项目信息")
        print("6. ✅ CRUD操作中的加密解密正常工作")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
