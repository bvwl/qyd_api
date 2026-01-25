#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查 project_info 表结构
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


async def check_table():
    """检查表结构"""
    await Tortoise.init(config=settings.TORTOISE_ORM)
    conn = Tortoise.get_connection('default')
    
    try:
        # 查看 project_info 表结构
        result = await conn.execute_query('DESCRIBE project_info')
        print('project_info 表结构:')
        print('-' * 80)
        for row in result[1]:
            print(f'  {row}')
        
        print('\n' + '=' * 80)
        
        # 查看 project_withdrawal 表是否存在
        try:
            result = await conn.execute_query('DESCRIBE project_withdrawal')
            print('project_withdrawal 表结构:')
            print('-' * 80)
            for row in result[1]:
                print(f'  {row}')
        except Exception as e:
            print(f'project_withdrawal 表不存在: {e}')
        
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(check_table())
