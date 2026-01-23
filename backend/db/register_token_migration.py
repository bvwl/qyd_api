#!/usr/bin/env python3
"""
注册Token字段迁移到aerich
由于之前手动执行了数据库迁移，现在需要在aerich表中注册这个迁移
"""
import asyncio
import sys
import os
import json
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


async def register_migration():
    """注册迁移到aerich表"""
    print("=" * 60)
    print("注册Token字段迁移到aerich")
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
            # 1. 检查aerich表
            print("1. 检查aerich表:")
            print("-" * 60)
            await cursor.execute("SELECT version, app FROM aerich ORDER BY id")
            result = await cursor.fetchall()
            print(f"  当前已有 {len(result)} 条迁移记录:")
            for row in result:
                print(f"    - {row[1]}: {row[0]}")
            print()
            
            # 2. 检查迁移是否已存在
            migration_version = "1_20260123_token_text.py"
            await cursor.execute(
                "SELECT COUNT(*) FROM aerich WHERE version = %s AND app = 'models'",
                (migration_version,)
            )
            count = (await cursor.fetchone())[0]
            
            if count > 0:
                print(f"⚠️  迁移 {migration_version} 已存在，无需重复注册")
                print()
                conn.close()
                return 0
            
            # 3. 注册新迁移
            print("2. 注册新迁移:")
            print("-" * 60)
            
            # 迁移内容（与迁移文件一致）
            migration_content = {
                "upgrade": [
                    "ALTER TABLE `tokens` MODIFY COLUMN `token` TEXT NOT NULL COMMENT '访问令牌';"
                ]
            }
            
            sql = """
                INSERT INTO aerich (version, app, content)
                VALUES (%s, %s, %s)
            """
            
            print(f"  版本: {migration_version}")
            print(f"  应用: models")
            print(f"  内容: {json.dumps(migration_content, ensure_ascii=False)}")
            
            await cursor.execute(
                sql,
                (migration_version, "models", json.dumps(migration_content))
            )
            await conn.commit()
            print("✓ 迁移注册成功")
            print()
            
            # 4. 验证注册结果
            print("3. 验证注册结果:")
            print("-" * 60)
            await cursor.execute("SELECT version, app FROM aerich ORDER BY id")
            result = await cursor.fetchall()
            print(f"  现在共有 {len(result)} 条迁移记录:")
            for row in result:
                print(f"    - {row[1]}: {row[0]}")
            print()
        
        conn.close()
        
        print("=" * 60)
        print("✅ 迁移注册完成！")
        print("=" * 60)
        print()
        print("现在aerich已经知道这个迁移了，未来的迁移将正常工作")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n✗ 注册失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(register_migration())
    sys.exit(exit_code)
