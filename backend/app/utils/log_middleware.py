"""
FastAPI 日志中间件
自动记录所有 API 请求和响应
"""

from fastapi import Request
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send
import itertools
import os
import time
from app.utils.logs import getLogger, safe_repr, sanitize_mapping
from app.utils.jwt_tool import JwtToken


def get_request_ip(request: Request) -> tuple[str, str | None]:
    """
    获取真实调用方 IP。

    优先级：
    1. X-Forwarded-For 的第一个 IP（真实客户端）
    2. X-Real-IP
    3. CF-Connecting-IP / True-Client-IP（兼容 CDN）
    4. request.client.host（直连或兜底）
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # 代理头来自外部输入，限制数量和长度，避免恶意超长日志。
        ip_chain = [ip.strip()[:64] for ip in forwarded_for.split(",", 10) if ip.strip()][:10]
        if ip_chain:
            return ip_chain[0], " -> ".join(ip_chain)

    for header_name in ("X-Real-IP", "CF-Connecting-IP", "True-Client-IP"):
        header_ip = request.headers.get(header_name)
        if header_ip:
            return header_ip.strip()[:64], None

    return (request.client.host if request.client else "unknown"), None


class LoggingMiddleware:
    """
    API 请求日志中间件
    自动记录所有请求的详细信息，包括操作人信息
    """

    def __init__(self, app: ASGIApp, logger_name: str = "api"):
        self.app = app
        self.logger = getLogger(logger_name)
        self.slow_request_seconds = self._get_float_env("API_LOG_SLOW_SECONDS", 3.0, 0.001, 3600.0)
        self.success_sample_rate = self._get_float_env(
            "API_LOG_SUCCESS_SAMPLE_RATE", 0.01, 0.0, 1.0
        )
        self.client_error_sample_rate = self._get_float_env(
            "API_LOG_CLIENT_ERROR_SAMPLE_RATE", 0.1, 0.0, 1.0
        )
        self.skip_paths = {
            path.strip()
            for path in os.getenv("API_LOG_SKIP_PATHS", "/health,/api/health").split(",")
            if path.strip()
        }
        self._request_counter = itertools.count()
        self._client_error_counter = itertools.count()

    @staticmethod
    def _get_float_env(name: str, default: float, minimum: float, maximum: float) -> float:
        try:
            return min(maximum, max(minimum, float(os.getenv(name, str(default)))))
        except (TypeError, ValueError):
            return default

    def _should_log_success(self, path: str) -> bool:
        if path in self.skip_paths or self.success_sample_rate <= 0:
            return False
        if self.success_sample_rate >= 1:
            return True
        sample_every = max(1, round(1 / self.success_sample_rate))
        return next(self._request_counter) % sample_every == 0

    def _should_log_client_error(self) -> bool:
        if self.client_error_sample_rate <= 0:
            return False
        if self.client_error_sample_rate >= 1:
            return True
        sample_every = max(1, round(1 / self.client_error_sample_rate))
        return next(self._client_error_counter) % sample_every == 0

    @staticmethod
    def _get_user_id(request: Request) -> str:
        """仅在确实要写日志时解析 token，避免每个成功请求重复做 JWT 校验。"""
        authenticated_user_id = getattr(request.state, "user_id", None)
        if authenticated_user_id:
            return str(authenticated_user_id)[:128]

        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                payload = JwtToken.verify_token(auth_header[7:])
                return str(payload.get("id", "server"))[:128]
        except Exception:
            pass
        return "server"

    def _log_response(
        self,
        request: Request,
        method: str,
        client_ip: str,
        proxy_chain: str | None,
        status_code: int,
        process_time: float,
    ) -> None:
        path = request.url.path
        is_slow = process_time > self.slow_request_seconds
        is_important_client_error = status_code in {401, 403, 429}
        is_sampled_client_error = (
            400 <= status_code < 500
            and not is_important_client_error
            and self._should_log_client_error()
        )
        should_log = (
            status_code >= 500
            or is_important_client_error
            or is_sampled_client_error
            or is_slow
            or (status_code < 400 and self._should_log_success(path))
        )
        if not should_log:
            return

        user_id = self._get_user_id(request)
        log_parts = [f"user_id={user_id}", f"IP={client_ip}"]
        if proxy_chain and proxy_chain != client_ip:
            log_parts.append(f"代理链={proxy_chain}")
        log_parts.append(f"{method} {path[:2048]}")

        if request.query_params:
            safe_params = sanitize_mapping(dict(request.query_params))
            if safe_params:
                log_parts.append(f"参数={safe_repr(safe_params)}")

        log_parts.append(f"状态={status_code}")
        log_parts.append(f"耗时={process_time:.3f}s")
        log_message = " ".join(log_parts)

        if status_code >= 500:
            self.logger.error(log_message)
        elif status_code >= 400 or is_slow:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # 纯 ASGI 中间件不创建 BaseHTTPMiddleware 的额外任务和内存流。
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        request = Request(scope)
        method = request.method
        client_ip, proxy_chain = get_request_ip(request)
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                headers = MutableHeaders(scope=message)
                headers["X-Process-Time"] = f"{time.perf_counter() - start_time:.3f}s"
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            process_time = time.perf_counter() - start_time
            user_id = self._get_user_id(request)
            self.logger.error(
                f"请求异常 user_id={user_id} {method} {request.url.path[:2048]} "
                f"错误={safe_repr(e)} IP={client_ip} 耗时={process_time:.3f}s",
                exc_info=True
            )
            raise
        else:
            self._log_response(
                request,
                method,
                client_ip,
                proxy_chain,
                status_code,
                time.perf_counter() - start_time,
            )
