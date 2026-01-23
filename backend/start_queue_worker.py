"""
独立的Redis队列处理进程
用于分离队列处理和HTTP服务，避免Uvicorn多进程导致的资源耗尽问题
"""
import os
import asyncio
import logging
import signal
from pathlib import Path


def load_env_from_file(env_path: Path | None = None) -> None:
    """加载 .env 文件中的环境变量"""
    if env_path is None:
        env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        os.environ.setdefault(key, value)


# 先加载环境变量，再导入settings
load_env_from_file()

# 现在导入settings和其他模块
from tortoise import Tortoise
from app.core.settings import get_tortoise_config, REDIS_ENABLED
from app.utils.logs import getLogger


# 配置日志
logger = getLogger('app')
scheduler_logger = getLogger('scheduler')


class QueueWorkerManager:
    """队列处理管理器"""
    
    def __init__(self):
        self.running = False
        self.queue_handler = None
    
    async def start(self):
        """启动队列处理"""
        logger.info("=" * 60)
        logger.info("启动独立Redis队列处理进程")
        logger.info("=" * 60)
        
        # 初始化数据库连接
        try:
            await Tortoise.init(config=get_tortoise_config())
            logger.info("数据库初始化完成")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}", exc_info=True)
            raise
        
        # 检查Redis是否启用
        if not REDIS_ENABLED:
            logger.error("Redis未启用，无法启动队列处理")
            return
        
        # 启动队列处理
        try:
            from app.utils.project_account_queue import project_account_queue
            self.queue_handler = project_account_queue
            
            await self.queue_handler.start()
            logger.info("Redis队列处理已启动")
            
            # 显示配置信息
            logger.info(f"队列名称: {self.queue_handler.queue_name}")
            logger.info(f"工作线程数: {self.queue_handler.num_workers}")
            logger.info(f"批处理大小: {self.queue_handler.batch_size}")
            
            self.running = True
            
            # 保持运行
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"队列处理启动失败: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """停止队列处理"""
        logger.info("正在停止队列处理...")
        self.running = False
        
        if self.queue_handler:
            try:
                await self.queue_handler.stop()
                logger.info("队列处理已停止")
            except Exception as e:
                logger.error(f"停止队列处理失败: {e}", exc_info=True)
        
        # 关闭数据库连接
        try:
            await Tortoise.close_connections()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}", exc_info=True)


# 全局管理器实例
manager = QueueWorkerManager()


def signal_handler(signum, frame):
    """信号处理函数"""
    logger.info(f"收到信号 {signum}，准备退出...")
    manager.running = False


async def main():
    """主函数"""
    # 配置日志
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await manager.start()
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
    except Exception as e:
        logger.error(f"队列处理异常退出: {e}", exc_info=True)
    finally:
        await manager.stop()
        logger.info("队列处理进程已退出")


if __name__ == "__main__":
    asyncio.run(main())
