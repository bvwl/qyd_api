"""
项目账号Redis队列处理器
"""
from app.utils.redis_queue import RedisQueueHandler
from app.models.project import ProjectAccount, ProjectInfo
from app.core.settings import REDIS_QUEUE_BATCH_SIZE, REDIS_QUEUE_NUM_WORKERS
from app.utils.project_crypto import encrypt_sensitive_fields
from typing import Dict, Any
from app.utils.logs import getLogger

logger = getLogger('app')


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
    
    async def add_to_queue(self, data: Dict[str, Any], retry: int = 3) -> bool:
        """
        添加数据到队列（重写以支持加密）
        
        Args:
            data: 要添加的数据字典
            retry: 重试次数
            
        Returns:
            bool: 是否成功添加
        """
        # 如果有 data 字段且包含敏感信息，需要加密
        if 'data' in data and data['data'] and 'account' in data:
            try:
                account = data['account']
                # 加密 data 字段中的敏感字段
                data['data'] = encrypt_sensitive_fields(data['data'], account)
                logger.debug(f"队列数据已加密 [account={account}]")
            except Exception as e:
                logger.error(f"加密队列数据失败: {e}")
                # 加密失败，仍然继续处理（数据可能已经是加密的）
        
        # 如果有 password 字段，需要加密
        if 'password' in data and data['password'] and 'account' in data:
            try:
                from app.utils.project_crypto import encrypt_password
                account = data['account']
                data['password'] = encrypt_password(data['password'], account)
                logger.debug(f"密码已加密 [account={account}]")
            except Exception as e:
                logger.error(f"加密密码失败: {e}")
        
        # 调用父类方法添加到队列
        return await super().add_to_queue(data, retry)


# 创建全局实例
project_account_queue = ProjectAccountQueue()

