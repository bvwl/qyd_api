"""
项目统计CRUD
"""
from datetime import datetime, timedelta, date
from typing import List, Dict
from uuid import UUID

from app.models.project import ProjectInfo
from app.models.stats import ProjectDailyStats
from app.core.database import db_read, db_write
from app.utils.stats_cache import stats_cache


class ProjectStatsCRUD:
    """项目统计CRUD"""
    
    async def upsert_daily_stats(
        self,
        project_id: UUID,
        date: date,
        update_count: int
    ) -> ProjectDailyStats:
        """
        创建或更新项目每日统计
        
        :param project_id: 项目ID
        :param date: 统计日期
        :param update_count: 更新数量
        :return: 统计记录
        """
        # 尝试获取现有记录（从主库读取，确保数据一致性）
        stats = await ProjectDailyStats.get_or_none(
            project_id=project_id,
            date=date
        )
        
        if stats:
            # 更新现有记录（写入主库）
            stats.update_count = update_count
            await stats.save()
        else:
            # 创建新记录（写入主库）
            stats = await ProjectDailyStats.create(
                project_id=project_id,
                date=date,
                update_count=update_count
            )
        
        # 清除相关缓存
        await stats_cache.clear_project_cache(str(project_id))
        
        return stats
    
    async def increment_daily_count(
        self,
        project_id: UUID,
        date: date | None = None
    ) -> int:
        """
        增加项目某天的更新数量（原子操作）
        
        :param project_id: 项目ID
        :param date: 统计日期，None表示今天
        :return: 增加后的数量
        """
        if date is None:
            date = datetime.now().date()
        
        # 尝试获取现有记录（从主库读取，确保数据一致性）
        stats = await ProjectDailyStats.get_or_none(
            project_id=project_id,
            date=date
        )
        
        if stats:
            # 更新现有记录（写入主库）
            stats.update_count += 1
            await stats.save()
            count = stats.update_count
        else:
            # 创建新记录（写入主库）
            stats = await ProjectDailyStats.create(
                project_id=project_id,
                date=date,
                update_count=1
            )
            count = 1
        
        # 同时更新Redis缓存（用于实时展示）
        await stats_cache.set_project_daily_stats(
            str(project_id),
            date.strftime('%Y-%m-%d'),
            count,
            expire=86400
        )
        
        return count
    """项目统计CRUD"""
    
    
    async def get_daily_stats_from_db(
        self,
        project_ids: List[str] | None = None,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> Dict[str, Dict[str, int]]:
        """
        从数据库获取项目每日统计数据（使用从库）
        
        :param project_ids: 项目ID列表，None表示所有项目
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: {project_id: {date: count}}
        """
        # 构建查询（使用从库）
        query = db_read(ProjectDailyStats)
        
        if project_ids:
            query = query.filter(project_id__in=project_ids)
        
        if start_date:
            query = query.filter(date__gte=start_date)
        
        if end_date:
            query = query.filter(date__lte=end_date)
        
        # 获取所有统计记录
        stats_list = await query.all()
        
        # 组织数据
        result: Dict[str, Dict[str, int]] = {}
        for stats in stats_list:
            project_id = str(stats.project_id)
            date_str = stats.date.strftime('%Y-%m-%d')
            
            if project_id not in result:
                result[project_id] = {}
            
            result[project_id][date_str] = stats.update_count
        
        return result
    
    async def get_daily_update_counts(
        self,
        project_ids: List[str] | None = None,
        days: int = 7
    ) -> Dict[str, Dict[str, int]]:
        """
        获取项目每日更新账号数量（从数据库读取）
        
        :param project_ids: 项目ID列表，None表示所有项目
        :param days: 查询最近N天的数据
        :return: {project_id: {date: count}}
        """
        # 计算日期范围
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 从数据库获取统计数据
        return await self.get_daily_stats_from_db(
            project_ids=project_ids,
            start_date=start_date,
            end_date=end_date
        )
    
    async def get_project_stats_time_series(
        self,
        project_ids: List[str] | None = None,
        days: int = 7,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        获取项目统计时间序列数据（用于曲线图）
        
        :param project_ids: 项目ID列表，None表示所有项目
        :param days: 查询最近N天的数据
        :param use_cache: 是否使用缓存
        :return: 项目统计时间序列列表
        """
        # 尝试从缓存获取
        if use_cache and project_ids:
            cached_data = await stats_cache.get_project_stats_time_series(project_ids, days)
            if cached_data:
                print(f"✅ 从缓存获取统计数据（{len(project_ids)}个项目，{days}天）")
                return cached_data
        
        # 获取每日统计数据
        daily_stats = await self.get_daily_update_counts(project_ids, days)
        
        # 获取项目信息（使用从库）
        if project_ids:
            projects = await db_read(ProjectInfo).filter(id__in=project_ids).all()
        else:
            projects = await db_read(ProjectInfo).all()
        
        # 生成日期列表
        end_date = datetime.now()
        dates = []
        for i in range(days):
            date = (end_date - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
            dates.append(date)
        
        # 构建时间序列数据
        result = []
        for project in projects:
            project_id = str(project.id)
            project_stats = daily_stats.get(project_id, {})
            
            # 填充每天的数据（没有数据的日期填0）
            counts = []
            for date in dates:
                count = project_stats.get(date, 0)
                counts.append(count)
            
            result.append({
                'project_id': project_id,
                'project_name': project.name,
                'dates': dates,
                'counts': counts
            })
        
        # 按项目名称排序
        result.sort(key=lambda x: x['project_name'])
        
        # 缓存结果（5分钟）
        if use_cache and project_ids:
            await stats_cache.set_project_stats_time_series(project_ids, days, result, expire=300)
        
        return result
    
    async def get_total_stats_time_series(
        self,
        project_ids: List[str] | None = None,
        days: int = 7,
        use_cache: bool = True
    ) -> List[Dict]:
        """
        获取所有项目的总和统计时间序列数据（用于仪表盘总览）
        
        :param project_ids: 项目ID列表，None表示所有项目
        :param days: 查询最近N天的数据
        :param use_cache: 是否使用缓存
        :return: 总和统计时间序列（单条数据）
        """
        # 构建缓存键
        cache_key = f"total_stats_{days}"
        if project_ids:
            cache_key = f"total_stats_{','.join(sorted(project_ids))}_{days}"
        
        # 尝试从缓存获取
        if use_cache:
            cached_data = await stats_cache.get_project_stats_time_series(
                [cache_key] if project_ids else None, 
                days
            )
            if cached_data:
                print(f"✅ 从缓存获取总和统计数据（{days}天）")
                return cached_data
        
        # 获取每日统计数据
        daily_stats = await self.get_daily_update_counts(project_ids, days)
        
        # 生成日期列表
        end_date = datetime.now()
        dates = []
        for i in range(days):
            date = (end_date - timedelta(days=days-1-i)).strftime('%Y-%m-%d')
            dates.append(date)
        
        # 计算每天的总和
        total_counts = []
        for date in dates:
            day_total = 0
            for project_id, project_stats in daily_stats.items():
                day_total += project_stats.get(date, 0)
            total_counts.append(day_total)
        
        # 构建结果
        result = [{
            'project_id': 'total',
            'project_name': '总计',
            'dates': dates,
            'counts': total_counts
        }]
        
        # 缓存结果（5分钟）
        if use_cache:
            await stats_cache.set_project_stats_time_series(
                [cache_key] if project_ids else None,
                days,
                result,
                expire=300
            )
        
        return result
    
    async def get_today_update_count(
        self,
        project_id: UUID
    ) -> int:
        """
        获取项目今天更新的账号数量（从数据库读取，使用从库）
        
        :param project_id: 项目ID
        :return: 更新数量
        """
        today = datetime.now().date()
        
        # 从数据库获取今天的统计记录（使用从库）
        stats = await db_read(ProjectDailyStats).get_or_none(
            project_id=project_id,
            date=today
        )
        
        return stats.update_count if stats else 0
    
    async def sync_stats_from_accounts(
        self,
        project_id: UUID | None = None,
        date: date | None = None
    ) -> int:
        """
        从账号表同步统计数据到统计表
        用于初始化或修复统计数据
        
        :param project_id: 项目ID，None表示所有项目
        :param date: 统计日期，None表示今天
        :return: 同步的记录数
        """
        from app.models.project import ProjectAccount
        
        if date is None:
            date = datetime.now().date()
        
        # 计算日期范围
        start_time = datetime.combine(date, datetime.min.time())
        end_time = datetime.combine(date, datetime.max.time())
        
        # 构建查询（使用从库）
        query = db_read(ProjectAccount).filter(
            update_time__gte=start_time,
            update_time__lte=end_time
        )
        
        if project_id:
            query = query.filter(project_id=project_id)
        
        # 获取所有更新的账号
        accounts = await query.all()
        
        # 统计每个项目的更新数量
        project_counts: Dict[UUID, int] = {}
        for account in accounts:
            if account.project_id not in project_counts:
                project_counts[account.project_id] = 0
            project_counts[account.project_id] += 1
        
        # 更新统计表
        synced_count = 0
        for pid, count in project_counts.items():
            await self.upsert_daily_stats(pid, date, count)
            synced_count += 1
        
        return synced_count


# 创建实例
project_stats_crud = ProjectStatsCRUD()
