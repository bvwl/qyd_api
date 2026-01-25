#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import aiomysql
from dotenv import load_dotenv

load_dotenv()

async def check_table():
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', 3307)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'db': os.getenv('DB_NAME', 'qyd'),
        'charset': 'utf8mb4',
    }

    conn = await aiomysql.connect(**db_config)
    cursor = await conn.cursor()

    try:
        await cursor.execute("SHOW CREATE TABLE users")
        result = await cursor.fetchone()
        print("users 表结构:")
        print(result[1])
        
        print("\n" + "="*80 + "\n")
        
        await cursor.execute("SHOW CREATE TABLE xui_inbound")
        result = await cursor.fetchone()
        print("xui_inbound 表结构:")
        print(result[1])
        
        print("\n" + "="*80 + "\n")
        
        await cursor.execute("SHOW CREATE TABLE server_accounts")
        result = await cursor.fetchone()
        print("server_accounts 表结构:")
        print(result[1])

    finally:
        await cursor.close()
        conn.close()

if __name__ == '__main__':
    asyncio.run(check_table())
