#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查提现记录数据
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载.env文件
from dotenv import load_dotenv
env_path = project_root / '.env'
load_dotenv(env_path)

from tortoise import Tortoise
from app.core import settings


async def check_data():
    """检查数据"""
    await Tortoise.init(config=settings.TORTOISE_ORM)
    conn = Tortoise.get_connection('default')
    
    try:
        # 查看所有提现记录
        result = await conn.execute_query('SELECT id, project_id FROM project_withdrawal')
        print('提现记录:')
        print('-' * 80)
        for row in result[1]:
            print(f'  ID: {row["id"]}, Project ID: {row["project_id"]}')
        
        # 查找NULL project_id的记录
        result = await conn.execute_query('SELECT COUNT(*) as count FROM project_withdrawal WHERE project_id IS NULL')
        null_count = result[1][0]['count']
        print(f'\nNULL project_id 记录数: {null_count}')
        
        if null_count > 0:
            print('\n删除NULL project_id的记录...')
            await conn.execute_query('DELETE FROM project_withdrawal WHERE project_id IS NULL')
            print('✓ 删除完成')
        
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(check_data())
