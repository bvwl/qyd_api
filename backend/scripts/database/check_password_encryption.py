"""
检查数据库中的 password 字段是否已加密
"""

import asyncio
import sys
from tortoise import Tortoise

sys.path.insert(0, '/Users/qyd/qyd_api2/backend')

from app.core import settings
from app.models.project import ProjectAccount


async def check_password_encryption():
    """检查数据库中的 password 加密情况"""
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    try:
        # 查询最近创建的账号
        accounts = await ProjectAccount.all().order_by('-create_time').limit(10)
        
        print("\n" + "="*80)
        print("最近创建的10个项目账号的 password 字段检查")
        print("="*80)
        
        for account in accounts:
            print(f"\n账号: {account.account}")
            print(f"  ID: {account.id}")
            print(f"  项目ID: {account.project_id}")
            print(f"  创建时间: {account.create_time}")
            
            if account.password:
                print(f"  密码长度: {len(account.password)}")
                print(f"  密码内容: {account.password}")
                
                # 判断是否加密（加密后的密码通常是Base64编码，长度较长且包含特殊字符）
                if len(account.password) > 20 and ('=' in account.password or '+' in account.password or '/' in account.password):
                    print(f"  ✅ 密码已加密（Base64格式）")
                else:
                    print(f"  ❌ 密码未加密（明文）")
            else:
                print(f"  ⚠️  密码为空")
        
        # 查询特定账号
        print("\n" + "="*80)
        print("查询特定账号: hsm48786@kisoq.com")
        print("="*80)
        
        specific_account = await ProjectAccount.filter(account="hsm48786@kisoq.com").first()
        if specific_account:
            print(f"\n找到账号:")
            print(f"  ID: {specific_account.id}")
            print(f"  账号: {specific_account.account}")
            print(f"  项目ID: {specific_account.project_id}")
            print(f"  创建时间: {specific_account.create_time}")
            
            if specific_account.password:
                print(f"  密码: {specific_account.password}")
                print(f"  密码长度: {len(specific_account.password)}")
                
                # 尝试解密
                from app.utils.project_crypto import decrypt_password
                try:
                    decrypted = decrypt_password(specific_account.password, specific_account.account)
                    print(f"  解密后的密码: {decrypted}")
                    
                    if decrypted == specific_account.password:
                        print(f"  ❌ 密码未加密（解密后与原文相同）")
                    else:
                        print(f"  ✅ 密码已加密（解密成功）")
                except Exception as e:
                    print(f"  ❌ 解密失败: {e}")
                    print(f"  可能是明文密码")
            else:
                print(f"  ⚠️  密码为空")
        else:
            print("\n未找到该账号")
        
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(check_password_encryption())
