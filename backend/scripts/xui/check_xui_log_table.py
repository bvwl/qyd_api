"""
检查 xui_operation_logs 表结构
"""
import asyncio
import os
from tortoise import Tortoise

async def check_table():
    # 从环境变量读取数据库配置
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', '3307'))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'qyd')
    
    await Tortoise.init(
        db_url=f'mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
        modules={'models': ['app.models']}
    )
    
    conn = Tortoise.get_connection('default')
    
    # 检查表是否存在
    result = await conn.execute_query(
        "SHOW TABLES LIKE 'xui_operation_logs'"
    )
    
    if result[1]:
        print('✓ 表存在,检查表结构:')
        print('-' * 80)
        result = await conn.execute_query(
            'DESCRIBE xui_operation_logs'
        )
        for row in result[1]:
            print(f'  {row[0]:20} {row[1]:20} {row[2]:5} {row[3]:5} {row[4] or "":20}')
        print('-' * 80)
        
        # 检查是否有 status 字段
        has_status = any(row[0] == 'status' for row in result[1])
        has_is_resolved = any(row[0] == 'is_resolved' for row in result[1])
        
        print(f'\n字段检查:')
        print(f'  status 字段: {"存在 ❌" if has_status else "不存在 ✓"}')
        print(f'  is_resolved 字段: {"存在 ✓" if has_is_resolved else "不存在 ❌"}')
        
        if has_status:
            print('\n⚠️  发现旧的 status 字段,需要删除并重新创建表')
    else:
        print('✗ 表不存在,需要创建')
    
    await Tortoise.close_connections()

if __name__ == '__main__':
    asyncio.run(check_table())
