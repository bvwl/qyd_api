"""
统计数据同步工具
用于定时同步账号更新数量到统计表
"""
import asyncio
from datetime import datetime, timedelta, date
from typing import Dict
from uuid import UUID

from app.models.project import ProjectAccount
from app.models.stats import ProjectDailyStats
from app.core.database import db_read, db_write
from app.crud.project.stats import project_stats_crud


async def sync_today_stats():
    """
    同步今天的统计数据
    从账号表统计今天更新的数量，写入统计表
    """
    print(f"开始同步今天的统计数据: {datetime.now()}")
    
    today = datetime.now().date()
    start_time = datetime.combine(today, datetime.min.time())
    end_time = datetime.combine(today, datetime.max.time())
    
    # 获取今天更新的所有账号（使用从库）
    accounts = await db_read(ProjectAccount).filter(
        update_time__gte=start_time,
        update_time__lte=end_time
    ).all()
    
    # 统计每个项目的更新数量
    project_counts: Dict[UUID, int] = {}
    for account in accounts:
        if account.project_id not in project_counts:
            project_counts[account.project_id] = 0
        project_counts[account.project_id] += 1
    
    # 更新统计表
    synced_count = 0
    for project_id, count in project_counts.items():
        await project_stats_crud.upsert_daily_stats(project_id, today, count)
        synced_count += 1
    
    print(f"✅ 同步完成: {synced_count} 个项目，共 {len(accounts)} 个账号更新")
    return synced_count


async def sync_historical_stats(days: int = 30):
    """
    同步历史统计数据
    用于初始化或修复统计数据
    
    :param days: 同步最近N天的数据
    """
    print(f"开始同步最近 {days} 天的统计数据...")
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    total_synced = 0
    
    # 逐天同步
    current_date = start_date
    while current_date <= end_date:
        print(f"\n同步 {current_date} 的数据...")
        
        start_time = datetime.combine(current_date, datetime.min.time())
        end_time = datetime.combine(current_date, datetime.max.time())
        
        # 获取当天更新的所有账号（使用从库）
        accounts = await db_read(ProjectAccount).filter(
            update_time__gte=start_time,
            update_time__lte=end_time
        ).all()
        
        # 统计每个项目的更新数量
        project_counts: Dict[UUID, int] = {}
        for account in accounts:
            if account.project_id not in project_counts:
                project_counts[account.project_id] = 0
            project_counts[account.project_id] += 1
        
        # 更新统计表
        for project_id, count in project_counts.items():
            await project_stats_crud.upsert_daily_stats(project_id, current_date, count)
            total_synced += 1
        
        print(f"  {current_date}: {len(project_counts)} 个项目，{len(accounts)} 个账号更新")
        
        current_date += timedelta(days=1)
    
    print(f"\n✅ 历史数据同步完成: 共同步 {total_synced} 条记录")
    return total_synced


async def cleanup_old_stats(keep_days: int = 90):
    """
    清理旧的统计数据
    
    :param keep_days: 保留最近N天的数据
    """
    print(f"开始清理 {keep_days} 天前的统计数据...")
    
    cutoff_date = datetime.now().date() - timedelta(days=keep_days)
    
    # 删除旧数据（写入主库）
    deleted_count = await db_write(ProjectDailyStats).filter(
        date__lt=cutoff_date
    ).delete()
    
    print(f"✅ 清理完成: 删除了 {deleted_count} 条旧记录")
    return deleted_count


# 定时任务函数（可以被APScheduler调用）
async def scheduled_sync_stats():
    """
    定时同步统计数据（每小时执行一次）
    """
    try:
        await sync_today_stats()
    except Exception as e:
        print(f"❌ 定时同步失败: {e}")
        import traceback
        traceback.print_exc()
