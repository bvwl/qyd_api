"""
日志系统使用示例
展示各种场景下的日志使用方法
"""

from app.utils.logs import getLogger, log_api_call
from app.utils.log_decorator import log_function_call, log_exception


# ============ 示例 1: 基础日志使用 ============

def example_basic_logging():
    """基础日志记录"""
    logger = getLogger('example')
    
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    logger.critical("这是严重错误")


# ============ 示例 2: 不同模块使用独立日志 ============

def example_module_logging():
    """不同模块使用独立的日志文件"""
    
    # 用户模块
    user_logger = getLogger('user')
    user_logger.info("用户登录成功 user_id=123")
    
    # 项目模块
    project_logger = getLogger('project')
    project_logger.info("创建新项目 project_id=456")
    
    # 服务器模块
    server_logger = getLogger('server')
    server_logger.info("服务器健康检查通过")
    
    # 邮件模块
    mail_logger = getLogger('mail')
    mail_logger.info("发送邮件成功 to=user@example.com")


# ============ 示例 3: API 调用日志 ============

def example_api_logging():
    """记录 API 调用信息"""
    logger = getLogger('api')
    
    # 成功的 API 调用
    log_api_call(
        logger=logger,
        user_id="user123",
        endpoint="/api/v1/users/profile",
        method="GET",
        params={"fields": ["name", "email"]},
        response_status=200,
        client_ip="192.168.1.100"
    )
    
    # 失败的 API 调用
    log_api_call(
        logger=logger,
        user_id="user456",
        endpoint="/api/v1/users/login",
        method="POST",
        params={"username": "test", "password": "will_be_filtered"},
        response_status=401,
        client_ip="10.0.0.50"
    )


# ============ 示例 4: 使用装饰器记录函数调用 ============

@log_function_call(logger_name="user", log_args=True, log_result=True)
def create_user(username: str, email: str):
    """创建用户"""
    # 模拟创建用户
    return {"id": 1, "username": username, "email": email}


@log_function_call(logger_name="user")
async def async_get_user(user_id: int):
    """异步获取用户信息"""
    # 模拟异步操作
    import asyncio
    await asyncio.sleep(0.1)
    return {"id": user_id, "username": "test"}


# ============ 示例 5: 异常日志记录 ============

@log_exception(logger_name="error")
def risky_operation():
    """可能抛出异常的操作"""
    # 模拟异常
    raise ValueError("这是一个测试异常")


def example_exception_logging():
    """异常日志记录示例"""
    logger = getLogger('error')
    
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error(f"除零错误: {e}", exc_info=True)
    
    try:
        risky_operation()
    except ValueError:
        pass  # 异常已被装饰器记录


# ============ 示例 6: 业务日志记录 ============

def example_business_logging():
    """业务操作日志记录"""
    logger = getLogger('business')
    
    # 用户操作日志
    logger.info("用户注册 username=newuser email=new@example.com")
    logger.info("用户登录 user_id=123 ip=192.168.1.100")
    logger.info("用户修改密码 user_id=123")
    
    # 订单操作日志
    logger.info("创建订单 order_id=789 user_id=123 amount=99.99")
    logger.info("订单支付 order_id=789 payment_method=alipay")
    logger.info("订单完成 order_id=789")
    
    # 系统操作日志
    logger.warning("系统负载过高 cpu=85% memory=90%")
    logger.error("数据库连接失败 retry_count=3")


# ============ 示例 7: 性能监控日志 ============

def example_performance_logging():
    """性能监控日志"""
    import time
    
    logger = getLogger('performance')
    
    # 记录慢查询
    start = time.time()
    # 模拟慢查询
    time.sleep(0.5)
    elapsed = time.time() - start
    
    if elapsed > 0.3:
        logger.warning(f"慢查询检测 sql='SELECT * FROM users' 耗时={elapsed:.3f}s")
    
    # 记录缓存命中率
    cache_hits = 850
    cache_misses = 150
    hit_rate = cache_hits / (cache_hits + cache_misses) * 100
    logger.info(f"缓存统计 命中率={hit_rate:.2f}% 命中={cache_hits} 未命中={cache_misses}")


# ============ 示例 8: 在 FastAPI 路由中使用 ============

"""
# 在 FastAPI 应用中使用示例

from fastapi import APIRouter, Request, Depends
from app.utils.logs import getLogger, log_api_call
from app.utils.log_decorator import log_function_call

router = APIRouter()
logger = getLogger('user_api')

@router.post("/users")
@log_function_call(logger_name="user_api", log_args=True)
async def create_user_endpoint(
    username: str,
    email: str,
    request: Request
):
    # 记录 API 调用
    log_api_call(
        logger=logger,
        endpoint=request.url.path,
        method=request.method,
        params={"username": username, "email": email},
        response_status=201,
        client_ip=request.client.host
    )
    
    # 业务逻辑
    user = create_user(username, email)
    
    return user

@router.get("/users/{user_id}")
async def get_user_endpoint(user_id: int, request: Request):
    try:
        user = await async_get_user(user_id)
        
        log_api_call(
            logger=logger,
            endpoint=request.url.path,
            method=request.method,
            response_status=200,
            client_ip=request.client.host
        )
        
        return user
    except Exception as e:
        logger.error(f"获取用户失败 user_id={user_id} 错误={str(e)}")
        raise
"""


# ============ 运行所有示例 ============

if __name__ == "__main__":
    print("=== 运行日志示例 ===\n")
    
    print("1. 基础日志使用")
    example_basic_logging()
    
    print("\n2. 模块独立日志")
    example_module_logging()
    
    print("\n3. API 调用日志")
    example_api_logging()
    
    print("\n4. 函数调用日志")
    user = create_user("testuser", "test@example.com")
    print(f"创建用户结果: {user}")
    
    print("\n5. 异常日志记录")
    example_exception_logging()
    
    print("\n6. 业务日志记录")
    example_business_logging()
    
    print("\n7. 性能监控日志")
    example_performance_logging()
    
    print("\n=== 示例运行完成 ===")
    print("请查看 logs/ 目录下的日志文件")
