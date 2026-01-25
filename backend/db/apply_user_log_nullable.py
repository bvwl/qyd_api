#!/usr/bin/env python3
"""
修改 user_logs 表,让 user_id 可以为空
用于记录系统操作日志
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import aiomysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


async def apply_migration():
    """应用数据库迁移"""
    # 数据库配置
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', 3307)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'db': os.getenv('DB_NAME', 'qyd'),
        'charset': 'utf8mb4',
    }

    print(f"连接数据库: {db_config['host']}:{db_config['port']}/{db_config['db']}")

    # 连接数据库
    conn = await aiomysql.connect(**db_config)
    cursor = await conn.cursor()

    try:
        # 读取 SQL 文件
        sql_file = Path(__file__).parent / 'update_user_log_nullable.sql'
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 执行 SQL
        print("\n执行 SQL:")
        print(sql_content)
        
        await cursor.execute(sql_content)
        await conn.commit()

        print("\n✅ 迁移成功!")
        print("user_logs.user_id 字段已修改为可空")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        await conn.rollback()
        raise
    finally:
        await cursor.close()
        conn.close()


if __name__ == '__main__':
    asyncio.run(apply_migration())
