#!/usr/bin/env python3
"""
测试项目统计功能
"""
import asyncio
import sys
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, '.')

from app.utils.stats_cache import stats_cache
from app.crud.project.stats import project_stats_crud
from tortoise import Tortoise
from app.core.settings import TORTOISE_ORM


async def test_stats_cache():
    """测试统计缓存"""
    print("=" * 60)
    print("测试统计缓存（Redis DB 10）")
    print("=" * 60)
    
    # 测试1: 设置和获取单个项目的每日统计
    print("\n测试1: 设置和获取单个项目的每日统计")
    project_id = "test-project-123"
    date = datetime.now().strftime('%Y-%m-%d')
    
    # 设置缓存
    success = await stats_cache.set_project_daily_stats(project_id, date, 100)
    print(f"设置缓存: {'成功' if success else '失败'}")
    
    # 获取缓存
    count = await stats_cache.get_project_daily_stats(project_id, date)
    print(f"获取缓存: {count}")
    
    # 测试2: 增加计数
    print("\n测试2: 增加计数")
    for i in range(5):
        count = await stats_cache.increment_project_daily_count(project_id, date)
        print(f"第{i+1}次增加后的计数: {count}")
    
    # 测试3: 清除缓存
    print("\n测试3: 清除项目缓存")
    success = await stats_cache.clear_project_cache(project_id)
    print(f"清除缓存: {'成功' if success else '失败'}")
    
    # 验证缓存已清除
    count = await stats_cache.get_project_daily_stats(project_id, date)
    print(f"清除后获取缓存: {count}")


async def test_stats_crud():
    """测试统计CRUD"""
    print("\n" + "=" * 60)
    print("测试统计CRUD")
    print("=" * 60)
    
    # 初始化数据库
    await Tortoise.init(config=TORTOISE_ORM)
    
    try:
        # 测试1: 获取所有项目的统计数据
        print("\n测试1: 获取所有项目的统计数据（最近7天）")
        stats = await project_stats_crud.get_project_stats_time_series(
            project_ids=None,
            days=7,
            use_cache=False  # 不使用缓存，直接查询数据库
        )
        
        print(f"找到 {len(stats)} 个项目")
        for project_stat in stats[:3]:  # 只显示前3个
            print(f"\n项目: {project_stat['project_name']}")
            print(f"  日期: {project_stat['dates']}")
            print(f"  数量: {project_stat['counts']}")
            print(f"  总计: {sum(project_stat['counts'])}")
        
        # 测试2: 使用缓存
        print("\n测试2: 使用缓存获取统计数据")
        if stats:
            project_ids = [s['project_id'] for s in stats[:3]]
            
            # 第一次查询（写入缓存）
            print("第一次查询（写入缓存）...")
            import time
            start = time.time()
            stats1 = await project_stats_crud.get_project_stats_time_series(
                project_ids=project_ids,
                days=7,
                use_cache=True
            )
            time1 = time.time() - start
            print(f"耗时: {time1:.3f}秒")
            
            # 第二次查询（从缓存读取）
            print("\n第二次查询（从缓存读取）...")
            start = time.time()
            stats2 = await project_stats_crud.get_project_stats_time_series(
                project_ids=project_ids,
                days=7,
                use_cache=True
            )
            time2 = time.time() - start
            print(f"耗时: {time2:.3f}秒")
            print(f"性能提升: {(time1/time2):.1f}x")
        
    finally:
        await Tortoise.close_connections()


async def main():
    """主函数"""
    try:
        # 测试缓存
        await test_stats_cache()
        
        # 测试CRUD
        await test_stats_crud()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 关闭Redis连接
        stats_cache.close()


if __name__ == '__main__':
    asyncio.run(main())
