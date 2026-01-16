from functools import wraps
from fastapi import HTTPException
from typing import Callable, Any, Optional
import logging
import asyncio
from tortoise.exceptions import OperationalError

# 获取日志记录器
logger = logging.getLogger(__name__)


def handle_exceptions_unified(
    max_retries: int = 0,
    retry_delay: float = 1.0,
    status_code: int = 500,
    custom_message: Optional[str] = None,
    is_background_task: bool = False
):
    """
    统一的异常处理装饰器
    
    集成了所有异常处理功能：数据库重试、自定义状态码、自定义消息、后台任务处理
    
    Args:
        max_retries: 最大重试次数，默认0（不重试）
        retry_delay: 重试间隔时间（秒），默认1秒
        status_code: HTTP状态码，默认500
        custom_message: 自定义错误消息前缀
        is_background_task: 是否为后台任务（不抛出HTTPException）
        
    使用方法:
        # 基础异常处理
        @handle_exceptions_unified()
        async def basic_function(...):
            pass
            
        # 带数据库重试
        @handle_exceptions_unified(max_retries=3, retry_delay=1.0)
        async def db_function(...):
            pass
            
        # 自定义状态码和消息
        @handle_exceptions_unified(status_code=400, custom_message="参数错误")
        async def validation_function(...):
            pass
            
        # 后台任务处理
        @handle_exceptions_unified(is_background_task=True)
        async def background_function(...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except HTTPException as e:
                    # HTTPException 直接抛出，不重试
                    if is_background_task:
                        logger.error(f"后台任务 {func.__name__} HTTPException: {str(e)}")
                        return False
                    raise
                except OperationalError as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # 检查是否是连接相关的错误
                    if any(keyword in error_msg for keyword in [
                        'lost connection', 'connection', 'timeout', 
                        'server has gone away', 'broken pipe'
                    ]):
                        if attempt < max_retries:
                            logger.warning(
                                f"函数 {func.__name__} 数据库连接错误 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)}"
                            )
                            # 等待一段时间后重试，使用指数退避
                            await asyncio.sleep(retry_delay * (2 ** attempt))
                            continue
                        else:
                            logger.error(
                                f"函数 {func.__name__} 数据库连接错误，已达到最大重试次数: {str(e)}"
                            )
                    else:
                        # 非连接错误，直接处理
                        logger.error(f"函数 {func.__name__} 发生数据库错误: {str(e)}")
                        if is_background_task:
                            return False
                        error_detail = f"{custom_message}: {str(e)}" if custom_message else f"数据库操作失败: {str(e)}"
                        raise HTTPException(status_code=status_code, detail=error_detail)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"函数 {func.__name__} 发生异常 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)}"
                        )
                        await asyncio.sleep(retry_delay * (2 ** attempt))
                        continue
                    else:
                        logger.error(f"函数 {func.__name__} 发生异常: {str(e)}", exc_info=True)
                        if is_background_task:
                            return False
                        break
            
            # 所有重试都失败了，处理最后一个异常
            if is_background_task:
                return False
                
            if isinstance(last_exception, OperationalError):
                error_detail = f"{custom_message}: 数据库连接失败: {str(last_exception)}" if custom_message else f"数据库连接失败: {str(last_exception)}"
            else:
                error_detail = f"{custom_message}: {str(last_exception)}" if custom_message else str(last_exception)
            
            raise HTTPException(status_code=status_code, detail=error_detail)
        
        return wrapper
    return decorator


# 向后兼容的别名函数
def handle_exceptions_with_db_retry(max_retries: int = 3, retry_delay: float = 1.0):
    """
    带数据库连接重试的异常处理装饰器（向后兼容）
    
    这是 handle_exceptions_unified 的别名，保持向后兼容性
    """
    return handle_exceptions_unified(max_retries=max_retries, retry_delay=retry_delay)


def handle_exceptions(func: Callable) -> Callable:
    """
    基础异常处理装饰器（向后兼容）
    
    这是 handle_exceptions_unified() 的别名，保持向后兼容性
    """
    return handle_exceptions_unified()(func)


def handle_background_task_exceptions(func: Callable) -> Callable:
    """
    后台任务异常处理装饰器（向后兼容）
    
    这是 handle_exceptions_unified 的别名，保持向后兼容性
    """
    return handle_exceptions_unified(is_background_task=True)(func)


def handle_exceptions_with_custom_message(message: str = "操作失败"):
    """
    带自定义错误消息的异常处理装饰器（向后兼容）
    
    这是 handle_exceptions_unified 的别名，保持向后兼容性
    """
    return handle_exceptions_unified(custom_message=message)


def handle_exceptions_with_status_code(status_code: int = 500, message: str = None):
    """
    带自定义状态码和错误消息的异常处理装饰器（向后兼容）
    
    这是 handle_exceptions_unified 的别名，保持向后兼容性
    """
    return handle_exceptions_unified(status_code=status_code, custom_message=message)