#!/bin/bash
# 检查 XUI 服务器的 web_path 配置

echo "=== 检查 XUI 服务器配置 ==="
echo ""

# 进入容器执行 Python 脚本
docker exec -it qyd-backend-api python -c "
import asyncio
from app.core.database import init_db, close_db
from app.models.xui import XuiServer

async def main():
    await init_db()
    try:
        servers = await XuiServer.all()
        if not servers:
            print('❌ 没有找到任何 XUI 服务器')
            return
        
        print(f'✅ 找到 {len(servers)} 个 XUI 服务器:\n')
        
        for server in servers:
            print(f'服务器: {server.name}')
            print(f'  - ID: {server.id}')
            print(f'  - Host: {server.host}')
            print(f'  - Domain: {server.domain}')
            print(f'  - Port: {server.port}')
            print(f'  - Username: {server.username}')
            print(f'  - SSL: {server.is_ssl}')
            print(f'  - Web Path: {server.web_path}')
            
            protocol = 'https' if server.is_ssl else 'http'
            connect_host = server.domain if server.domain else server.host
            base_url = f'{protocol}://{connect_host}:{server.port}{server.web_path}'
            login_url = f'{base_url}/login'
            
            print(f'  - Base URL: {base_url}')
            print(f'  - Login URL: {login_url}')
            print()
    finally:
        await close_db()

asyncio.run(main())
"
