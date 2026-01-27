#!/usr/bin/env python3
"""
检查用户的服务器账号配置

用法:
python check_server_account.py <user_email>
"""

import asyncio
import sys
from app.models.user import UserInfo
from app.models.server import ServerAccount
from app.core.database import init_db, close_db
from app.core.tools import aes_decrypt


async def check_user_server_account(email: str):
    """检查用户的服务器账号"""
    
    # 初始化数据库
    await init_db()
    
    try:
        print("=" * 60)
        print(f"检查用户服务器账号: {email}")
        print("=" * 60)
        
        # 1. 查找用户
        print(f"\n1. 查找用户...")
        user = await UserInfo.get_or_none(email=email)
        
        if not user:
            print(f"   ✗ 用户不存在: {email}")
            return
        
        print(f"   ✓ 用户ID: {user.id}")
        print(f"   ✓ 昵称: {user.nickname}")
        print(f"   ✓ 状态: {user.status}")
        
        # 2. 查找服务器账号
        print(f"\n2. 查找服务器账号...")
        account = await ServerAccount.get_or_none(user_id=user.id)
        
        if not account:
            print(f"   ✗ 未找到服务器账号")
            print(f"\n   建议: 为用户创建服务器账号")
            print(f"   ```python")
            print(f"   from app.models.server import ServerAccount")
            print(f"   from app.core.tools import aes_encrypt")
            print(f"   ")
            print(f"   encrypted_password = aes_encrypt('your_password', '{user.id}')")
            print(f"   account = await ServerAccount.create(")
            print(f"       username='your_username',")
            print(f"       password=encrypted_password,")
            print(f"       user_id='{user.id}'")
            print(f"   )")
            print(f"   ```")
            return
        
        print(f"   ✓ 账号ID: {account.id}")
        print(f"   ✓ 用户名: {account.username}")
        print(f"   ✓ 密码(加密): {account.password[:50]}...")
        print(f"   ✓ 是否已添加到所有入站: {account.is_all_inbound_added}")
        
        # 3. 尝试解密密码
        print(f"\n3. 尝试解密密码...")
        try:
            decrypted_password = aes_decrypt(account.password, str(user.id))
            print(f"   ✓ 密码解密成功")
            print(f"   ✓ 明文密码: {decrypted_password}")
        except Exception as e:
            print(f"   ✗ 密码解密失败: {e}")
        
        # 4. 生成代理 URL 示例
        print(f"\n4. 代理 URL 示例:")
        print(f"   HTTP:    http://{account.username}:{decrypted_password}@proxy.example.com:25000")
        print(f"   SOCKS5:  socks5://{account.username}:{decrypted_password}@proxy.example.com:35000")
        
        print("\n" + "=" * 60)
        print("检查完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        await close_db()


async def list_all_accounts():
    """列出所有服务器账号"""
    
    # 初始化数据库
    await init_db()
    
    try:
        print("=" * 60)
        print("所有服务器账号列表")
        print("=" * 60)
        
        accounts = await ServerAccount.all().prefetch_related('user')
        
        if not accounts:
            print("\n没有找到任何服务器账号")
            return
        
        print(f"\n共找到 {len(accounts)} 个服务器账号:\n")
        
        for i, account in enumerate(accounts, 1):
            user = account.user
            print(f"{i}. 账号ID: {account.id}")
            print(f"   用户名: {account.username}")
            if user:
                print(f"   关联用户: {user.email} ({user.nickname})")
                print(f"   用户ID: {user.id}")
            else:
                print(f"   关联用户: 无")
            print(f"   创建时间: {account.create_time}")
            print()
        
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        await close_db()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  检查特定用户: python check_server_account.py <user_email>")
        print("  列出所有账号: python check_server_account.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        asyncio.run(list_all_accounts())
    else:
        email = sys.argv[1]
        asyncio.run(check_user_server_account(email))
