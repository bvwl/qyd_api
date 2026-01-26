#!/usr/bin/env python3
"""
测试代理 URL 生成功能

测试场景：
1. 用户有服务器账号 - 使用服务器账号的用户名和密码
2. 用户没有服务器账号 - 使用默认的 username:password
"""

import asyncio
from uuid import UUID
from app.models.server import ServerInfo, ServerAccount
from app.models.user import UserInfo
from app.crud.server.info import server_info_crud
from app.core.database import init_db, close_db
from app.core.tools import aes_encrypt


async def test_proxy_url_generation():
    """测试代理 URL 生成"""
    
    # 初始化数据库
    await init_db()
    
    try:
        print("=" * 60)
        print("测试代理 URL 生成功能")
        print("=" * 60)
        
        # 1. 创建测试用户
        print("\n1. 创建测试用户...")
        test_user = await UserInfo.create(
            email="test_proxy@example.com",
            password="hashed_password",
            nickname="测试用户"
        )
        print(f"   ✓ 用户创建成功: {test_user.email} (ID: {test_user.id})")
        
        # 2. 创建服务器账号
        print("\n2. 创建服务器账号...")
        encrypted_password = aes_encrypt("my_proxy_password", str(test_user.id))
        server_account = await ServerAccount.create(
            username="my_proxy_user",
            password=encrypted_password,
            user_id=test_user.id
        )
        print(f"   ✓ 服务器账号创建成功: {server_account.username}")
        
        # 3. 创建测试服务器
        print("\n3. 创建测试服务器...")
        test_server = await ServerInfo.create(
            host="192.168.1.100",
            domain="proxy.example.com",
            port=25000,  # HTTP 代理端口
            ssh_port=22
        )
        print(f"   ✓ 服务器创建成功: {test_server.host}:{test_server.port}")
        
        # 4. 测试场景1：有服务器账号的用户
        print("\n4. 测试场景1：有服务器账号的用户")
        current_user = {
            'user_id': str(test_user.id),
            'email': test_user.email
        }
        
        proxy_url, proxy_type = await server_info_crud._generate_proxy_url(
            test_server, 
            current_user
        )
        
        print(f"   代理类型: {proxy_type}")
        print(f"   代理 URL: {proxy_url}")
        print(f"   预期格式: http://my_proxy_user:my_proxy_password@proxy.example.com:25000")
        
        # 验证
        expected_url = f"http://my_proxy_user:my_proxy_password@proxy.example.com:25000"
        if proxy_url == expected_url:
            print("   ✓ 测试通过！")
        else:
            print(f"   ✗ 测试失败！预期: {expected_url}")
        
        # 5. 测试场景2：没有服务器账号的用户
        print("\n5. 测试场景2：没有服务器账号的用户")
        test_user2 = await UserInfo.create(
            email="test_no_account@example.com",
            password="hashed_password",
            nickname="无账号用户"
        )
        
        current_user2 = {
            'user_id': str(test_user2.id),
            'email': test_user2.email
        }
        
        proxy_url2, proxy_type2 = await server_info_crud._generate_proxy_url(
            test_server,
            current_user2
        )
        
        print(f"   代理类型: {proxy_type2}")
        print(f"   代理 URL: {proxy_url2}")
        print(f"   预期格式: http://username:password@proxy.example.com:25000")
        
        # 验证
        expected_url2 = f"http://username:password@proxy.example.com:25000"
        if proxy_url2 == expected_url2:
            print("   ✓ 测试通过！")
        else:
            print(f"   ✗ 测试失败！预期: {expected_url2}")
        
        # 6. 测试场景3：SOCKS5 代理
        print("\n6. 测试场景3：SOCKS5 代理")
        test_server_socks5 = await ServerInfo.create(
            host="192.168.1.101",
            port=35000,  # SOCKS5 代理端口
            ssh_port=22
        )
        
        proxy_url3, proxy_type3 = await server_info_crud._generate_proxy_url(
            test_server_socks5,
            current_user
        )
        
        print(f"   代理类型: {proxy_type3}")
        print(f"   代理 URL: {proxy_url3}")
        print(f"   预期格式: socks5://my_proxy_user:my_proxy_password@192.168.1.101:35000")
        
        # 验证
        expected_url3 = f"socks5://my_proxy_user:my_proxy_password@192.168.1.101:35000"
        if proxy_url3 == expected_url3:
            print("   ✓ 测试通过！")
        else:
            print(f"   ✗ 测试失败！预期: {expected_url3}")
        
        # 7. 测试场景4：没有用户信息
        print("\n7. 测试场景4：没有用户信息（匿名访问）")
        proxy_url4, proxy_type4 = await server_info_crud._generate_proxy_url(
            test_server,
            None
        )
        
        print(f"   代理类型: {proxy_type4}")
        print(f"   代理 URL: {proxy_url4}")
        print(f"   预期格式: http://username:password@proxy.example.com:25000")
        
        # 验证
        if proxy_url4 == expected_url2:
            print("   ✓ 测试通过！")
        else:
            print(f"   ✗ 测试失败！预期: {expected_url2}")
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
        # 清理测试数据
        print("\n清理测试数据...")
        await test_server.delete()
        await test_server_socks5.delete()
        await server_account.delete()
        await test_user.delete()
        await test_user2.delete()
        print("✓ 清理完成")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        await close_db()


if __name__ == "__main__":
    asyncio.run(test_proxy_url_generation())
