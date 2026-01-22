#!/usr/bin/env python3
"""
手动应用余额字段迁移
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tortoise import Tortoise
from app.core import settings


async def apply_migration():
    """应用余额字段迁移"""
    # 初始化数据库连接
    await Tortoise.init(config=settings.TORTOISE_ORM)
    
    # 获取数据库连接
    conn = Tortoise.get_connection("default")
    
    print("开始应用余额字段迁移...")
    
    try:
        # 检查字段是否已存在
        result = await conn.execute_query_dict(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'project_account' AND COLUMN_NAME = 'balance'",
            [settings.DB_NAME]
        )
        
        if result:
            print("✅ 余额字段已存在，无需迁移")
            return
        
        print("1. 添加余额相关字段...")
        await conn.execute_script("""
            ALTER TABLE `project_account` ADD `balance` DECIMAL(18,6) NOT NULL DEFAULT 0 COMMENT '余额';
            ALTER TABLE `project_account` ADD `variable` DECIMAL(18,6) NOT NULL DEFAULT 0 COMMENT '变动余额';
            ALTER TABLE `project_account` ADD `balance_history` JSON NULL COMMENT '历史余额';
        """)
        print("   ✅ 字段添加成功")
        
        print("2. 检查是否存在 project_balance 表...")
        result = await conn.execute_query_dict(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'project_balance'",
            [settings.DB_NAME]
        )
        
        if result:
            print("3. 迁移 project_balance 表的数据...")
            await conn.execute_query("""
                UPDATE project_account pa
                INNER JOIN project_balance pb ON pa.id = pb.account_id
                SET pa.balance = pb.balance,
                    pa.variable = pb.variable,
                    pa.balance_history = pb.history
            """)
            print("   ✅ 数据迁移成功")
            
            print("4. 删除 project_balance 表...")
            await conn.execute_query("DROP TABLE IF EXISTS `project_balance`")
            print("   ✅ 旧表删除成功")
        else:
            print("   ℹ️  project_balance 表不存在，跳过数据迁移")
        
        print("5. 添加余额字段索引...")
        await conn.execute_query(
            "CREATE INDEX `idx_project_account_balance` ON `project_account` (`balance`)"
        )
        print("   ✅ 索引创建成功")
        
        print("\n✅ 迁移完成！")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        raise
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(apply_migration())
