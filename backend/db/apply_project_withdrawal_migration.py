#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
应用项目提现表迁移
"""
import asyncio
import sys
import os
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


async def apply_migration():
    """应用迁移"""
    print("=" * 60)
    print("应用项目提现表迁移")
    print("=" * 60)
    
    # 初始化数据库连接
    await Tortoise.init(config=settings.TORTOISE_ORM)
    print(f"✓ 数据库连接成功")
    print(f"  主机: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"  数据库: {settings.DB_NAME}")
    print()
    
    conn = Tortoise.get_connection("default")
    
    try:
        # 读取SQL文件
        sql_file = Path(__file__).parent / 'add_project_withdrawal.sql'
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句
        sql_statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        # 执行每条SQL语句
        for i, sql in enumerate(sql_statements, 1):
            print(f"\n执行SQL语句 {i}/{len(sql_statements)}...")
            print(f"SQL: {sql[:100]}...")
            
            try:
                await conn.execute_script(sql)
                print(f"✓ 执行成功")
            except Exception as e:
                if "already exists" in str(e) or "Duplicate" in str(e):
                    print(f"⚠ 已存在，跳过: {e}")
                else:
                    print(f"✗ 执行失败: {e}")
                    raise
        
        print("\n" + "=" * 60)
        print("✓ 迁移完成！")
        print("=" * 60)
        print("\n创建的表：")
        print("  - project_withdrawal (项目提现记录)")
        print("\n修改的表：")
        print("  - project_account (余额字段精度：18位小数)")
        
    except Exception as e:
        print(f"\n✗ 迁移失败: {e}")
        raise
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(apply_migration())
