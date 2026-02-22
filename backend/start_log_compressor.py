#!/usr/bin/env python3
"""
独立的日志压缩服务
专门用于高并发环境，避免影响主服务性能

功能：
1. 每2小时压缩旧日志文件
2. 删除超过7天的压缩日志
3. 按日期组织日志目录结构
4. 支持优雅关闭

使用方式：
  python start_log_compressor.py
"""
import os
import sys
import signal
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger


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


# 加载环境变量
load_env_from_file()

# 导入日志工具
from app.utils.logs import compress_all_logs, get_log_statistics


# 配置基础日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("log_compressor")


class LogCompressorService:
    """日志压缩服务"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.running = False
        
    async def compress_logs_task(self) -> None:
        """
        压缩旧日志文件的定时任务
        
        日志策略：
        - 单个日志文件最大200MB，达到后自动分割
        - 旧日志自动压缩为.gz格式并按日期组织
        - 只保留最近7天的日志，超过7天自动删除
        """
        try:
            logger.info("=" * 60)
            logger.info("开始执行日志压缩任务...")
            logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 显示压缩前的统计信息
            stats_before = get_log_statistics()
            logger.info(f"压缩前统计:")
            logger.info(f"  总文件数: {stats_before['total_files']}")
            logger.info(f"  总大小: {stats_before['total_size'] / 1024 / 1024:.2f} MB")
            logger.info(f"  已压缩文件: {stats_before['compressed_files']}")
            
            # 在线程池中异步执行同步函数，避免阻塞事件循环
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, compress_all_logs)
            
            # 显示压缩后的统计信息
            stats_after = get_log_statistics()
            logger.info(f"压缩后统计:")
            logger.info(f"  总文件数: {stats_after['total_files']}")
            logger.info(f"  总大小: {stats_after['total_size'] / 1024 / 1024:.2f} MB")
            logger.info(f"  已压缩文件: {stats_after['compressed_files']}")
            
            # 计算节省的空间
            saved_space = stats_before['total_size'] - stats_after['total_size']
            if saved_space > 0:
                logger.info(f"  节省空间: {saved_space / 1024 / 1024:.2f} MB")
            
            logger.info("日志压缩任务完成")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"日志压缩任务失败: {e}", exc_info=True)
    
    async def start(self):
        """启动服务"""
        if self.running:
            logger.warning("服务已在运行中")
            return
        
        logger.info("=" * 60)
        logger.info("日志压缩服务启动中...")
        logger.info("=" * 60)
        
        # 读取配置
        compress_interval = int(os.getenv("LOG_COMPRESS_INTERVAL_HOURS", "2"))
        retention_days = int(os.getenv("LOG_RETENTION_DAYS", "7"))
        
        logger.info(f"配置信息:")
        logger.info(f"  压缩间隔: 每 {compress_interval} 小时")
        logger.info(f"  保留天数: {retention_days} 天")
        logger.info(f"  日志目录: logs/")
        
        # 启动时立即执行一次压缩（可选）
        run_on_startup = os.getenv("LOG_COMPRESS_ON_STARTUP", "1").lower() in ("1", "true", "yes")
        if run_on_startup:
            logger.info("启动时执行首次压缩...")
            await self.compress_logs_task()
        else:
            logger.info("跳过启动时压缩（LOG_COMPRESS_ON_STARTUP=0）")
        
        # 注册定时任务
        self.scheduler.add_job(
            self.compress_logs_task,
            IntervalTrigger(hours=compress_interval),
            id="compress_logs",
            name="压缩旧日志文件",
            coalesce=True,  # 如果错过了执行时间，只执行一次
            misfire_grace_time=300,  # 5分钟容错
        )
        
        # 启动调度器
        self.scheduler.start()
        self.running = True
        
        logger.info("=" * 60)
        logger.info("日志压缩服务已启动")
        logger.info(f"下次执行时间: {datetime.now().replace(microsecond=0)}")
        logger.info("按 Ctrl+C 停止服务")
        logger.info("=" * 60)
    
    async def stop(self):
        """停止服务"""
        if not self.running:
            return
        
        logger.info("=" * 60)
        logger.info("正在停止日志压缩服务...")
        
        # 关闭调度器
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("调度器已关闭")
        
        self.running = False
        logger.info("日志压缩服务已停止")
        logger.info("=" * 60)


# 全局服务实例
service = LogCompressorService()


def signal_handler(signum, frame):
    """信号处理器（用于优雅关闭）"""
    logger.info(f"收到信号 {signum}，准备关闭...")
    asyncio.create_task(service.stop())
    sys.exit(0)


async def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务
    await service.start()
    
    # 保持运行
    try:
        while service.running:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到键盘中断...")
    finally:
        await service.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("服务已停止")
