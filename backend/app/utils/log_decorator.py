"""
日志装饰器
用于函数级别的日志记录
"""

import functools
import logging
import time
from typing import Callable
from app.utils.logs import getLogger, safe_repr


def log_function_call(logger_name: str = None, log_args: bool = False, log_result: bool = False):
    """
    函数调用日志装饰器
    
    Args:
        logger_name: 日志器名称，如果不指定则使用函数所在模块名
        log_args: 是否记录函数参数
        log_result: 是否记录函数返回值
    
    Example:
        @log_function_call(logger_name="user", log_args=True)
        def create_user(username: str, email: str):
            return {"id": 1, "username": username}
    """
    def decorator(func: Callable):
        # 获取 logger
        nonlocal logger_name
        if logger_name is None:
            logger_name = func.__module__.split('.')[-1]
        
        logger = getLogger(logger_name)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            # 记录函数调用
            if logger.isEnabledFor(logging.DEBUG):
                if log_args:
                    logger.debug(
                        "调用函数 %s 参数=args%s kwargs=%s",
                        func_name,
                        safe_repr(args),
                        safe_repr(kwargs),
                    )
                else:
                    logger.debug("调用函数 %s", func_name)
            
            try:
                result = await func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if logger.isEnabledFor(logging.DEBUG):
                    if log_result:
                        logger.debug(
                            "函数 %s 完成 耗时=%.3fs 结果=%s",
                            func_name,
                            elapsed,
                            safe_repr(result),
                        )
                    else:
                        logger.debug("函数 %s 完成 耗时=%.3fs", func_name, elapsed)
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    "函数 %s 异常 耗时=%.3fs 错误=%s",
                    func_name,
                    elapsed,
                    safe_repr(e),
                    exc_info=True
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            func_name = func.__name__
            
            # 记录函数调用
            if logger.isEnabledFor(logging.DEBUG):
                if log_args:
                    logger.debug(
                        "调用函数 %s 参数=args%s kwargs=%s",
                        func_name,
                        safe_repr(args),
                        safe_repr(kwargs),
                    )
                else:
                    logger.debug("调用函数 %s", func_name)
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                if logger.isEnabledFor(logging.DEBUG):
                    if log_result:
                        logger.debug(
                            "函数 %s 完成 耗时=%.3fs 结果=%s",
                            func_name,
                            elapsed,
                            safe_repr(result),
                        )
                    else:
                        logger.debug("函数 %s 完成 耗时=%.3fs", func_name, elapsed)
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    "函数 %s 异常 耗时=%.3fs 错误=%s",
                    func_name,
                    elapsed,
                    safe_repr(e),
                    exc_info=True
                )
                raise
        
        # 根据函数类型返回对应的包装器
        if functools.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_exception(logger_name: str = None):
    """
    异常日志装饰器
    只记录异常，不记录正常调用
    
    Example:
        @log_exception(logger_name="user")
        def risky_operation():
            # 可能抛出异常的代码
            pass
    """
    def decorator(func: Callable):
        nonlocal logger_name
        if logger_name is None:
            logger_name = func.__module__.split('.')[-1]
        
        logger = getLogger(logger_name)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    "函数 %s 发生异常: %s",
                    func.__name__,
                    safe_repr(e),
                    exc_info=True
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    "函数 %s 发生异常: %s",
                    func.__name__,
                    safe_repr(e),
                    exc_info=True
                )
                raise
        
        if functools.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
