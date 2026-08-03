import asyncio
from functools import wraps
import time
from app.utils.logs import getLogger, safe_repr


logger = getLogger("app")


def retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 1.0):
    """
    通用重试装饰器
    :param max_retries: 最大重试次数
    :param delay: 每次重试的初始延迟（秒）
    :param backoff: 每次重试延迟的递增倍数
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                # 尝试将当前重试次数注入到 self (args[0]) 中
                if args and hasattr(args[0], '__class__'):
                    try:
                        setattr(args[0], '_async_retry_count', retries)
                    except AttributeError:
                        pass
                    
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.warning(
                            "函数 %s 在尝试了 %d 次后失败，错误信息: %s",
                            func.__name__, max_retries, safe_repr(e),
                        )
                        return None  # 重试次数用尽后返回 None
                    logger.warning(
                        "正在重试 %s %d/%d 因错误: %s",
                        func.__name__, retries + 1, max_retries, safe_repr(e),
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            return None  # 三次重试仍未成功，返回 None

        return wrapper

    return decorator


def async_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 1.0):
    """
    支持异步函数的通用重试装饰器
    :param max_retries: 最大重试次数
    :param delay: 每次重试的初始延迟（秒）
    :param backoff: 每次重试延迟的递增倍数
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                # 尝试将当前重试次数注入到 self (args[0]) 中
                if args and hasattr(args[0], '__class__'):
                    try:
                        setattr(args[0], '_async_retry_count', retries)
                    except AttributeError:
                        pass

                try:
                    return await func(*args, **kwargs)  # 直接执行原始方法
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.warning(
                            "函数 %s 在尝试了 %d 次后失败，错误信息: %s",
                            func.__name__, max_retries, safe_repr(e),
                        )
                        return None  # 重试次数用尽后返回 None
                    logger.warning(
                        "正在重试 %s %d/%d 因错误: %s",
                        func.__name__, retries + 1, max_retries, safe_repr(e),
                    )

                await asyncio.sleep(current_delay)  # 异步延迟
                current_delay *= backoff  # 根据backoff递增延迟

            return None  # 三次重试仍未成功，返回 None

        return wrapper

    return decorator
