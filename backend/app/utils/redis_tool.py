import redis
from loguru import logger


class RedisClient:
    def __init__(self, host: str = 'localhost', port: int = 6379, password: str = None):
        self.host = host
        self.port = port
        self.password = password
        self.browser_client = None
        self.task_client = None
        self.cache_client = None
        self.ok_client = None
        self.init()

    # 初始化
    def init(self):
        """
        初始化Redis客户端
        :return:
        """
        if self.browser_client is None:
            self.browser_client = redis.Redis(host=self.host, port=self.port, password=self.password, db=0,
                                              decode_responses=True)

        if self.task_client is None:
            self.task_client = redis.Redis(host=self.host, port=self.port, password=self.password, db=1,
                                           decode_responses=True)

        if self.cache_client is None:
            self.cache_client = redis.Redis(host=self.host, port=self.port, password=self.password, db=2,
                                            decode_responses=True)

        if self.ok_client is None:
            self.ok_client = redis.Redis(host=self.host, port=self.port, password=self.password, db=3,
                                         decode_responses=True)

        logger.info("Redis连接已初始化")

    # 关闭连接
    def close(self):
        self.browser_client.close()
        self.task_client.close()
        self.cache_client.close()
        self.ok_client.close()
        logger.info("Redis连接已关闭")

    """browser_client"""

    # 写入浏览器信息
    async def set_browser(self, browser_id: str, data: dict):
        try:
            # 处理None值，将其转换为空字符串
            processed_data = {}
            for key, value in data.items():
                if value is None:
                    processed_data[key] = ""
                else:
                    processed_data[key] = value

            self.browser_client.hset(browser_id, mapping=processed_data)
            logger.info(f"写入浏览器信息: {browser_id} - {processed_data}")
            return True
        except Exception as e:
            logger.error(f"写入浏览器信息失败: {browser_id} - {e}")
            return False

    # 获取浏览器信息
    async def get_browser(self, browser_id: str = None):
        try:
            if browser_id is None:
                # 获取全部数据
                data = self.browser_client.hgetall()
            else:
                data = self.browser_client.hgetall(browser_id)
                logger.info(f"获取浏览器信息: {browser_id} - {data}")
            return data
        except Exception as e:
            logger.error(f"获取浏览器信息失败: {browser_id} - {e}")


async def main():
    host = '183.66.27.14'
    port = 50086
    password = 'redis_AdJsBP'
    redis_client = RedisClient(host, port, password)
    # await redis_client.set_browser('9eac7f95ca2d47359ace4083a566e119', {'status': 'online', 'current_task_id': None})
    await redis_client.get_browser('9eac7f95ca2d47359ace4083a566e119')
    # 关闭连接
    redis_client.close()


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
