"""
应用 XUI 表创建脚本（使用 aiomysql 直接连接）
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
    print("")
    sys.exit(1)


async def apply_xui_tables():
    """应用 XUI 表创建脚本"""
    print("=" * 60)
    print("  应用 XUI 表创建脚本")
    print("=" * 60)
    print()
    
    # 读取 .env 文件
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        print("📄 加载 .env 文件...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ .env 加载成功")
    else:
        print("⚠️  .env 文件不存在，使用默认配置")
    print()
    
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
    
    # 读取 SQL 文件
    sql_file = Path(__file__).parent / 'create_xui_tables.sql'
    
    if not sql_file.exists():
        print(f"❌ SQL 文件不存在: {sql_file}")
        return False
    
    print(f"📄 读取 SQL 文件: {sql_file.name}")
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割 SQL 语句
    sql_statements = []
    for statement in sql_content.split(';'):
        statement = statement.strip()
        # 跳过空语句
        if not statement:
            continue
        
        # 跳过纯注释（只有注释没有 SQL）
        lines = [line.strip() for line in statement.split('\n') if line.strip()]
        has_sql = any(not line.startswith('--') for line in lines)
        
        # 只保留包含 CREATE TABLE 的语句
        if has_sql and 'CREATE TABLE' in statement.upper():
            sql_statements.append(statement)
    
    print(f"📊 共 {len(sql_statements)} 条 SQL 语句")
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
            charset='utf8mb4',
            autocommit=True
        )
        print("✅ 数据库连接成功")
        print()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print()
        print("请检查:")
        print("  1. 数据库服务是否启动")
        print("  2. .env 配置是否正确")
        print("  3. 用户名密码是否正确")
        return False
    
    try:
        cursor = await conn.cursor()
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(sql_statements, 1):
            try:
                # 提取表名（用于显示）
                table_name = None
                if 'CREATE TABLE' in statement.upper():
                    parts = statement.upper().split('CREATE TABLE')
                    if len(parts) > 1:
                        table_part = parts[1].split('(')[0].strip()
                        table_name = table_part.replace('IF NOT EXISTS', '').replace('`', '').strip()
                
                if table_name:
                    print(f"⏳ [{i}/{len(sql_statements)}] 创建表: {table_name}...", end=' ', flush=True)
                else:
                    print(f"⏳ [{i}/{len(sql_statements)}] 执行 SQL...", end=' ', flush=True)
                
                # 执行 SQL
                await cursor.execute(statement)
                
                print("✅")
                success_count += 1
                
            except Exception as e:
                error_msg = str(e)
                
                # 如果是表已存在的错误，不算错误
                if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
                    print("⚠️  (已存在)")
                    success_count += 1
                else:
                    print(f"❌")
                    print(f"   错误: {error_msg}")
                    error_count += 1
        
        await cursor.close()
        
        print()
        print("=" * 60)
        print(f"  执行完成: 成功 {success_count} 条, 失败 {error_count} 条")
        print("=" * 60)
        print()
        
        if error_count == 0:
            print("✅ 所有表创建成功！")
            print()
            
            # 验证表
            print("📊 验证表是否创建:")
            cursor = await conn.cursor()
            await cursor.execute("SHOW TABLES LIKE 'xui%'")
            tables = await cursor.fetchall()
            await cursor.close()
            
            if tables:
                for table in tables:
                    print(f"   ✅ {table[0]}")
            else:
                print("   ⚠️  未找到 xui 相关表")
            
            print()
            print("下一步:")
            print("  1. 测试功能: python test_xui_migration.py")
            print("  2. 启动服务: python start.py")
            print("  3. 访问文档: http://localhost:6080/docs")
            print()
            return True
        else:
            print(f"⚠️  有 {error_count} 条语句执行失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()
        print("🔌 数据库连接已关闭")


if __name__ == "__main__":
    result = asyncio.run(apply_xui_tables())
    sys.exit(0 if result else 1)
