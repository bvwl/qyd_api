#!/usr/bin/env python3
"""
应用项目每日统计表迁移
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM


async def apply_migration():
    """应用迁移"""
    print("=" * 60)
    print("应用项目每日统计表迁移")
    print("=" * 60)
    
    # 初始化数据库连接
    await Tortoise.init(config=TORTOISE_ORM)
    
    try:
        # 获取数据库连接
        conn = Tortoise.get_connection("default")
        
        # 读取SQL文件
        sql_file = os.path.join(os.path.dirname(__file__), 'create_project_daily_stats.sql')
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # 执行SQL
        print("\n执行SQL...")
        await conn.execute_script(sql)
        print("✅ 项目每日统计表创建成功")
        
        # 验证表是否创建
        result = await conn.execute_query(
            "SELECT COUNT(*) as count FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = 'project_daily_stats'"
        )
        
        if result[1][0]['count'] > 0:
            print("✅ 表验证成功")
            
            # 显示表结构
            columns = await conn.execute_query("DESCRIBE project_daily_stats")
            print("\n表结构:")
            for col in columns[1]:
                print(f"  - {col['Field']}: {col['Type']} {col['Null']} {col['Key']}")
        else:
            print("❌ 表验证失败")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(apply_migration())
