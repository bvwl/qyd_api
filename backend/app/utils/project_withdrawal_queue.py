"""
项目提现 Redis 队列处理器
支持高并发批量处理

使用独立的Redis数据库：
- 队列：DB 2
- 缓存：DB 3

注意：由于提现记录需要计算变动和历史，建议使用直接API调用而不是队列
队列适用于简单的批量创建/更新场景
"""
from app.utils.redis_queue import RedisQueueHandler
from app.models.project import ProjectWithdrawal
from app.core.settings import REDIS_QUEUE_BATCH_SIZE, REDIS_QUEUE_NUM_WORKERS
from typing import Dict, Any
from app.utils.logs import getLogger

logger = getLogger('app')


class ProjectWithdrawalQueue(RedisQueueHandler):
    """项目提现队列处理器"""
    
    def __init__(self):
        super().__init__(
            queue_name="project_withdrawal",
            model_class=ProjectWithdrawal,
            unique_fields=["project_id"],  # 使用 project_id 作为唯一标识
            batch_size=REDIS_QUEUE_BATCH_SIZE,
            num_workers=REDIS_QUEUE_NUM_WORKERS,
            queue_db=2,  # 使用 DB 2 作为队列数据库
            cache_db=3   # 使用 DB 3 作为缓存数据库
        )


# 创建全局实例
project_withdrawal_queue = ProjectWithdrawalQueue()
