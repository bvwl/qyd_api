#!/usr/bin/env python3
"""
初始化项目统计功能
1. 创建数据库表
2. 同步历史数据
3. 测试功能
"""
import asyncio
import sys

sys.path.insert(0, '.')

from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM
from app.utils.stats_sync import sync_historical_stats, sync_today_stats
from app.crud.project.stats import project_stats_crud


async def main():
    """主函数"""
    print("=" * 60)
    print("初始化项目统计功能")
    print("=" * 60)
    
    # 初始化数据库
    await Tortoise.init(config=TORTOISE_ORM)
    
    try:
        # 步骤1: 创建数据库表
        print("\n步骤1: 创建数据库表")
        print("-" * 60)
        
        conn = Tortoise.get_connection("default")
        
        # 读取SQL文件
        import os
        sql_file = os.path.join('db', 'create_project_daily_stats.sql')
        
        if os.path.exists(sql_file):
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            await conn.execute_script(sql)
            print("✅ 数据库表创建成功")
        else:
            print("⚠️  SQL文件不存在，跳过表创建")
        
        # 验证表是否存在
        result = await conn.execute_query(
            "SELECT COUNT(*) as count FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = 'project_daily_stats'"
        )
        
        if result[1][0]['count'] == 0:
            print("❌ 表不存在，请手动执行SQL文件")
            return
        
        print("✅ 表验证成功")
        
        # 步骤2: 同步历史数据
        print("\n步骤2: 同步历史数据（最近30天）")
        print("-" * 60)
        
        synced_count = await sync_historical_stats(days=30)
        print(f"✅ 历史数据同步完成: {synced_count} 条记录")
        
        # 步骤3: 测试查询
        print("\n步骤3: 测试查询功能")
        print("-" * 60)
        
        # 获取统计数据
        stats = await project_stats_crud.get_project_stats_time_series(
            project_ids=None,
            days=7,
            use_cache=False
        )
        
        print(f"✅ 查询成功: 找到 {len(stats)} 个项目的统计数据")
        
        # 显示前3个项目的数据
        for i, project_stat in enumerate(stats[:3], 1):
            print(f"\n项目 {i}: {project_stat['project_name']}")
            print(f"  最近7天总更新: {sum(project_stat['counts'])} 个账号")
            print(f"  日期: {project_stat['dates']}")
            print(f"  数量: {project_stat['counts']}")
        
        # 步骤4: 测试今天的统计
        print("\n步骤4: 测试今天的统计")
        print("-" * 60)
        
        if stats:
            project_id = stats[0]['project_id']
            project_name = stats[0]['project_name']
            
            from uuid import UUID
            count = await project_stats_crud.get_today_update_count(UUID(project_id))
            print(f"✅ 项目 {project_name} 今天更新了 {count} 个账号")
        
        print("\n" + "=" * 60)
        print("✅ 初始化完成！")
        print("=" * 60)
        print("\n后续步骤:")
        print("1. 启动后端服务: python backend/start.py")
        print("2. 测试API: bash backend/test_stats_api.sh")
        print("3. 前端集成: 参考 PROJECT_STATS_DASHBOARD.md")
        
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(main())
