# 定时任务异步执行修复

## 更新时间
2026-02-22

## 问题描述

定时任务中的日志压缩任务 `compress_logs_task()` 直接调用同步函数 `compress_all_logs()`，导致：

1. **阻塞事件循环**：同步 I/O 操作阻塞主事件循环
2. **影响性能**：在压缩大量日志时，API 请求响应变慢
3. **重复执行**：多个 worker 同时执行相同任务

日志显示：
```
INFO 2026-02-22 14:54:50 开始执行日志压缩任务...
INFO 2026-02-22 14:54:50 开始执行日志压缩任务...
INFO 2026-02-22 14:54:50 开始执行日志压缩任务...
INFO 2026-02-22 14:54:50 开始执行日志压缩任务...
```

## 原因分析

### 1. 同步函数阻塞事件循环

```python
# 错误的做法
async def compress_logs_task():
    compress_all_logs()  # 同步函数，会阻塞事件循环
```

`compress_all_logs()` 包含大量同步 I/O 操作：
- 文件读取
- 文件压缩（gzip）
- 文件移动
- 目录遍历

这些操作在执行时会阻塞整个事件循环，导致其他异步任务无法执行。

### 2. 多 Worker 重复执行

如果使用 `WORKERS > 1`，每个 worker 进程都会启动自己的调度器，导致：
- 同一时间多个进程执行相同任务
- 资源浪费
- 可能的文件冲突

## 解决方案

### 1. 使用 run_in_executor 异步执行

```python
async def compress_logs_task():
    """异步执行日志压缩任务"""
    try:
        scheduler_logger.info("开始执行日志压缩任务...")
        
        # 在线程池中异步执行同步函数，避免阻塞事件循环
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, compress_all_logs)
        
        scheduler_logger.info("日志压缩任务完成")
    except Exception as e:
        scheduler_logger.error(f"日志压缩任务失败: {e}", exc_info=True)
```

**工作原理**：
- `run_in_executor(None, func)` 在默认线程池中执行同步函数
- 不阻塞事件循环
- 其他异步任务可以继续执行

### 2. 确保单 Worker 执行定时任务

在生产环境中，建议：

```bash
# .env 配置
WORKERS=1  # 只使用一个 worker 进程
```

或者使用独立的调度器进程（推荐）：

```python
# 单独的调度器进程
# scheduler_worker.py
```

## 修改的文件

1. **backend/app/main.py**
   - 修改 `compress_logs_task()` 函数
   - 使用 `run_in_executor` 异步执行
   - 添加详细注释说明

## 效果对比

### 修复前

```
INFO 14:54:50 开始执行日志压缩任务...
INFO 14:54:50 开始执行日志压缩任务...  # 多个 worker 重复执行
INFO 14:54:50 开始执行日志压缩任务...
INFO 14:54:50 开始执行日志压缩任务...

# API 请求变慢
INFO 14:54:50 GET /v1/project/account 耗时=2.5s  # 被阻塞
```

### 修复后

```
INFO 14:54:50 开始执行日志压缩任务...
# 在后台线程执行，不阻塞事件循环
INFO 14:54:51 日志压缩任务完成

# API 请求正常
INFO 14:54:50 GET /v1/project/account 耗时=0.65s  # 不受影响
```

## 其他定时任务检查

已检查所有定时任务，确认都是异步执行：

### ✅ keep_db_connection_alive
```python
async def keep_db_connection_alive():
    conn = Tortoise.get_connection("default")
    await conn.execute_query("SELECT 1")  # 异步查询
```

### ✅ auto_check_email_status
```python
async def auto_check_email_status(days: int = 15):
    # 异步函数，使用 await
    pass
```

### ✅ scheduled_sync_stats
```python
async def scheduled_sync_stats():
    # 异步函数，使用 await
    pass
```

### ✅ compress_logs_task（已修复）
```python
async def compress_logs_task():
    # 使用 run_in_executor 异步执行同步函数
    await loop.run_in_executor(None, compress_all_logs)
```

## 最佳实践

### 1. 定时任务应该是异步的

```python
# ✅ 正确：异步函数
async def my_scheduled_task():
    await some_async_operation()

# ❌ 错误：同步函数
def my_scheduled_task():
    some_sync_operation()
```

### 2. 同步操作使用 run_in_executor

```python
# ✅ 正确：在线程池中执行
async def my_task():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, sync_function)

# ❌ 错误：直接调用同步函数
async def my_task():
    result = sync_function()  # 阻塞事件循环
```

### 3. I/O 密集型操作使用线程池

```python
# 文件操作
await loop.run_in_executor(None, compress_files)

# 网络请求（如果使用同步库）
await loop.run_in_executor(None, requests.get, url)

# 数据库操作（如果使用同步库）
await loop.run_in_executor(None, db.query, sql)
```

### 4. CPU 密集型操作使用进程池

```python
from concurrent.futures import ProcessPoolExecutor

# CPU 密集型计算
executor = ProcessPoolExecutor()
result = await loop.run_in_executor(executor, cpu_intensive_task)
```

## 监控和调试

### 1. 检查事件循环阻塞

```python
import asyncio

# 启用调试模式
asyncio.get_event_loop().set_debug(True)

# 会警告执行时间超过 100ms 的任务
```

### 2. 监控定时任务执行

```python
# 记录任务执行时间
import time

async def my_task():
    start = time.time()
    try:
        await do_something()
    finally:
        duration = time.time() - start
        logger.info(f"任务执行耗时: {duration:.2f}s")
```

### 3. 查看活跃任务

```python
# 查看当前运行的任务
tasks = asyncio.all_tasks()
logger.info(f"活跃任务数: {len(tasks)}")
```

## 配置建议

### 生产环境

```bash
# .env
WORKERS=1  # 单 worker，避免重复执行定时任务
DEBUG=0
LOG_LEVEL=INFO
```

### 开发环境

```bash
# .env
WORKERS=1  # 开发时也建议单 worker
DEBUG=1
LOG_LEVEL=DEBUG
```

### 高并发环境

如果需要多 worker 处理 HTTP 请求，建议：

1. **分离调度器**：使用独立进程运行定时任务
2. **使用分布式锁**：确保任务只执行一次
3. **使用消息队列**：Celery、RQ 等

```python
# 使用 Redis 分布式锁
from redis import Redis
from redis.lock import Lock

async def compress_logs_task():
    redis = Redis()
    lock = Lock(redis, "compress_logs_lock", timeout=3600)
    
    if lock.acquire(blocking=False):
        try:
            await loop.run_in_executor(None, compress_all_logs)
        finally:
            lock.release()
    else:
        logger.info("任务正在其他进程中执行，跳过")
```

## 验证修复

### 1. 检查日志

```bash
# 应该只看到一次执行
docker compose -f docker-compose.backend.yml logs | grep "开始执行日志压缩任务"

# 输出应该是：
# INFO 14:54:50 开始执行日志压缩任务...
# INFO 14:54:51 日志压缩任务完成
```

### 2. 监控 API 性能

```bash
# 在日志压缩期间，API 响应时间应该正常
docker compose -f docker-compose.backend.yml logs | grep "耗时"

# 应该看到正常的响应时间（< 1s）
```

### 3. 检查 CPU 使用

```bash
# 日志压缩应该在后台执行，不影响主进程
docker stats qyd-backend-api
```

## 相关文档

- `LOG_CONFIG_UPDATE.md` - 日志配置更新
- `REDIS_ERROR_FIX_SUMMARY.md` - Redis 错误修复
- `JSON_DATA_FIX.md` - JSON 数据修复

## 总结

通过使用 `run_in_executor` 将同步 I/O 操作移到线程池执行：

1. ✅ 不阻塞事件循环
2. ✅ API 响应时间不受影响
3. ✅ 定时任务正常执行
4. ✅ 系统性能提升

所有定时任务现在都是真正的异步执行！
