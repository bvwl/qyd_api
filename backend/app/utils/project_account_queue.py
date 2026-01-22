"""
项目账号Redis队列处理器
"""
from app.utils.redis_queue import RedisQueueHandler
from app.models.project import ProjectAccount
from app.core.settings import REDIS_QUEUE_BATCH_SIZE, REDIS_QUEUE_NUM_WORKERS


class ProjectAccountQueue(RedisQueueHandler):
    """项目账号队列处理器"""
    
    def __init__(self):
        super().__init__(
            queue_name="project_account",
            model_class=ProjectAccount,
            unique_fields=["account", "project_id"],  # 使用account和project_id作为唯一标识
            batch_size=REDIS_QUEUE_BATCH_SIZE,  # 从配置读取批量大小
            num_workers=REDIS_QUEUE_NUM_WORKERS  # 从配置读取工作线程数
        )


# 创建全局实例
project_account_queue = ProjectAccountQueue()
