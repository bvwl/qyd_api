"""
FastAPI 日志中间件
自动记录所有 API 请求和响应
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from app.utils.logs import getLogger, log_api_call


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    API 请求日志中间件
    自动记录所有请求的详细信息
    """
    
    def __init__(self, app: ASGIApp, logger_name: str = "api"):
        super().__init__(app)
        self.logger = getLogger(logger_name)
    
    async def dispatch(self, request: Request, call_next):
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        url = str(request.url)
        client_ip = request.client.host if request.client else "unknown"
        
        # 尝试获取用户ID（从请求状态中，需要在认证中间件中设置）
        user_id = getattr(request.state, "user_id", None)
        
        # 获取查询参数
        query_params = dict(request.query_params) if request.query_params else None
        
        try:
            # 处理请求
            response: Response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 记录日志
            log_api_call(
                logger=self.logger,
                user_id=str(user_id) if user_id else None,
                endpoint=request.url.path,
                method=method,
                params=query_params,
                response_status=response.status_code,
                client_ip=client_ip
            )
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = f"{process_time:.3f}s"
            
            # 如果响应时间过长，记录警告
            if process_time > 3.0:
                self.logger.warning(
                    f"慢请求 {method} {request.url.path} "
                    f"耗时={process_time:.3f}s IP={client_ip}"
                )
            
            return response
            
        except Exception as e:
            # 记录异常
            self.logger.error(
                f"请求异常 {method} {request.url.path} "
                f"错误={str(e)} IP={client_ip}",
                exc_info=True
            )
            raise
