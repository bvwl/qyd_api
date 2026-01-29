"""
Redis队列处理工具
用于批量处理数据，避免数据库压力和接口长时间占用
"""
import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from redis.asyncio import Redis, ConnectionPool
from tortoise.transactions import in_transaction
from tortoise.expressions import Q

from app.core.settings import (
    REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB,
    REDIS_MAX_CONNECTIONS, REDIS_TIMEOUT, REDIS_KEY_PREFIX, REDIS_ENABLED
)
from app.utils.logs import getLogger

# 使用自定义日志记录器
logger = getLogger('app')


class RedisQueueHandler:
    """Redis队列处理基类"""
    
    def __init__(
        self,
        queue_name: str,
        model_class,
        unique_fields: List[str],
        batch_size: int = 200,
        num_workers: int = 4,
        queue_db: int = 0,  # 队列使用的Redis数据库编号
        cache_db: int = 1   # 缓存使用的Redis数据库编号
    ):
        """
        初始化Redis队列处理器
        
        Args:
            queue_name: 队列名称（用于区分不同的队列）
            model_class: Tortoise ORM模型类
            unique_fields: 唯一标识字段列表（用于生成key和查询）
            batch_size: 每批处理的数量
            num_workers: 工作线程数量
            queue_db: 队列使用的Redis数据库编号（默认0）
            cache_db: 缓存使用的Redis数据库编号（默认1）
        """
        self._redis = None  # 队列 Redis
        self._redis_cache = None  # 缓存 Redis
        self._pool = None
        self._cache_pool = None
        
        # 队列配置
        self.queue_name = queue_name
        self.model_class = model_class
        self.unique_fields = unique_fields
        self.queue_db = queue_db  # 队列数据库编号
        self.cache_db = cache_db  # 缓存数据库编号
        
        # Redis key配置
        self.task_key_prefix = f"{REDIS_KEY_PREFIX}{queue_name}_item_"
        self.task_key_zset = f"{REDIS_KEY_PREFIX}{queue_name}_keys_zset"
        self.cache_key_prefix = f"{REDIS_KEY_PREFIX}{queue_name}_cache_"
        
        # 批处理配置
        self.batch_size = batch_size
        self.num_workers = num_workers
        
        # 休眠时间配置
        self.empty_sleep = 0.5  # 队列为空时的休眠时间
        self.fail_sleep = 1  # 处理失败时的休眠时间
        self.success_sleep = 0.05  # 处理成功时的休眠时间
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 0.5
        
        # 数据过期时间
        self.data_expire_seconds = 86400  # 1天
        self.cache_expire_seconds = 3600  # 缓存1小时
        
        # 工作线程列表
        self._workers = []
        self._running = False
    
    async def init_redis(self):
        """初始化Redis连接（使用自定义的队列DB和缓存DB）"""
        if not REDIS_ENABLED:
            logger.warning("Redis未启用，队列功能将不可用")
            return
        
        # 初始化队列连接池
        if not self._pool:
            try:
                redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{self.queue_db}"
                if REDIS_PASSWORD:
                    redis_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{self.queue_db}"
                
                self._pool = ConnectionPool.from_url(
                    redis_url,
                    max_connections=REDIS_MAX_CONNECTIONS,
                    socket_timeout=REDIS_TIMEOUT,
                    socket_connect_timeout=REDIS_TIMEOUT,
                    encoding='utf-8',
                    decode_responses=True,
                    retry_on_timeout=True
                )
                logger.info(f"Redis队列连接池初始化成功 (DB {self.queue_db}) [{self.queue_name}]")
            except Exception as e:
                logger.error(f"Redis队列连接池初始化失败 [{self.queue_name}]: {e}")
                raise
        
        # 初始化缓存连接池
        if not self._cache_pool:
            try:
                cache_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{self.cache_db}"
                if REDIS_PASSWORD:
                    cache_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{self.cache_db}"
                
                self._cache_pool = ConnectionPool.from_url(
                    cache_url,
                    max_connections=REDIS_MAX_CONNECTIONS,
                    socket_timeout=REDIS_TIMEOUT,
                    socket_connect_timeout=REDIS_TIMEOUT,
                    encoding='utf-8',
                    decode_responses=True,
                    retry_on_timeout=True
                )
                logger.info(f"Redis缓存连接池初始化成功 (DB {self.cache_db}) [{self.queue_name}]")
            except Exception as e:
                logger.error(f"Redis缓存连接池初始化失败 [{self.queue_name}]: {e}")
                raise
        
        self._redis = Redis(connection_pool=self._pool)
        self._redis_cache = Redis(connection_pool=self._cache_pool)
    
    async def get_redis(self) -> Redis:
        """获取队列Redis连接"""
        if not self._redis:
            await self.init_redis()
        return self._redis
    
    async def get_redis_cache(self) -> Redis:
        """获取缓存Redis连接"""
        if not self._redis_cache:
            await self.init_redis()
        return self._redis_cache
    
    async def close(self):
        """关闭Redis连接"""
        if self._redis:
            await self._redis.close()
            logger.info(f"Redis队列连接已关闭 [{self.queue_name}]")
        if self._redis_cache:
            await self._redis_cache.close()
            logger.info(f"Redis缓存连接已关闭 [{self.queue_name}]")
    
    def _generate_task_key(self, data: Dict[str, Any]) -> str:
        """根据唯一字段生成任务key"""
        key_parts = [str(data.get(field, '')) for field in self.unique_fields]
        key_suffix = '_'.join(key_parts)
        return f"{self.task_key_prefix}{key_suffix}"
    
    async def add_to_queue(self, data: Dict[str, Any], retry: int = 3) -> bool:
        """
        添加数据到队列
        
        Args:
            data: 要添加的数据字典
            retry: 重试次数
            
        Returns:
            bool: 是否成功添加
        """
        if not REDIS_ENABLED:
            logger.warning("Redis未启用，直接返回失败")
            return False
        
        redis = await self.get_redis()
        
        # 检查必要字段
        if not all(field in data for field in self.unique_fields):
            logger.error(f"数据缺少必要字段 [{self.queue_name}]: {data}")
            return False
        
        # 生成唯一key
        task_key = self._generate_task_key(data)
        current_time = time.time()
        
        for attempt in range(retry):
            try:
                async with redis.pipeline() as pipe:
                    # 存储数据
                    await pipe.set(task_key, json.dumps(data, ensure_ascii=False))
                    await pipe.expire(task_key, self.data_expire_seconds)
                    # 添加到有序集合
                    await pipe.zadd(self.task_key_zset, {task_key: current_time})
                    await pipe.expire(self.task_key_zset, self.data_expire_seconds * 2)
                    await pipe.execute()
                
                logger.debug(f"数据已添加到队列 [{self.queue_name}]: {task_key}")
                return True
            except Exception as e:
                logger.warning(f"[重试{attempt + 1}] Redis写入失败 [{self.queue_name}]: {e}")
                await asyncio.sleep(1 + attempt)
        
        logger.error(f"最终写入失败 [{self.queue_name}]: {data}")
        return False
    
    async def get_queue_size(self) -> int:
        """获取队列大小"""
        if not REDIS_ENABLED:
            return 0
        
        try:
            redis = await self.get_redis()
            return await redis.zcard(self.task_key_zset)
        except Exception as e:
            logger.error(f"获取队列大小失败 [{self.queue_name}]: {e}")
            return 0
    
    async def _build_query_conditions(self, items: List[Dict]) -> List[Q]:
        """构建查询条件"""
        conditions = []
        for item in items:
            condition_dict = {field: item[field] for field in self.unique_fields}
            conditions.append(Q(**condition_dict))
        return conditions
    
    async def _process_batch(self, worker_id: int) -> bool:
        """
        处理一批数据
        
        Args:
            worker_id: 工作线程ID
            
        Returns:
            bool: 是否处理成功
        """
        redis = await self.get_redis()
        
        try:
            # 原子性地获取并移除任务
            task_keys_with_scores = await redis.zpopmin(
                self.task_key_zset, 
                count=self.batch_size
            )
            
            if not task_keys_with_scores:
                return True
            
            task_keys = [key for key, _ in task_keys_with_scores]
            
            # 批量获取数据
            items = []
            keys_to_process = []
            
            async with redis.pipeline() as pipe:
                for key in task_keys:
                    pipe.get(key)
                results = await pipe.execute()
            
            # 解析数据
            for i, result in enumerate(results):
                if not result:
                    continue
                try:
                    item = json.loads(result)
                    items.append(item)
                    keys_to_process.append(task_keys[i])
                except json.JSONDecodeError:
                    logger.warning(f"[Worker-{worker_id}] 无效数据格式 [{self.queue_name}]: {result}")
                    await redis.delete(task_keys[i])
                    continue
            
            if not items:
                return True
            
            # 处理数据
            try:
                # 1. 构建查询条件
                query_conditions = []
                for item in items:
                    condition_dict = {field: item[field] for field in self.unique_fields}
                    query_conditions.append(Q(**condition_dict))
                
                # 2. 使用从库批量查询现有记录
                from app.core.settings import get_read_db
                from tortoise import Tortoise
                read_db = get_read_db()
                
                existing_records = {}
                if query_conditions:
                    # 分批查询
                    batch_size = 50
                    for i in range(0, len(query_conditions), batch_size):
                        batch_conditions = query_conditions[i:i + batch_size]
                        if batch_conditions:
                            combined_query = Q(*batch_conditions, join_type="OR")
                            # 使用从库查询 - 直接指定connection
                            batch_records = await self.model_class.filter(combined_query).using_db(Tortoise.get_connection(read_db))
                            for record in batch_records:
                                # 使用唯一字段组合作为key（转为字符串确保类型一致）
                                key = tuple(str(getattr(record, field)) for field in self.unique_fields)
                                existing_records[key] = record
                
                # 3. 准备批量更新和创建
                updates = []
                creates = []
                cache_items = []  # 需要缓存的记录
                
                for item in items:
                    # 过滤掉None值，避免违反非空约束
                    # 同时排除 variable 和 balance_history，这两个字段由 balance 自动计算
                    filtered_item = {
                        k: v for k, v in item.items() 
                        if v is not None and k not in ['variable', 'balance_history']
                    }
                    
                    # 构建key时确保类型一致（都转为字符串）
                    key = tuple(str(item[field]) for field in self.unique_fields)
                    
                    # 调试日志
                    logger.debug(f"[Worker-{worker_id}] 处理数据 key={key}, existing_keys={list(existing_records.keys())}")
                    
                    if key in existing_records:
                        # 更新现有记录 - 只更新非空字段
                        record = existing_records[key]
                        has_update = False
                        
                        # 检查是否传入了 balance
                        has_balance = 'balance' in filtered_item
                        
                        for field, value in filtered_item.items():
                            # 跳过唯一字段
                            if field not in self.unique_fields:
                                setattr(record, field, value)
                                has_update = True
                        
                        # 如果传入了 balance，需要计算 variable 和 balance_history
                        if has_balance:
                            from datetime import datetime
                            from decimal import Decimal
                            
                            new_balance = Decimal(str(filtered_item['balance']))
                            today = datetime.now().strftime('%Y-%m-%d')
                            
                            # 初始化 balance_history
                            if record.balance_history is None:
                                record.balance_history = {}
                            
                            # 实时更新当天的余额记录（覆盖，保留6位小数）
                            record.balance_history[today] = float(new_balance.quantize(Decimal('0.000001')))
                            
                            # 按日期排序并保留最近7条记录
                            sorted_data = dict(sorted(record.balance_history.items(), key=lambda x: x[0], reverse=True))
                            record.balance_history = dict(list(sorted_data.items())[:7])
                            
                            # 实时计算变动余额：当前余额 - 昨天的余额
                            if len(record.balance_history) >= 2:
                                dates = list(record.balance_history.keys())
                                today_balance = Decimal(str(record.balance_history[dates[0]]))  # 今天的余额（最新）
                                yesterday_balance = Decimal(str(record.balance_history[dates[1]]))  # 昨天的余额
                                record.variable = (today_balance - yesterday_balance).quantize(Decimal('0.01'))
                            else:
                                # 只有今天的记录，variable 等于 balance（从0增加到balance）
                                record.variable = new_balance.quantize(Decimal('0.01'))
                            
                            has_update = True
                        
                        # 只有在有实际更新时才添加到更新列表
                        if has_update:
                            updates.append(record)
                        cache_items.append((key, "update"))
                    else:
                        # 创建新记录 - 使用过滤后的数据
                        # 如果传入了 balance，需要初始化 variable 和 balance_history
                        if 'balance' in filtered_item:
                            from datetime import datetime
                            from decimal import Decimal
                            
                            new_balance = Decimal(str(filtered_item['balance']))
                            today = datetime.now().strftime('%Y-%m-%d')
                            
                            # 初始化 balance_history（记录当天的余额，保留6位小数）
                            filtered_item['balance_history'] = {today: float(new_balance.quantize(Decimal('0.000001')))}
                            # 创建时变动余额等于当前余额（从0增加到balance）
                            filtered_item['variable'] = new_balance.quantize(Decimal('0.01'))
                        
                        creates.append(self.model_class(**filtered_item))
                        cache_items.append((key, "create"))
                
                # 4. 批量执行数据库操作（使用主库，在事务中）
                async with in_transaction(connection_name="default"):
                    if updates:
                        # 获取模型的所有字段名（排除唯一字段和自动字段）
                        model_fields = set(self.model_class._meta.fields_map.keys())
                        # 从第一个item获取实际要更新的字段，并确保它们存在于模型中
                        update_fields = [
                            field for field in items[0].keys() 
                            if field not in self.unique_fields 
                            and field in model_fields
                            and field not in ['id', 'create_time', 'update_time']  # 排除自动管理的字段
                        ]
                        
                        logger.debug(f"[Worker-{worker_id}] 批量更新字段: {update_fields}")
                        
                        # 分批更新
                        batch_size = 50
                        for i in range(0, len(updates), batch_size):
                            batch_updates = updates[i:i + batch_size]
                            if batch_updates:
                                await self.model_class.bulk_update(
                                    batch_updates, 
                                    fields=update_fields
                                )
                    
                    if creates:
                        # 分批创建
                        batch_size = 50
                        for i in range(0, len(creates), batch_size):
                            batch_creates = creates[i:i + batch_size]
                            if batch_creates:
                                await self.model_class.bulk_create(batch_creates)
                
                # 数据库操作成功后，记录日志
                logger.info(
                    f"[Worker-{worker_id}] 数据库操作成功 [{self.queue_name}]，"
                    f"更新 {len(updates)}，创建 {len(creates)}"
                )
                
                # 5. 在Redis缓存DB中批量添加缓存（独立于数据库事务）
                try:
                    redis_cache = await self.get_redis_cache()
                    
                    async with redis_cache.pipeline() as cache_pipe:
                        for key, operation in cache_items:
                            key_parts = [str(k) for k in key]
                            cache_key = self.cache_key_prefix + '_'.join(key_parts)
                            # 设置缓存，值为操作类型，过期时间1小时
                            cache_pipe.setex(cache_key, self.cache_expire_seconds, operation)
                        await cache_pipe.execute()
                    
                    logger.debug(
                        f"[Worker-{worker_id}] 缓存添加成功 (DB {self.cache_db}) [{self.queue_name}]，"
                        f"缓存 {len(cache_items)} 条记录，过期时间 {self.cache_expire_seconds}秒"
                    )
                except Exception as cache_error:
                    # 缓存操作失败不影响主流程，只记录警告
                    logger.warning(
                        f"[Worker-{worker_id}] 缓存添加失败 (DB {self.cache_db}) [{self.queue_name}]: {cache_error}，"
                        f"数据库操作已成功，将继续处理"
                    )
                
                # 6. 在另一个管道中删除Redis任务数据（独立操作）
                try:
                    async with redis.pipeline() as delete_pipe:
                        for key in keys_to_process:
                            delete_pipe.delete(key)
                        await delete_pipe.execute()
                    
                    logger.debug(
                        f"[Worker-{worker_id}] 任务清理成功 [{self.queue_name}]，"
                        f"清理 {len(keys_to_process)} 个任务"
                    )
                except Exception as delete_error:
                    # 删除失败记录警告，但不影响主流程
                    logger.warning(
                        f"[Worker-{worker_id}] 任务清理失败 [{self.queue_name}]: {delete_error}"
                    )
                
                # 最终成功日志
                logger.info(
                    f"[Worker-{worker_id}] 成功处理 {len(items)} 条数据 [{self.queue_name}]，"
                    f"更新 {len(updates)}，创建 {len(creates)}"
                )
                return True
                
            except Exception as db_error:
                logger.error(f"[Worker-{worker_id}] 数据库操作失败 [{self.queue_name}]: {db_error}", exc_info=True)
                # 数据库操作失败，重新添加到队列
                try:
                    current_time = time.time()
                    async with redis.pipeline() as retry_pipe:
                        for i, key in enumerate(keys_to_process):
                            retry_pipe.zadd(
                                self.task_key_zset, 
                                {key: current_time + i * 0.001}
                            )
                        await retry_pipe.execute()
                    logger.info(f"[Worker-{worker_id}] 任务已重新加入队列 [{self.queue_name}]")
                except Exception as e:
                    logger.error(f"[Worker-{worker_id}] 重新添加任务失败 [{self.queue_name}]: {e}")
                return False
                
        except Exception as e:
            logger.error(f"[Worker-{worker_id}] 处理批次失败 [{self.queue_name}]: {e}")
            return False
    
    async def _worker_loop(self, worker_id: int):
        """工作线程循环"""
        logger.info(f"[Worker-{worker_id}] 启动 [{self.queue_name}]")
        
        while self._running:
            try:
                success = await self._process_batch(worker_id)
                
                if success:
                    # 检查是否还有数据
                    count = await self.get_queue_size()
                    if count > 0:
                        await asyncio.sleep(self.success_sleep)
                    else:
                        await asyncio.sleep(self.empty_sleep)
                else:
                    # 处理失败，重试
                    retry_count = 0
                    retry_success = False
                    
                    while retry_count < self.max_retries and not retry_success:
                        await asyncio.sleep(self.retry_delay * (retry_count + 1))
                        retry_success = await self._process_batch(worker_id)
                        if retry_success:
                            break
                        retry_count += 1
                    
                    if not retry_success:
                        logger.error(f"[Worker-{worker_id}] 达到最大重试次数 [{self.queue_name}]")
                        await asyncio.sleep(self.fail_sleep * 2)
                        
            except Exception as e:
                logger.error(f"[Worker-{worker_id}] 处理异常 [{self.queue_name}]: {e}")
                await asyncio.sleep(self.fail_sleep)
        
        logger.info(f"[Worker-{worker_id}] 停止 [{self.queue_name}]")
    
    async def start(self):
        """启动队列处理"""
        if not REDIS_ENABLED:
            logger.warning(f"Redis未启用，无法启动队列处理 [{self.queue_name}]")
            return
        
        if self._running:
            logger.warning(f"队列处理已在运行 [{self.queue_name}]")
            return
        
        self._running = True
        await self.init_redis()
        
        # 启动工作线程
        for worker_id in range(self.num_workers):
            worker = asyncio.create_task(self._worker_loop(worker_id))
            self._workers.append(worker)
        
        logger.info(f"队列处理已启动，{self.num_workers} 个工作线程 [{self.queue_name}]")
    
    async def stop(self):
        """停止队列处理"""
        if not self._running:
            return
        
        logger.info(f"正在停止队列处理 [{self.queue_name}]...")
        self._running = False
        
        # 等待所有工作线程完成
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
        
        await self.close()
        logger.info(f"队列处理已停止 [{self.queue_name}]")
