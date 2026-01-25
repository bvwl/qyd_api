"""
直接创建统计表
"""
import asyncio
import aiomysql
import os
from dotenv import load_dotenv

load_dotenv()

async def create_table():
    # 读取SQL文件
    with open('db/create_project_daily_stats.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # 连接数据库
    conn = await aiomysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        port=int(os.getenv('DB_PORT', 3307)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        db=os.getenv('DB_NAME', 'qyd'),
        charset='utf8mb4'
    )
    
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(sql)
            await conn.commit()
            print("✅ 表创建成功")
    finally:
        conn.close()

if __name__ == '__main__':
    asyncio.run(create_table())
