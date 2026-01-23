#!/usr/bin/env python3
"""
应用Token字段长度迁移
将 tokens 表的 token 字段从 VARCHAR(255) 改为 VARCHAR(512)
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import aiomysql

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载.env文件
env_path = project_root / '.env'
load_dotenv(env_path)

# 获取数据库配置
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3307"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "qyd")


async def apply_migration():
    """应用迁移"""
    print("=" * 60)
    print("应用Token字段长度迁移")
    print("=" * 60)
    print()
    
    print(f"数据库配置:")
    print(f"  主机: {DB_HOST}:{DB_PORT}")
    print(f"  数据库: {DB_NAME}")
    print(f"  用户: {DB_USER}")
    print()
    
    try:
        # 连接数据库
        print("正在连接数据库...")
        conn = await aiomysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset='utf8mb4'
        )
        print("✓ 数据库连接成功")
        print()
        
        async with conn.cursor() as cursor:
            # 1. 查看当前表结构
            print("1. 查看当前 tokens 表结构:")
            print("-" * 60)
            await cursor.execute("DESCRIBE tokens")
            result = await cursor.fetchall()
            for row in result:
                if row[0] == 'token':
                    print(f"  当前 token 字段: {row[1]}")
            print()
            
            # 2. 修改字段类型为TEXT
            print("2. 修改 token 字段类型为 TEXT:")
            print("-" * 60)
            sql = "ALTER TABLE tokens MODIFY COLUMN token TEXT NOT NULL COMMENT '访问令牌'"
            print(f"  执行SQL: {sql}")
            await cursor.execute(sql)
            await conn.commit()
            print("✓ 字段类型修改成功")
            print()
            
            # 3. 验证修改结果
            print("3. 验证修改结果:")
            print("-" * 60)
            await cursor.execute("DESCRIBE tokens")
            result = await cursor.fetchall()
            for row in result:
                if row[0] == 'token':
                    print(f"  修改后 token 字段: {row[1]}")
                    if 'text' in row[1].lower():
                        print("✓ 验证成功：字段类型已更新为 TEXT")
                    else:
                        print("✗ 验证失败：字段类型未正确更新")
            print()
        
        conn.close()
        
        print("=" * 60)
        print("✅ 迁移完成！")
        print("=" * 60)
        print()
        print("现在可以生成任意长度的JWT Token了（TEXT类型支持最大65535字符）")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(apply_migration())
    sys.exit(exit_code)
