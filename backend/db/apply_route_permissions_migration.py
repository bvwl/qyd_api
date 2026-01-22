"""
应用路由权限字段迁移
"""
import asyncio
import aiomysql
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

async def apply_migration():
    """
    应用数据库迁移
    """
    print("=" * 60)
    print("应用路由权限字段迁移")
    print("=" * 60)
    print()
    
    # 数据库配置
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', 3307)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'zhiyu666'),
        'db': os.getenv('DB_NAME', 'qyd'),
    }
    
    print(f"连接数据库: {db_config['host']}:{db_config['port']}/{db_config['db']}")
    print()
    
    try:
        # 连接数据库
        conn = await aiomysql.connect(**db_config)
        cursor = await conn.cursor()
        
        # 检查字段是否已存在
        await cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'frontend_routes' 
            AND COLUMN_NAME IN ('route_type', 'permission', 'api_method', 'api_path')
        """, (db_config['db'],))
        
        existing_columns = [row[0] for row in await cursor.fetchall()]
        
        if len(existing_columns) == 4:
            print("✓ 字段已存在，无需迁移")
            await cursor.close()
            conn.close()
            return
        
        print("开始添加字段...")
        
        # 添加 route_type 字段
        if 'route_type' not in existing_columns:
            await cursor.execute("""
                ALTER TABLE frontend_routes 
                ADD COLUMN route_type SMALLINT NOT NULL DEFAULT 1 
                COMMENT '路由类型(1:菜单,2:按钮,3:接口)' 
                AFTER status
            """)
            print("  ✓ 添加 route_type 字段")
        
        # 添加 permission 字段
        if 'permission' not in existing_columns:
            await cursor.execute("""
                ALTER TABLE frontend_routes 
                ADD COLUMN permission VARCHAR(128) NULL 
                COMMENT '权限标识（如：user:create, user:edit）' 
                AFTER route_type
            """)
            print("  ✓ 添加 permission 字段")
        
        # 添加 api_method 字段
        if 'api_method' not in existing_columns:
            await cursor.execute("""
                ALTER TABLE frontend_routes 
                ADD COLUMN api_method VARCHAR(16) NULL 
                COMMENT 'API方法(GET/POST/PUT/DELETE)' 
                AFTER permission
            """)
            print("  ✓ 添加 api_method 字段")
        
        # 添加 api_path 字段
        if 'api_path' not in existing_columns:
            await cursor.execute("""
                ALTER TABLE frontend_routes 
                ADD COLUMN api_path VARCHAR(255) NULL 
                COMMENT 'API路径' 
                AFTER api_method
            """)
            print("  ✓ 添加 api_path 字段")
        
        await conn.commit()
        print()
        
        # 添加索引
        print("添加索引...")
        try:
            await cursor.execute("""
                CREATE INDEX idx_permission ON frontend_routes(permission)
            """)
            print("  ✓ 添加 permission 索引")
        except aiomysql.Error as e:
            if e.args[0] == 1061:  # 索引已存在
                print("  - permission 索引已存在")
            else:
                raise
        
        try:
            await cursor.execute("""
                CREATE INDEX idx_route_type ON frontend_routes(route_type)
            """)
            print("  ✓ 添加 route_type 索引")
        except aiomysql.Error as e:
            if e.args[0] == 1061:  # 索引已存在
                print("  - route_type 索引已存在")
            else:
                raise
        
        await conn.commit()
        print()
        
        # 显示表结构
        print("当前表结构:")
        print("-" * 60)
        await cursor.execute("DESCRIBE frontend_routes")
        rows = await cursor.fetchall()
        for row in rows:
            print(f"  {row[0]:<20} {row[1]:<20} {row[2]:<5} {row[3]:<5}")
        
        await cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("✓ 迁移完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(apply_migration())
