"""
为 proxy_account 表添加 is_all_inbound_added 字段
"""
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3307'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'qyd')

print(f'连接数据库: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

try:
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    
    cursor = conn.cursor()
    
    # 检查字段是否已存在
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = 'proxy_account' 
        AND COLUMN_NAME = 'is_all_inbound_added'
    """, (DB_NAME,))
    
    exists = cursor.fetchone()[0]
    
    if exists:
        print('✓ 字段 is_all_inbound_added 已存在,无需添加')
    else:
        print('添加字段 is_all_inbound_added...')
        
        # 读取 SQL 文件
        with open('backend/db/add_is_all_inbound_added_field.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # 执行 SQL
        cursor.execute(sql)
        conn.commit()
        
        print('✓ 字段添加成功')
        
        # 验证
        cursor.execute('DESCRIBE proxy_account')
        rows = cursor.fetchall()
        
        print('\n当前表结构:')
        print('-' * 80)
        for row in rows:
            if row[0] == 'is_all_inbound_added':
                print(f'✓ {row[0]:30} {row[1]:20} {row[2]:5} {row[3]:5}')
        print('-' * 80)
    
    cursor.close()
    conn.close()
    
    print('\n✅ 迁移完成')
    
except Exception as e:
    print(f'\n❌ 错误: {e}')
    import traceback
    traceback.print_exc()
