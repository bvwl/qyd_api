"""
检查 XUI 表是否存在
"""
import os
import sys
import asyncio
from pathlib import Path

try:
    import aiomysql
except ImportError:
    print("❌ 缺少 aiomysql 库")
    print("   安装命令: pip install aiomysql")
    sys.exit(1)


async def check_tables():
    """检查表是否存在"""
    print("=" * 60)
    print("  检查 XUI 表")
    print("=" * 60)
    print()
    
    # 读取 .env 文件
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        print("📄 加载 .env 文件...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # 获取数据库配置
    db_host = os.getenv('DB_HOST', '127.0.0.1')
    db_port = int(os.getenv('DB_PORT', '3306'))
    db_user = os.getenv('DB_USER', 'qyd')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'qyd')
    
    print(f"📊 数据库配置:")
    print(f"   Host: {db_host}:{db_port}")
    print(f"   User: {db_user}")
    print(f"   Database: {db_name}")
    print()
    
    # 连接数据库
    print("🔌 连接数据库...")
    try:
        conn = await aiomysql.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            db=db_name,
            charset='utf8mb4'
        )
        print("✅ 数据库连接成功")
        print()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return
    
    try:
        cursor = await conn.cursor()
        
        # 查看所有表
        print("📊 查看所有表:")
        await cursor.execute("SHOW TABLES")
        all_tables = await cursor.fetchall()
        print(f"   共 {len(all_tables)} 个表")
        for table in all_tables:
            print(f"   - {table[0]}")
        print()
        
        # 查看 xui 相关的表
        print("🔍 查找 XUI 相关的表:")
        await cursor.execute("SHOW TABLES LIKE 'xui%'")
        xui_tables = await cursor.fetchall()
        
        if xui_tables:
            print(f"   找到 {len(xui_tables)} 个 XUI 表:")
            for table in xui_tables:
                print(f"   ✅ {table[0]}")
                
                # 查看表结构
                await cursor.execute(f"DESC {table[0]}")
                columns = await cursor.fetchall()
                print(f"      字段数: {len(columns)}")
        else:
            print("   ❌ 未找到 XUI 相关的表")
            print()
            print("   可能的原因:")
            print("   1. SQL 执行失败但没有报错")
            print("   2. 连接到了错误的数据库")
            print("   3. 表创建在其他数据库中")
        
        print()
        
        # 检查是否有创建表的权限
        print("🔐 检查权限:")
        try:
            await cursor.execute("SHOW GRANTS")
            grants = await cursor.fetchall()
            print("   当前用户权限:")
            for grant in grants:
                print(f"   - {grant[0]}")
        except Exception as e:
            print(f"   ⚠️  无法查看权限: {e}")
        
        await cursor.close()
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print()
        print("🔌 数据库连接已关闭")


if __name__ == "__main__":
    asyncio.run(check_tables())
