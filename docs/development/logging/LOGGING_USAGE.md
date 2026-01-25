# 日志工具使用指南

## 功能特性

- ✅ 每个模块独立日志文件
- ✅ 每2小时自动滚动日志
- ✅ 保留30天日志（360个文件）
- ✅ 自动压缩旧日志为 .gz 格式
- ✅ 自动清理超过30天的压缩日志
- ✅ 多进程安全写入
- ✅ 敏感信息过滤（password, token, secret, key）

## 基础使用

### 1. 在不同模块中创建独立日志

```python
from app.utils.logs import getLogger

# 用户模块日志
user_logger = getLogger('user')
user_logger.info("用户登录成功")

# 项目模块日志
project_logger = getLogger('project')
project_logger.info("创建新项目")

# 服务器模块日志
server_logger = getLogger('server')
server_logger.info("服务器状态检查")

# 邮件模块日志
mail_logger = getLogger('mail')
mail_logger.info("发送邮件")
```

### 2. 记录API调用

```python
from app.utils.logs import getLogger, log_api_call

logger = getLogger('api')

# 记录完整的API调用信息
log_api_call(
    logger=logger,
    user_id="user123",
    endpoint="/api/v1/users/info",
    method="GET",
    params={"id": 123},
    response_status=200,
    client_ip="192.168.1.100"
)
```

### 3. 在FastAPI路由中使用

```python
from fastapi import APIRouter, Request
from app.utils.logs import getLogger, log_api_call

router = APIRouter()
logger = getLogger('user_api')

@router.get("/users/{user_id}")
async def get_user(user_id: int, request: Request):
    log_api_call(
        logger=logger,
        user_id=str(user_id),
        endpoint=request.url.path,
        method=request.method,
        params=dict(request.query_params),
        response_status=200,
        client_ip=request.client.host
    )
    return {"user_id": user_id}
```

## 日志文件结构

```
logs/
├── user.log              # 当前用户模块日志
├── user.log.2026-01-21_00  # 历史日志（未压缩）
├── user.log.2026-01-20_22.gz  # 压缩的历史日志
├── project.log           # 当前项目模块日志
├── project.log.2026-01-21_00.gz
├── server.log            # 当前服务器模块日志
├── mail.log              # 当前邮件模块日志
└── api.log               # 当前API日志
```

## 日志格式

### 控制台输出
```
INFO 2026-01-21 15:30:45 系统启动
```

### 文件输出
```
【user】INFO 2026-01-21 15:30:45 用户=user123 IP=192.168.1.100 GET /api/v1/users/info 参数={'id': 123} 状态码=200
```

## 日志级别

```python
logger.debug("调试信息")      # DEBUG
logger.info("普通信息")       # INFO
logger.warning("警告信息")    # WARNING
logger.error("错误信息")      # ERROR
logger.critical("严重错误")   # CRITICAL
```

## 手动维护

### 手动压缩日志
```python
from app.utils.logs import compress_old_logs

compress_old_logs(log_dir="logs", name="user")
```

### 手动清理旧日志
```python
from app.utils.logs import delete_old_compressed_logs

# 删除超过30天的压缩日志
delete_old_compressed_logs(log_dir="logs", days=30)
```

## 注意事项

1. **自动维护**：每次创建新的 logger 时会自动压缩和清理旧日志
2. **敏感信息**：password、token、secret、key 等字段会自动过滤
3. **单例模式**：相同名称的 logger 只会创建一次
4. **多进程安全**：使用 TimedRotatingFileHandler 支持多进程写入
5. **存储空间**：30天 × 12个文件/天 = 360个文件，压缩后约占原大小的10-20%
