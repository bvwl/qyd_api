import os
from fastapi import Request, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from .logs import getLogger

logger = getLogger(os.environ.get('APP_NAME'))


def global_http_exception_handler(request: Request, exc):
    """
    全局HTTP请求处理异常
    :param request: HTTP请求对象
    :param exc: 本次发生的异常对象
    :return:
    """

    # 使用日志记录异常
    logger.error(f"发生异常：{exc.detail}")

    # 直接返回JSONResponse，避免重新抛出异常导致循环
    return JSONResponse(
        status_code=exc.status_code, 
        content={
            'err_msg': exc.detail,
            'status': False
        },
        headers=getattr(exc, 'headers', None)
    )


def global_request_exception_handler(request: Request, exc):
    """
    全局请求校验异常处理函数
    :param request: HTTP请求对象
    :param exc: 本次发生的异常对象
    :return:
    """

    # 直接返回JSONResponse，避免重新抛出异常
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, 
        content={
            'err_msg': exc.errors()[0],
            'status': False
        }
    )
