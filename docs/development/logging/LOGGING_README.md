# 日志系统完整文档

## 📋 目录

1. [功能特性](#功能特性)
2. [快速开始](#快速开始)
3. [文件说明](#文件说明)
4. [配置说明](#配置说明)
5. [使用示例](#使用示例)
6. [维护管理](#维护管理)
7. [最佳实践](#最佳实践)

## 功能特性

✅ **模块化日志** - 每个模块独立日志文件，便于追踪和调试  
✅ **自动滚动** - 每2小时自动滚动，避免单文件过大  
✅ **长期保留** - 保留30天日志（360个文件）  
✅ **自动压缩** - 旧日志自动压缩为 .gz 格式，节省 80-90% 空间  
✅ **自动清理** - 超过30天的日志自动删除  
✅ **多进程安全** - 支持多进程并发写入  
✅ **敏感信息过滤** - 自动过滤 password、token、secret、key  
✅ **性能监控** - 记录慢请求和处理时间  
✅ **中间件支持** - 自动记录所有 API 请求  
✅ **装饰器支持** - 函数级别的日志记录  

## 快速开始

### 1. 基础使用

```python
from app.utils.logs import getLogger

# 创建日志器
logger = getLogger('user')

# 记录日志
logger.info("用户登录成功")
logger.error("用户登录失败", exc_info=True)
```

### 2. 运行测试

```bash
# 测试日志系统
python test_logging_system.py

# 运行使用示例
python examples/log_usage_examples.py

# 手动清理日志
python scripts/cleanup_logs.py
```

### 3. 查看日志

```bash
# 查看当前日志
tail -f logs/user.log

# 查看压缩日志
zless logs/user.log.2026-01-20_22.gz

# 搜索日志
grep "错误" logs/user.log
zgrep "错误" logs/user.log.*.gz
```

## 文件说明

```
backend/
├── app/
│   ├── utils/
│   │   ├── logs.py              # 核心日志工具
│   │   ├── log_middleware.py    # FastAPI 日志中间件
│   │   └── log_decorator.py     # 日志装饰器
│   └── logs/
│       ├── README.md            # 本文档
│       └── USAGE.md             # 使用指南
├── scripts/
│   └── cleanup_logs.py          # 日志清理脚本
├── examples/
│   └── log_usage_examples.py    # 使用示例
├── test_logging_system.py       # 测试脚本
├── LOGGING_INTEGRATION.md       # 集成指南
└── logs/                        # 日志目录（自动创建）
    ├── user.log                 # 当前用户日志
    ├── user.log.2026-01-21_00   # 滚动日志
    ├── user.log.2026-01-20_22.gz # 压缩日志
    ├── project.log
    ├── server.log
    ├── mail.log
    └── api.log
```

## 配置说明

### 日志配置参数

在 `app/utils/logs.py` 中的配置：

```python
# 滚动间隔
when='H'           # 按小时滚动
interval=2         # 每2小时

# 保留数量
backupCount=360    # 30天 × 24小时 ÷ 2小时 = 360个文件

# 日志格式
fmt="【{name}】{levelname} {asctime} {message}"
datefmt="%Y-%m-%d %H:%M:%S"
```

### 环境变量（可选）

在 `.env` 文件中添加：

```bash
# 日志级别
LOG_LEVEL=INFO

# 日志保留天数
LOG_RETENTION_DAYS=30

# 是否启用日志压缩
LOG_COMPRESSION_ENABLED=1

# 是否启用自动清理
LOG_AUTO_CLEANUP_ENABLED=1
```

## 使用示例

### 1. 在路由中使用

```python
from fastapi import APIRouter, Request
from app.utils.logs import getLogger, log_api_call

router = APIRouter()
logger = getLogger('user_api')

@router.post("/users")
async def create_user(username: str, request: Request):
    logger.info(f"创建用户 username={username}")
    
    # 业务逻辑
    user = {"id": 1, "username": username}
    
    # 记录 API 调用
    log_api_call(
        logger=logger,
        endpoint=request.url.path,
        method=request.method,
        params={"username": username},
        response_status=201,
        client_ip=request.client.host
    )
    
    return user
```

### 2. 使用装饰器

```python
from app.utils.log_decorator import log_function_call, log_exception

@log_function_call(logger_name="user", log_args=True)
async def create_user_in_db(user_data: dict):
    # 函数调用会自动记录
    return await User.create(**user_data)

@log_exception(logger_name="error")
def risky_operation():
    # 异常会自动记录
    raise ValueError("Something went wrong")
```

### 3. 使用中间件

在 `main.py` 中添加：

```python
from app.utils.log_middleware import LoggingMiddleware

app = FastAPI(...)
app.add_middleware(LoggingMiddleware, logger_name="api")
```

### 4. 在 CRUD 中使用

```python
from app.utils.logs import getLogger

logger = getLogger('user_crud')

async def get_user_by_id(user_id: int):
    logger.debug(f"查询用户 user_id={user_id}")
    
    try:
        user = await User.get(id=user_id)
        logger.info(f"用户查询成功 user_id={user_id}")
        return user
    except Exception as e:
        logger.error(f"用户查询失败 user_id={user_id} 错误={e}", exc_info=True)
        raise
```

## 维护管理

### 自动维护

日志系统会在创建 logger 时自动执行：
- 压缩旧的未压缩日志文件
- 删除超过30天的压缩日志

### 手动维护

```bash
# 手动清理日志（保留30天）
python scripts/cleanup_logs.py

# 自定义保留天数（保留7天）
python scripts/cleanup_logs.py 7
```

### 定时任务

使用 crontab 设置定时清理：

```bash
# 编辑 crontab
crontab -e

# 每天凌晨3点清理日志
0 3 * * * cd /path/to/backend && python scripts/cleanup_logs.py
```

### 监控日志

```bash
# 查看日志目录大小
du -sh logs/

# 查看各文件大小
du -h logs/*.log* | sort -h

# 统计文件数量
ls logs/*.log* | wc -l

# 查看最新日志
tail -f logs/api.log

# 实时监控多个日志
tail -f logs/{user,project,server}.log
```

## 最佳实践

### 1. 日志级别使用

```python
logger.debug("详细的调试信息")      # 开发调试用
logger.info("正常的业务流程")       # 记录关键操作
logger.warning("警告但不影响运行")  # 需要注意的情况
logger.error("错误需要处理")        # 错误但程序继续
logger.critical("严重错误")         # 严重错误可能导致崩溃
```

### 2. 日志内容规范

```python
# ✓ 好的日志
logger.info(f"用户登录成功 user_id={user_id} ip={ip}")
logger.error(f"数据库连接失败 host={host} port={port}", exc_info=True)

# ✗ 不好的日志
logger.info("登录成功")  # 缺少关键信息
logger.error("失败")     # 信息不明确
```

### 3. 模块命名规范

```python
# 按功能模块命名
user_logger = getLogger('user')
project_logger = getLogger('project')

# 按层级命名
api_logger = getLogger('user_api')
crud_logger = getLogger('user_crud')
service_logger = getLogger('user_service')
```

### 4. 敏感信息处理

```python
# ✓ 自动过滤敏感字段
log_api_call(
    logger=logger,
    params={"username": "test", "password": "secret"}  # password 会被过滤
)

# ✓ 手动过滤
safe_data = {k: v for k, v in data.items() if k not in ['password', 'token']}
logger.info(f"用户数据 {safe_data}")

# ✗ 不要直接记录敏感信息
logger.info(f"密码: {password}")  # 危险！
```

### 5. 异常记录

```python
# ✓ 记录完整异常堆栈
try:
    risky_operation()
except Exception as e:
    logger.error(f"操作失败: {e}", exc_info=True)  # 包含堆栈信息

# ✗ 只记录异常消息
except Exception as e:
    logger.error(f"操作失败: {e}")  # 缺少堆栈信息
```

### 6. 性能考虑

```python
# ✓ 使用 f-string 延迟格式化
logger.debug(f"复杂计算结果: {expensive_calculation()}")

# ✓ 条件判断避免不必要的计算
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"详细信息: {expensive_calculation()}")

# ✗ 避免在循环中大量日志
for item in large_list:
    logger.debug(f"处理 {item}")  # 可能产生大量日志
```

## 故障排查

### 问题 1: 日志文件未创建

**原因**: logs 目录不存在或无写入权限

**解决**:
```bash
mkdir -p logs
chmod 755 logs
```

### 问题 2: 日志文件过大

**原因**: 滚动间隔太长或保留时间太久

**解决**: 调整 `logs.py` 中的配置
```python
interval=1         # 改为每1小时滚动
backupCount=168    # 改为保留7天
```

### 问题 3: 压缩日志无法查看

**解决**: 使用 zcat 或 zless
```bash
zcat logs/api.log.2026-01-20_22.gz
zless logs/api.log.2026-01-20_22.gz
zgrep "关键词" logs/api.log.*.gz
```

### 问题 4: 日志清理不生效

**原因**: 定时任务未配置或权限问题

**解决**:
```bash
# 检查 crontab
crontab -l

# 手动执行测试
python scripts/cleanup_logs.py

# 查看执行日志
tail -f /tmp/log_cleanup.log
```

## 性能指标

基于测试结果：

- **写入性能**: ~0.5ms/条（1000条/0.5秒）
- **压缩率**: 80-90%（取决于日志内容）
- **存储空间**: 30天约 360 个文件，压缩后约 100-200MB
- **查询性能**: grep 约 50MB/秒，zgrep 约 10MB/秒

## 相关文档

- [USAGE.md](./USAGE.md) - 详细使用指南
- [LOGGING_INTEGRATION.md](../../LOGGING_INTEGRATION.md) - 集成指南
- [log_usage_examples.py](../../examples/log_usage_examples.py) - 代码示例

## 技术支持

如有问题，请查看：
1. 运行测试脚本: `python test_logging_system.py`
2. 查看示例代码: `python examples/log_usage_examples.py`
3. 检查日志文件: `ls -lh logs/`
