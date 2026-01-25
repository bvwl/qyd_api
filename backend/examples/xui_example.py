"""
XUI 客户端使用示例
"""
import asyncio
from app.clients.xui import XuiClient


async def example_basic_usage():
    """基础使用示例"""
    # 初始化客户端
    client = XuiClient(
        host='31.57.104.150',
        port=10010,
        username='admin',
        password='admin',
        is_ssl=False
    )
    
    # 登录
    await client.login()
    
    # 获取入站列表
    inbounds = await client.get_inbounds()
    print(f'入站数量: {len(inbounds.get("obj", []))}')
    
    # 添加入站
    inbound_id = await client.add_inbound(
        host='192.168.1.100',
        port=21000,
        protocol='http',
        username='user1',
        password='pass1'
    )
    print(f'添加入站 ID: {inbound_id}')
    
    # 获取服务器状态
    status = await client.get_server_status()
    print(f'服务器状态: {status}')


async def example_user_management():
    """用户管理示例"""
    client = XuiClient(
        host='31.57.104.150',
        username='admin',
        password='admin'
    )
    
    await client.login()
    
    # 添加用户到入站
    success = await client.add_user_to_inbound(
        host='192.168.1.100',
        port=21000,
        username='newuser',
        password='newpass'
    )
    print(f'添加用户: {success}')
    
    # 删除用户
    success = await client.remove_user_from_inbound(
        host='192.168.1.100',
        port=21000,
        username='newuser',
        password='newpass'
    )
    print(f'删除用户: {success}')


async def example_batch_operations():
    """批量操作示例"""
    client = XuiClient(
        host='31.57.104.150',
        username='admin',
        password='admin'
    )
    
    await client.login()
    
    # 批量添加入站
    inbound_configs = [
        {'host': '192.168.1.100', 'port': 21000, 'protocol': 'http'},
        {'host': '192.168.1.100', 'port': 31000, 'protocol': 'socks'},
        {'host': '192.168.1.101', 'port': 21001, 'protocol': 'http'},
        {'host': '192.168.1.101', 'port': 31001, 'protocol': 'socks'},
    ]
    
    results = await client.batch_add_inbounds(inbound_configs)
    print(f'批量添加结果: {results}')
    
    # 批量添加用户
    user_configs = [
        {'host': '192.168.1.100', 'port': 21000, 'username': 'user1', 'password': 'pass1'},
        {'host': '192.168.1.100', 'port': 31000, 'username': 'user1', 'password': 'pass1'},
    ]
    
    results = await client.batch_add_users(user_configs)
    print(f'批量添加用户结果: {results}')


async def example_full_initialization():
    """完整初始化示例"""
    client = XuiClient(
        host='31.57.104.150',
        username='admin',
        password='admin'
    )
    
    # 准备入站配置
    inbound_configs = []
    
    # 从文件读取 IP 列表
    with open('ip.txt', 'r') as f:
        ips = [line.strip() for line in f if line.strip()]
    
    # 为每个 IP 生成 HTTP 和 SOCKS 入站
    for i, ip in enumerate(ips):
        inbound_configs.extend([
            {
                'host': ip,
                'port': 22000 + i,
                'protocol': 'http',
                'username': 'cqrxy',
                'password': 'Zpaily88'
            },
            {
                'host': ip,
                'port': 32000 + i,
                'protocol': 'socks',
                'username': 'cqrxy',
                'password': 'Zpaily88'
            }
        ])
    
    # 一键初始化
    success = await client.initialize_xui_panel(
        inbound_configs=inbound_configs,
        cert_file='/opt/xui/fullchain.pem',
        key_file='/opt/xui/privkey.pem'
    )
    
    print(f'初始化完成: {success}')


async def example_outbound_routing():
    """出站和路由配置示例"""
    client = XuiClient(
        host='31.57.104.150',
        username='admin',
        password='admin'
    )
    
    await client.login()
    
    # 配置出站和路由
    inbound_tags = [
        {'host': '192.168.1.100', 'port': 21000},
        {'host': '192.168.1.100', 'port': 31000},
        {'host': '192.168.1.101', 'port': 21001},
        {'host': '192.168.1.101', 'port': 31001},
    ]
    
    success = await client.configure_outbound_and_routing(inbound_tags)
    print(f'配置出站和路由: {success}')
    
    # 重启 Xray 服务
    await client.restart_xray()


if __name__ == '__main__':
    # 运行示例
    asyncio.run(example_basic_usage())
    # asyncio.run(example_user_management())
    # asyncio.run(example_batch_operations())
    # asyncio.run(example_full_initialization())
    # asyncio.run(example_outbound_routing())
