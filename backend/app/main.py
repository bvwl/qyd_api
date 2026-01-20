import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from tortoise import Tortoise

from app.core import (
    StarletteHTTPException,
    RequestValidationError,
    ResponseValidationError,
    http_exception_handler,
    validation_exception_handler,
    response_validation_exception_handler,
    global_exception_handler,
)
from app.core.settings import TORTOISE_ORM
from app import app as main_router
from app.apis.v1.mail.outlook import auto_check_email_status
from app.utils.log_middleware import LoggingMiddleware
from app.utils.logs import getLogger


# 配置日志
logger = logging.getLogger(__name__)
app_logger = getLogger('app')
scheduler_logger = getLogger('scheduler')
db_logger = getLogger('database')

# 创建调度器实例（全局）
scheduler = AsyncIOScheduler()


async def keep_db_connection_alive() -> None:
    """
    保持数据库连接活跃的函数
    定期执行简单查询以防止连接超时
    """
    try:
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
        scheduler_logger.debug("数据库连接检查成功")
    except Exception as e:
        scheduler_logger.error(f"数据库连接检查失败: {e}", exc_info=True)


async def shutdown_handler() -> None:
    """
    优雅关闭处理函数
    
    关闭顺序：
    1. 关闭调度器（停止新任务）
    2. 等待正在执行的任务完成
    3. 关闭数据库连接
    """
    app_logger.info("开始优雅关闭...")
    
    # 1. 先关闭调度器
    if scheduler and scheduler.running:
        try:
            scheduler.shutdown(wait=False)
            app_logger.info("调度器已关闭")
        except Exception as e:
            app_logger.error(f"关闭调度器出错: {e}", exc_info=True)
    
    # 2. 等待一小段时间，让正在执行的任务完成
    shutdown_wait = float(os.getenv("SHUTDOWN_WAIT_SECONDS", "0.5"))
    if shutdown_wait > 0:
        app_logger.info(f"等待 {shutdown_wait} 秒让任务完成...")
        import asyncio
        await asyncio.sleep(shutdown_wait)
    
    # 3. 关闭数据库连接
    try:
        await Tortoise.close_connections()
        db_logger.info("数据库连接已关闭")
    except Exception as e:
        db_logger.error(f"关闭数据库连接出错: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理函数

    启动阶段：
    - 初始化数据库连接
    - 注册定时任务
    - 启动调度器
    
    关闭阶段：
    - 优雅关闭调度器
    - 关闭数据库连接
    """
    app_logger.info("项目启动...")

    # 初始化数据库连接
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        db_logger.info("数据库初始化完成")
    except Exception as e:
        db_logger.error(f"数据库初始化失败: {e}", exc_info=True)
        raise

    # 配置定时任务
    db_check_interval = int(os.getenv("DB_CHECK_INTERVAL_MINUTES", "30"))
    scheduler.add_job(
        keep_db_connection_alive,
        IntervalTrigger(minutes=db_check_interval),
        id="keep_db_alive",
        name="保持数据库连接",
        coalesce=True,
        misfire_grace_time=30,
    )
    scheduler_logger.info(f"已注册定时任务: 每 {db_check_interval} 分钟检查数据库连接")

    # 可选：自动检查邮箱状态
    enable_email_check = os.getenv("ENABLE_EMAIL_CHECK", "0").lower() in ("1", "true", "yes")
    if enable_email_check:
        email_check_interval = int(os.getenv("EMAIL_CHECK_INTERVAL_HOURS", "1"))
        scheduler.add_job(
            auto_check_email_status,
            IntervalTrigger(hours=email_check_interval),
            id="auto_check_email_status",
            name="自动检查邮箱状态",
            coalesce=True,
            misfire_grace_time=60,
        )
        scheduler_logger.info(f"已注册定时任务: 每 {email_check_interval} 小时检查邮箱状态")

    scheduler.start()
    scheduler_logger.info("调度器已启动")
    
    try:
        yield
    finally:
        await shutdown_handler()


# 创建 FastAPI 应用实例
app = FastAPI(
    title="QYD API",
    description="QYD 项目管理系统 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENABLE_DOCS", "1") == "1" else None,
    redoc_url="/redoc" if os.getenv("ENABLE_DOCS", "1") == "1" else None,
)

# 配置 CORS 中间件
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加日志中间件
app.add_middleware(LoggingMiddleware, logger_name="api")

# 包含主路由
app.include_router(main_router)


# 全局异常处理
@app.exception_handler(StarletteHTTPException)
async def _http_exception_handler(request, exc):
    """
    FastAPI HTTP 异常入口函数，转发到 core 处理
    """
    return http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def _validation_exception_handler(request, exc):
    """
    FastAPI 请求校验异常入口函数，转发到 core 处理
    """
    return validation_exception_handler(request, exc)


@app.exception_handler(ResponseValidationError)
async def _response_validation_exception_handler(request, exc):
    """
    FastAPI 响应校验异常入口函数，转发到 core 处理
    """
    return response_validation_exception_handler(request, exc)


@app.exception_handler(Exception)
async def _global_exception_handler(request, exc):
    """
    FastAPI 全局未捕获异常入口函数，转发到 core 处理
    """
    return global_exception_handler(request, exc)
