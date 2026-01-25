"""
检查 xui_operation_logs 表结构
"""
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', '3307'))
DB_USER = os.getenv('DB_USER', 'qyd')
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
    
    # 检查表是否存在
    cursor.execute("SHOW TABLES LIKE 'xui_operation_logs'")
    result = cursor.fetchall()
    
    if result:
        print('\n✓ 表存在,检查表结构:')
        print('-' * 80)
        cursor.execute('DESCRIBE xui_operation_logs')
        rows = cursor.fetchall()
        
        print(f'{"字段名":20} {"类型":20} {"NULL":5} {"Key":5} {"默认值":20}')
        print('-' * 80)
        for row in rows:
            print(f'{row[0]:20} {row[1]:20} {row[2]:5} {row[3]:5} {str(row[4] or ""):20}')
        print('-' * 80)
        
        # 检查是否有 status 字段
        has_status = any(row[0] == 'status' for row in rows)
        has_is_resolved = any(row[0] == 'is_resolved' for row in rows)
        
        print(f'\n字段检查:')
        print(f'  status 字段: {"存在 ❌ (需要删除)" if has_status else "不存在 ✓"}')
        print(f'  is_resolved 字段: {"存在 ✓" if has_is_resolved else "不存在 ❌ (需要添加)"}')
        
        if has_status:
            print('\n⚠️  发现旧的 status 字段,需要删除表并重新创建')
            print('\n执行以下命令修复:')
            print('  DROP TABLE xui_operation_logs;')
            print('  然后重新运行: python backend/db/apply_xui_operation_logs.py')
    else:
        print('\n✗ 表不存在,需要创建')
        print('\n执行以下命令创建:')
        print('  python backend/db/apply_xui_operation_logs.py')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'\n❌ 错误: {e}')
