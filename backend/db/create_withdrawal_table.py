#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接创建项目提现表
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


async def create_table():
    """创建表"""
    print("=" * 60)
    print("创建项目提现表")
    print("=" * 60)
    
    # 初始化数据库连接
    await Tortoise.init(config=settings.TORTOISE_ORM)
    print(f"✓ 数据库连接成功")
    print(f"  主机: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"  数据库: {settings.DB_NAME}")
    print()
    
    conn = Tortoise.get_connection("default")
    
    try:
        # 先检查表是否存在
        check_table_sql = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() 
        AND table_name = 'project_withdrawal'
        """
        result = await conn.execute_query(check_table_sql)
        table_exists = result[1][0]['count'] > 0
        
        if table_exists:
            print("⚠ project_withdrawal 表已存在，跳过创建")
        else:
            # 创建项目提现表（不包含外键约束，避免兼容性问题）
            create_table_sql = """
            CREATE TABLE `project_withdrawal` (
                `id` CHAR(36) NOT NULL PRIMARY KEY COMMENT 'UUID主键',
                `project_id` CHAR(36) NOT NULL COMMENT '所属项目ID',
                
                `platform_coin` DECIMAL(38, 18) NULL COMMENT '平台币当前余额',
                `platform_coin_change` DECIMAL(38, 18) NOT NULL DEFAULT 0 COMMENT '平台币最近一次变动',
                `platform_coin_history` JSON NULL COMMENT '平台币历史记录',
                
                `stable_coin` DECIMAL(38, 18) NULL COMMENT '稳定币当前余额',
                `stable_coin_change` DECIMAL(38, 18) NOT NULL DEFAULT 0 COMMENT '稳定币最近一次变动',
                `stable_coin_history` JSON NULL COMMENT '稳定币历史记录',
                
                `rmb` DECIMAL(20, 2) NULL COMMENT '人民币当前余额',
                `rmb_change` DECIMAL(20, 2) NOT NULL DEFAULT 0 COMMENT '人民币最近一次变动',
                `rmb_history` JSON NULL COMMENT '人民币历史记录',
                
                `remark` VARCHAR(500) NULL COMMENT '备注',
                `create_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
                `update_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
                
                UNIQUE KEY `uk_project_id` (`project_id`),
                KEY `idx_project_create` (`project_id`, `create_time`),
                KEY `idx_create_time` (`create_time`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目提现记录'
            """
            
            print("创建 project_withdrawal 表...")
            await conn.execute_query(create_table_sql)
            print("✓ 创建成功")
            
            # 尝试添加外键约束（如果失败也不影响功能）
            try:
                add_fk_sql = """
                ALTER TABLE `project_withdrawal` 
                ADD CONSTRAINT `fk_withdrawal_project` 
                FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE
                """
                print("\n添加外键约束...")
                await conn.execute_query(add_fk_sql)
                print("✓ 外键约束添加成功")
            except Exception as e:
                print(f"⚠ 外键约束添加失败（不影响功能）: {e}")
                print("  提示: 可以通过索引保证数据完整性")
        
        # 修改项目账号表的余额字段精度
        alter_table_sql = """
        ALTER TABLE `project_account` 
            MODIFY COLUMN `balance` DECIMAL(38, 18) NOT NULL DEFAULT 0 COMMENT '余额',
            MODIFY COLUMN `variable` DECIMAL(38, 18) NOT NULL DEFAULT 0 COMMENT '变动余额'
        """
        
        print("\n修改 project_account 表的余额字段精度...")
        try:
            await conn.execute_query(alter_table_sql)
            print("✓ 修改成功")
        except Exception as e:
            if "Duplicate" in str(e) or "already" in str(e):
                print(f"⚠ 字段已是正确类型，跳过")
            else:
                print(f"⚠ 修改失败: {e}")
        
        print("\n" + "=" * 60)
        print("✓ 完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(create_table())
