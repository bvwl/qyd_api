#!/usr/bin/env python3
"""
添加 XUI 操作日志路由到数据库
"""
import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import aiomysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


async def apply_migration():
    """应用数据库迁移"""
    # 数据库配置
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', 3307)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'db': os.getenv('DB_NAME', 'qyd'),
        'charset': 'utf8mb4',
    }

    print(f"连接数据库: {db_config['host']}:{db_config['port']}/{db_config['db']}")

    # 连接数据库
    conn = await aiomysql.connect(**db_config)
    cursor = await conn.cursor()

    try:
        # 1. 查找 XUI 管理父路由 ID
        print("\n1. 查找 XUI 管理父路由...")
        await cursor.execute(
            "SELECT id, title FROM frontend_routes WHERE path = '/xui' AND parent_id IS NULL LIMIT 1"
        )
        xui_parent = await cursor.fetchone()
        
        if not xui_parent:
            print("❌ 未找到 XUI 管理父路由")
            return
        
        xui_parent_id = xui_parent[0]
        print(f"✅ 找到父路由: {xui_parent[1]} (ID: {xui_parent_id})")
        
        # 2. 检查是否已存在操作日志路由
        print("\n2. 检查操作日志路由是否已存在...")
        await cursor.execute("SELECT id, title FROM frontend_routes WHERE path = '/xui/log' LIMIT 1")
        existing = await cursor.fetchone()
        
        if existing:
            print(f"⚠️  操作日志路由已存在: {existing[1]} (ID: {existing[0]})")
            log_route_id = existing[0]
        else:
            # 3. 获取下一个排序值
            print("\n3. 计算排序值...")
            await cursor.execute(
                "SELECT COALESCE(MAX(sort), 0) + 1 FROM frontend_routes WHERE parent_id = %s",
                (xui_parent_id,)
            )
            next_sort = (await cursor.fetchone())[0]
            print(f"✅ 下一个排序值: {next_sort}")
            
            # 4. 插入操作日志路由
            print("\n4. 创建操作日志路由...")
            log_route_id = str(uuid4())
            
            await cursor.execute("""
                INSERT INTO frontend_routes (
                    id, name, path, component, title, icon, parent_id, sort, 
                    status, route_type, permission, create_time, update_time
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """, (
                log_route_id,
                'XuiOperationLog',
                '/xui/log',
                'views/Xui/XuiOperationLog',
                '操作日志',
                'FileTextOutlined',
                xui_parent_id,
                next_sort,
                1,  # status: 正常
                1,  # route_type: 菜单
                'xui:log:view'
            ))
            
            print(f"✅ 创建路由成功 (ID: {log_route_id})")
        
        # 5. 绑定到 ADMIN 角色
        print("\n5. 绑定到 ADMIN 角色...")
        await cursor.execute("SELECT id, name FROM user_roles WHERE code = 'ADMIN' LIMIT 1")
        admin_role = await cursor.fetchone()
        
        if admin_role:
            admin_role_id = admin_role[0]
            # 检查是否已绑定
            await cursor.execute(
                "SELECT 1 FROM role_route_rel WHERE userrole_id = %s AND frontend_routes_id = %s",
                (admin_role_id, log_route_id)
            )
            if not await cursor.fetchone():
                await cursor.execute(
                    "INSERT INTO role_route_rel (userrole_id, frontend_routes_id) VALUES (%s, %s)",
                    (admin_role_id, log_route_id)
                )
                print(f"✅ 已绑定到 ADMIN 角色")
            else:
                print(f"⚠️  ADMIN 角色已绑定此路由")
        
        # 6. 绑定到 GM 角色
        print("\n6. 绑定到 GM 角色...")
        await cursor.execute("SELECT id, name FROM user_roles WHERE code = 'GM' LIMIT 1")
        gm_role = await cursor.fetchone()
        
        if gm_role:
            gm_role_id = gm_role[0]
            # 检查是否已绑定
            await cursor.execute(
                "SELECT 1 FROM role_route_rel WHERE userrole_id = %s AND frontend_routes_id = %s",
                (gm_role_id, log_route_id)
            )
            if not await cursor.fetchone():
                await cursor.execute(
                    "INSERT INTO role_route_rel (userrole_id, frontend_routes_id) VALUES (%s, %s)",
                    (gm_role_id, log_route_id)
                )
                print(f"✅ 已绑定到 GM 角色")
            else:
                print(f"⚠️  GM 角色已绑定此路由")
        
        # 提交事务
        await conn.commit()
        
        # 7. 查询结果
        print("\n7. 查询结果...")
        await cursor.execute("""
            SELECT 
                fr.id,
                fr.name,
                fr.path,
                fr.title,
                fr.sort,
                fr.permission,
                COUNT(DISTINCT rr.userrole_id) as role_count
            FROM frontend_routes fr
            LEFT JOIN role_route_rel rr ON fr.id = rr.frontend_routes_id
            WHERE fr.path = '/xui/log'
            GROUP BY fr.id, fr.name, fr.path, fr.title, fr.sort, fr.permission
        """)
        
        result = await cursor.fetchone()
        if result:
            print("\n" + "=" * 80)
            print("✅ 迁移成功!")
            print("=" * 80)
            print(f"路由 ID: {result[0]}")
            print(f"路由名称: {result[1]}")
            print(f"路由路径: {result[2]}")
            print(f"菜单标题: {result[3]}")
            print(f"排序值: {result[4]}")
            print(f"权限标识: {result[5]}")
            print(f"绑定角色数: {result[6]}")
            print("=" * 80)
        
        # 8. 统计信息
        await cursor.execute("SELECT COUNT(*) FROM frontend_routes")
        total_routes = (await cursor.fetchone())[0]
        
        await cursor.execute(
            "SELECT COUNT(*) FROM frontend_routes WHERE parent_id = %s",
            (xui_parent_id,)
        )
        xui_routes = (await cursor.fetchone())[0]
        
        print(f"\n📊 统计信息:")
        print(f"   总路由数: {total_routes}")
        print(f"   XUI 子路由数: {xui_routes}")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        await conn.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        await cursor.close()
        conn.close()


if __name__ == '__main__':
    asyncio.run(apply_migration())
