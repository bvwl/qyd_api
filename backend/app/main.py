from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from tortoise import Tortoise
from contextlib import asynccontextmanager
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
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理函数

    - 启动：注册定时任务并启动调度器
    - 关闭：优雅关闭调度器与数据库连接
    """
    print('项目启动...')

    # 初始化数据库连接（使用 Tortoise 直接初始化，确保路由与定时任务可用）
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        print('数据库初始化完成')
    except Exception as e:
        print(f'数据库初始化失败: {e}')

    # 每30分钟保持一次数据库连接活跃
    scheduler.add_job(
        keep_db_connection_alive,
        IntervalTrigger(minutes=30),
        id='keep_db_alive',
        name='保持数据库连接',
        coalesce=True,
        misfire_grace_time=30,
    )

    # 每1小时自动检查 N 天前未更新的正常邮箱状态
    # scheduler.add_job(
    #     auto_check_email_status,
    #     IntervalTrigger(hours=1),
    #     id='auto_check_email_status',
    #     name='自动检查邮箱状态',
    #     coalesce=True,
    #     misfire_grace_time=60,
    # )

    scheduler.start()
    try:
        yield
    finally:
        print('项目结束...')

        # 关闭数据库连接
        print('关闭数据库连接...')
        try:
            await asyncio.wait_for(Tortoise.close_connections(), timeout=2)
        except asyncio.TimeoutError:
            print('关闭数据库连接超时')
        except Exception as e:
            print(f'关闭数据库连接出错: {e}')

        # 关闭调度器
        print('关闭调度器...')
        try:
            if scheduler is not None and hasattr(scheduler, 'shutdown'):
                scheduler.shutdown(wait=False)
        except Exception as e:
            print(f'关闭调度器出错: {e}')


# 创建 FastAPI 应用实例
app = FastAPI(lifespan=lifespan)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建调度器实例
scheduler = AsyncIOScheduler()

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


# 注意：使用自定义 lifespan 已在启动时手动初始化数据库。
# 若改回默认事件机制，可重新启用 register_tortoise。


async def keep_db_connection_alive():
    """
    保持数据库连接活跃的函数
    定期执行简单查询以防止连接超时
    """
    try:
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
        print("数据库连接检查成功")
    except Exception as e:
        print(f"数据库连接检查失败: {e}")


# 依赖 FastAPI lifespan 与 uvicorn 默认信号处理进行优雅关闭


if __name__ == '__main__':
    from uvicorn import run

    run(
        'main:app',
        host='0.0.0.0',
        port=6080,
        reload=False,
        workers=1,
        # loop='uvloop',
        http='httptools',
        limit_concurrency=10000,
        backlog=4096,
        timeout_keep_alive=5
    )
