from fastapi import Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    处理 HTTP 异常并返回统一响应
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None),
    )


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    处理请求校验异常并返回详细错误信息
    """
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": str(getattr(exc, "body", ""))},
    )


def response_validation_exception_handler(request: Request, exc: ResponseValidationError) -> JSONResponse:
    """
    处理响应校验异常并返回统一错误格式
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "Response validation error", "errors": exc.errors()},
    )


def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    处理所有未捕获异常并返回统一错误响应
    """
    # 异常已由 LoggingMiddleware 统一记录；这里仅生成响应，避免重复堆栈。
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )


__all__ = [
    "StarletteHTTPException",
    "RequestValidationError",
    "ResponseValidationError",
    "http_exception_handler",
    "validation_exception_handler",
    "response_validation_exception_handler",
    "global_exception_handler",
]
