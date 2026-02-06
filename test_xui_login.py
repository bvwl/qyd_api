#!/usr/bin/env python3
"""测试 XUI 登录"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.clients.xui import XuiClient


async def test_login(host, port, username, password, is_ssl=False, web_path='/web3'):
    """测试登录"""
    print(f"\n=== 测试 XUI 登录 ===")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Username: {username}")
    print(f"SSL: {is_ssl}")
    print(f"Web Path: {web_path}")
    
    protocol = 'https' if is_ssl else 'http'
    base_url = f'{protocol}://{host}:{port}{web_path}'
    login_url = f'{base_url}/login'
    print(f"Login URL: {login_url}\n")
    
    client = XuiClient(
        host=host,
        port=port,
        username=username,
        password=password,
        is_ssl=is_ssl,
        web_path=web_path
    )
    
    try:
        result = await client.login()
        if result:
            print("✅ 登录成功！")
        else:
            print("❌ 登录失败")
    except Exception as e:
        print(f"❌ 登录异常: {e}")


async def main():
    """主函数"""
    # 从命令行参数获取配置
    if len(sys.argv) < 5:
        print("用法: python test_xui_login.py <host> <port> <username> <password> [web_path]")
        print("示例: python test_xui_login.py zd16.0n.lv 10010 admin password123 /web3")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    username = sys.argv[3]
    password = sys.argv[4]
    web_path = sys.argv[5] if len(sys.argv) > 5 else '/web3'
    
    # 测试不同的 web_path
    print("测试 1: 使用指定的 web_path")
    await test_login(host, port, username, password, False, web_path)
    
    if web_path != '':
        print("\n" + "="*50)
        print("测试 2: 使用空 web_path")
        await test_login(host, port, username, password, False, '')


if __name__ == '__main__':
    asyncio.run(main())
