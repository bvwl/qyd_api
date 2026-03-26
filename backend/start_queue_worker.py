"""
独立的Redis队列处理进程
用于分离队列处理和HTTP服务，避免Uvicorn多进程导致的资源耗尽问题

支持多进程模式（利用多核CPU）：
  QUEUE_WORKER_PROCESSES=N  启动 N 个独立进程，每个进程有自己的事件循环
  默认值为 1（单进程，向后兼容）
  Redis zpopmin 是原子操作，多进程竞争消费是安全的
"""
import os
import asyncio
import logging
import multiprocessing
import signal
import sys
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
        self.queue_handlers = []
    
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
            from app.utils.project_withdrawal_queue import project_withdrawal_queue
            
            # 启动项目账号队列
            await project_account_queue.start()
            logger.info("项目账号队列处理已启动")
            logger.info(f"  队列名称: {project_account_queue.queue_name}")
            logger.info(f"  工作线程数: {project_account_queue.num_workers}")
            logger.info(f"  批处理大小: {project_account_queue.batch_size}")
            
            # 启动项目提现队列
            await project_withdrawal_queue.start()
            logger.info("项目提现队列处理已启动")
            logger.info(f"  队列名称: {project_withdrawal_queue.queue_name}")
            logger.info(f"  工作线程数: {project_withdrawal_queue.num_workers}")
            logger.info(f"  批处理大小: {project_withdrawal_queue.batch_size}")
            
            self.queue_handlers = [project_account_queue, project_withdrawal_queue]
            
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
        
        for queue_handler in self.queue_handlers:
            try:
                await queue_handler.stop()
                logger.info(f"队列 {queue_handler.queue_name} 已停止")
            except Exception as e:
                logger.error(f"停止队列 {queue_handler.queue_name} 失败: {e}", exc_info=True)
        
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
    """单进程主函数"""
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


def _worker_process_entry(process_id: int, env_path_str: str) -> None:
    """
    子进程入口：每个进程拥有独立的事件循环和数据库/Redis连接，
    通过 Redis zpopmin（原子操作）安全地多进程竞争消费同一队列。
    """
    # 子进程需要重新加载环境变量（fork 前已加载，但 spawn 模式需要）
    load_env_from_file(Path(env_path_str) if env_path_str else None)

    # 重新初始化日志（避免多进程共享文件句柄）
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=f"%(asctime)s [worker-{process_id}] %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )

    # 导入放在子进程内部，避免 spawn 模式下的继承问题
    from tortoise import Tortoise as _Tortoise
    from app.core.settings import get_tortoise_config as _get_cfg, REDIS_ENABLED as _REDIS_ENABLED
    from app.utils.logs import getLogger as _getLogger
    from app.utils.project_account_queue import project_account_queue as _paq
    from app.utils.project_withdrawal_queue import project_withdrawal_queue as _pwq

    _logger = _getLogger('app')
    _logger.info(f"子进程 {process_id} (PID={os.getpid()}) 已启动")

    _running = True

    def _child_signal(signum, frame):
        nonlocal _running
        _logger.info(f"子进程 {process_id} 收到信号 {signum}，准备退出...")
        _running = False

    signal.signal(signal.SIGINT, _child_signal)
    signal.signal(signal.SIGTERM, _child_signal)

    async def _child_main():
        await _Tortoise.init(config=_get_cfg())
        _logger.info(f"子进程 {process_id} 数据库初始化完成")

        if not _REDIS_ENABLED:
            _logger.error("Redis未启用，子进程退出")
            return

        await _paq.start()
        await _pwq.start()
        _logger.info(f"子进程 {process_id} 队列处理已启动")

        while _running:
            await asyncio.sleep(1)

        _logger.info(f"子进程 {process_id} 正在停止队列...")
        await _paq.stop()
        await _pwq.stop()
        await _Tortoise.close_connections()
        _logger.info(f"子进程 {process_id} 已退出")

    try:
        asyncio.run(_child_main())
    except Exception as exc:
        _logger.error(f"子进程 {process_id} 异常退出: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    num_processes = int(os.getenv("QUEUE_WORKER_PROCESSES", "1"))

    if num_processes <= 1:
        # 单进程模式（默认，向后兼容）
        asyncio.run(main())
    else:
        # 多进程模式：每个进程独立事件循环，真正利用多核 CPU
        env_path_str = str(Path(__file__).resolve().parent / ".env")
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format="%(asctime)s [main] %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        main_logger = logging.getLogger("app")
        main_logger.info(f"启动 {num_processes} 个队列处理进程（多核模式）")

        # 使用 spawn 上下文保证跨平台兼容性
        ctx = multiprocessing.get_context("spawn")
        processes: list[multiprocessing.Process] = []
        for pid in range(num_processes):
            p = ctx.Process(
                target=_worker_process_entry,
                args=(pid, env_path_str),
                daemon=False,
            )
            p.start()
            processes.append(p)
            main_logger.info(f"子进程 {pid} 已启动 (PID={p.pid})")

        def _main_signal(signum, frame):
            main_logger.info(f"主进程收到信号 {signum}，向所有子进程发送 SIGTERM...")
            for p in processes:
                if p.is_alive():
                    p.terminate()

        signal.signal(signal.SIGINT, _main_signal)
        signal.signal(signal.SIGTERM, _main_signal)

        # 等待所有子进程结束
        for p in processes:
            p.join()
            main_logger.info(f"子进程 PID={p.pid} 已退出，退出码={p.exitcode}")

        main_logger.info("所有队列处理进程已退出")

