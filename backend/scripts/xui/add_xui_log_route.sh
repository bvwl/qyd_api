#!/bin/bash

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 默认值
DB_HOST=${DB_HOST:-127.0.0.1}
DB_PORT=${DB_PORT:-3307}
DB_USER=${DB_USER:-root}
DB_NAME=${DB_NAME:-qyd}

echo "================================"
echo "添加 XUI 操作日志路由"
echo "================================"
echo "数据库: $DB_HOST:$DB_PORT/$DB_NAME"
echo "用户: $DB_USER"
echo ""

# 执行 SQL
python3 -c "
import asyncio
import aiomysql
import os

async def run():
    conn = await aiomysql.connect(
        host='$DB_HOST',
        port=int('$DB_PORT'),
        user='$DB_USER',
        password='$DB_PASSWORD',
        db='$DB_NAME',
        charset='utf8mb4'
    )
    cursor = await conn.cursor()
    
    try:
        # 读取 SQL 文件
        with open('db/add_xui_log_route.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割并执行每个语句
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for stmt in statements:
            if stmt:
                await cursor.execute(stmt)
        
        await conn.commit()
        
        # 查询结果
        await cursor.execute('''
            SELECT 
                fr.id,
                fr.name,
                fr.path,
                fr.title,
                fr.sort,
                fr.permission,
                COUNT(DISTINCT rr.role_id) as role_count
            FROM frontend_routes fr
            LEFT JOIN role_route_rel rr ON fr.id = rr.route_id
            WHERE fr.path = '/xui/log'
            GROUP BY fr.id, fr.name, fr.path, fr.title, fr.sort, fr.permission
        ''')
        
        result = await cursor.fetchone()
        if result:
            print('✅ 路由添加成功!')
            print(f'   ID: {result[0]}')
            print(f'   名称: {result[1]}')
            print(f'   路径: {result[2]}')
            print(f'   标题: {result[3]}')
            print(f'   排序: {result[4]}')
            print(f'   权限: {result[5]}')
            print(f'   绑定角色数: {result[6]}')
        else:
            print('⚠️  路由可能已存在')
        
    except Exception as e:
        print(f'❌ 执行失败: {e}')
        await conn.rollback()
    finally:
        await cursor.close()
        conn.close()

asyncio.run(run())
"

echo ""
echo "================================"
echo "完成!"
echo "================================"
