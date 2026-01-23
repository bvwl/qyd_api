"""
FastAPI 日志中间件
自动记录所有 API 请求和响应
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from app.utils.logs import getLogger
from app.utils.jwt_tool import JwtToken


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    API 请求日志中间件
    自动记录所有请求的详细信息，包括操作人信息
    """
    
    def __init__(self, app: ASGIApp, logger_name: str = "api"):
        super().__init__(app)
        self.logger = getLogger(logger_name)
    
    async def dispatch(self, request: Request, call_next):
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        method = request.method
        client_ip = request.client.host if request.client else "unknown"
        
        # 尝试从JWT Token中获取用户ID
        user_id = "server"  # 默认为server
        
        try:
            # 从Authorization header中提取JWT Token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
                payload = JwtToken.verify_token(token)
                user_id = payload.get("id", "server")
                
                # 将用户ID存储到request.state，供后续使用
                request.state.user_id = user_id
        except Exception:
            # Token验证失败，使用默认值server
            pass
        
        # 获取查询参数
        query_params = dict(request.query_params) if request.query_params else None
        
        try:
            # 处理请求
            response: Response = await call_next(request)
            
            # 计算处理时间
            process_time = time.time() - start_time
            
            # 构建日志信息
            log_parts = []
            
            # 添加用户ID
            log_parts.append(f"user_id={user_id}")
            
            # 添加IP地址
            log_parts.append(f"IP={client_ip}")
            
            # 添加请求信息
            log_parts.append(f"{method} {request.url.path}")
            
            # 添加查询参数（过滤敏感信息）
            if query_params:
                safe_params = {k: v for k, v in query_params.items() 
                              if k.lower() not in ['password', 'token', 'secret', 'key']}
                if safe_params:
                    log_parts.append(f"参数={safe_params}")
            
            # 添加响应状态
            log_parts.append(f"状态={response.status_code}")
            
            # 添加处理时间
            log_parts.append(f"耗时={process_time:.3f}s")
            
            # 记录日志
            log_message = " ".join(log_parts)
            
            # 根据状态码选择日志级别
            if response.status_code >= 500:
                self.logger.error(log_message)
            elif response.status_code >= 400:
                self.logger.warning(log_message)
            else:
                self.logger.info(log_message)
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = f"{process_time:.3f}s"
            
            # 如果响应时间过长，记录警告
            if process_time > 3.0:
                self.logger.warning(
                    f"慢请求 user_id={user_id} {method} {request.url.path} "
                    f"耗时={process_time:.3f}s IP={client_ip}"
                )
            
            return response
            
        except Exception as e:
            # 记录异常
            process_time = time.time() - start_time
            self.logger.error(
                f"请求异常 user_id={user_id} {method} {request.url.path} "
                f"错误={str(e)} IP={client_ip} 耗时={process_time:.3f}s",
                exc_info=True
            )
            raise
