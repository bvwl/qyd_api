"""
统计数据缓存工具（使用Redis 10号数据库）
"""
import json
import redis
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from app.core.settings import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_ENABLED


class StatsCache:
    """统计数据缓存类"""
    
    def __init__(self):
        """初始化Redis连接（使用10号数据库）"""
        self.enabled = REDIS_ENABLED
        self.redis_client: Optional[redis.Redis] = None
        self.key_prefix = "stats:"
        
        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    password=REDIS_PASSWORD if REDIS_PASSWORD else None,
                    db=10,  # 使用10号数据库
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                # 测试连接
                self.redis_client.ping()
                print("✅ 统计缓存Redis连接成功（DB 10）")
            except Exception as e:
                print(f"⚠️  统计缓存Redis连接失败: {e}")
                self.enabled = False
                self.redis_client = None
    
    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        return f"{self.key_prefix}{key}"
    
    async def get_project_daily_stats(
        self,
        project_id: str,
        date: str
    ) -> Optional[int]:
        """
        获取项目某天的更新数量缓存
        
        :param project_id: 项目ID
        :param date: 日期 YYYY-MM-DD
        :return: 更新数量，None表示缓存不存在
        """
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            key = self._make_key(f"project:{project_id}:daily:{date}")
            value = self.redis_client.get(key)
            return int(value) if value else None
        except Exception as e:
            print(f"获取缓存失败: {e}")
            return None
    
    async def set_project_daily_stats(
        self,
        project_id: str,
        date: str,
        count: int,
        expire: int = 86400  # 默认缓存24小时
    ) -> bool:
        """
        设置项目某天的更新数量缓存
        
        :param project_id: 项目ID
        :param date: 日期 YYYY-MM-DD
        :param count: 更新数量
        :param expire: 过期时间（秒）
        :return: 是否成功
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            key = self._make_key(f"project:{project_id}:daily:{date}")
            self.redis_client.setex(key, expire, count)
            return True
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False
    
    async def get_project_stats_time_series(
        self,
        project_ids: List[str] | None,
        days: int
    ) -> Optional[List[Dict]]:
        """
        获取项目统计时间序列缓存
        
        :param project_ids: 项目ID列表，None表示不使用缓存
        :param days: 天数
        :return: 时间序列数据，None表示缓存不存在
        """
        if not self.enabled or not self.redis_client:
            return None
        
        # 如果 project_ids 为 None 或空列表，不使用缓存
        if not project_ids:
            return None
        
        try:
            # 生成缓存键（使用项目ID列表的哈希值）
            project_ids_str = ",".join(sorted(project_ids))
            key = self._make_key(f"time_series:{hash(project_ids_str)}:days:{days}")
            value = self.redis_client.get(key)
            
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"获取时间序列缓存失败: {e}")
            return None
    
    async def set_project_stats_time_series(
        self,
        project_ids: List[str] | None,
        days: int,
        data: List[Dict],
        expire: int = 300  # 默认缓存5分钟
    ) -> bool:
        """
        设置项目统计时间序列缓存
        
        :param project_ids: 项目ID列表，None表示不使用缓存
        :param days: 天数
        :param data: 时间序列数据
        :param expire: 过期时间（秒）
        :return: 是否成功
        """
        if not self.enabled or not self.redis_client:
            return False
        
        # 如果 project_ids 为 None 或空列表，不使用缓存
        if not project_ids:
            return False
        
        try:
            # 生成缓存键
            project_ids_str = ",".join(sorted(project_ids))
            key = self._make_key(f"time_series:{hash(project_ids_str)}:days:{days}")
            self.redis_client.setex(key, expire, json.dumps(data))
            return True
        except Exception as e:
            print(f"设置时间序列缓存失败: {e}")
            return False
    
    async def increment_project_daily_count(
        self,
        project_id: str,
        date: str | None = None
    ) -> int:
        """
        增加项目某天的更新数量（用于实时统计）
        
        :param project_id: 项目ID
        :param date: 日期 YYYY-MM-DD，None表示今天
        :return: 增加后的数量
        """
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            key = self._make_key(f"project:{project_id}:daily:{date}")
            count = self.redis_client.incr(key)
            
            # 设置过期时间（7天后过期）
            self.redis_client.expire(key, 7 * 86400)
            
            return count
        except Exception as e:
            print(f"增加计数失败: {e}")
            return 0
    
    async def clear_project_cache(self, project_id: str) -> bool:
        """
        清除项目的所有缓存
        
        :param project_id: 项目ID
        :return: 是否成功
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            # 查找所有相关的键
            pattern = self._make_key(f"project:{project_id}:*")
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
            
            return True
        except Exception as e:
            print(f"清除缓存失败: {e}")
            return False
    
    async def clear_all_stats_cache(self) -> bool:
        """
        清除所有统计缓存
        
        :return: 是否成功
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            pattern = self._make_key("*")
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
                print(f"✅ 已清除 {len(keys)} 个统计缓存")
            
            return True
        except Exception as e:
            print(f"清除所有缓存失败: {e}")
            return False
    
    def close(self):
        """关闭Redis连接"""
        if self.redis_client:
            self.redis_client.close()


# 创建全局实例
stats_cache = StatsCache()
