# 定时任务重复执行问题修复

## 问题描述

从日志中发现定时任务重复执行了 4 次：

```
INFO 2026-02-22 14:54:50 开始执行日志压缩任务...
INFO 2026-02-22 14:54:50 开始执行日志压缩任务...
INFO 2026-02-22 14:54:50 开始执行日志压缩任务...
INFO 2026-02-22 14:54:50 开始执行日志压缩任务...
```

## 原因分析

这是因为 **uvicorn 启动了多个 worker 进程**，每个 worker 进程都会独立执行定时任务，导致：

1. 日志压缩任务重复执行
2. 数据库连接检查重复执行
3. 其他定时任务（邮箱检查、统计同步）也会重复执行
4. 浪费系统资源，可能导致竞争条件

## 检查当前配置

运行以下命令检查实际的 WORKERS 配置：

```bash
# 1. 检查 .env 文件
grep "^WORKERS=" .env

# 2. 检查容器中的环境变量
docker compose -f docker-compose.backend.yml exec backend-api printenv | grep WORKERS

# 3. 检查实际运行的进程数
docker compose -f docker-compose.backend.yml exec backend-api ps aux | grep uvicorn
```

或者使用提供的诊断脚本：

```bash
bash check-workers.sh
```

## 解决方案

### 方案 1：确保 WORKERS=1（推荐）

**适用场景**：生产环境，需要定时任务正常运行

1. 确认 `.env` 文件中的配置：

```bash
# 确保这一行存在且值为 1
WORKERS=1
```

2. 重新构建并启动服务：

```bash
bash force-rebuild-backend.sh
```

3. 验证配置生效：

```bash
# 应该只看到 1 个 uvicorn worker 进程
docker compose -f docker-compose.backend.yml exec backend-api ps aux | grep uvicorn
```

### 方案 2：禁用定时任务（如果需要多 worker）

**适用场景**：需要高并发处理，但不需要定时任务

如果你确实需要多个 worker 来处理高并发请求，可以禁用定时任务：

1. 修改 `.env` 文件：

```bash
# 设置多个 worker
WORKERS=4

# 禁用定时任务
ENABLE_EMAIL_CHECK=0
ENABLE_STATS_SYNC=0
```

2. 修改 `backend/app/main.py`，在 `lifespan` 函数中添加检查：

```python
# 只在主进程中启动定时任务
import multiprocessing
if multiprocessing.current_process().name == 'MainProcess':
    # 启动定时任务
    scheduler.start()
else:
    app_logger.info("Worker 进程，跳过定时任务启动")
```

但是这个方案**不推荐**，因为：
- 定时任务是系统的重要功能
- 多 worker 模式下定时任务管理复杂
- 可能导致任务遗漏或重复执行

### 方案 3：使用外部调度器（企业级方案）

**适用场景**：大规模生产环境

将定时任务从应用中分离出来，使用专门的调度系统：

1. 使用 Celery Beat 或 APScheduler 独立进程
2. 使用 Kubernetes CronJob
3. 使用系统 cron + API 调用

## 推荐配置

### 单机部署（当前场景）

```bash
# .env 配置
WORKERS=1  # 单 worker，定时任务正常运行
```

**优点**：
- 定时任务不会重复执行
- 配置简单，易于维护
- 适合中小规模应用

**性能**：
- 单 worker 可以处理 1000+ 并发请求
- 配合异步 I/O，性能已经很好
- 如需更高性能，使用方案 4

### 高并发场景

如果确实需要更高的并发处理能力，推荐使用 **容器扩展** 而不是多 worker：

```bash
# 保持 WORKERS=1
WORKERS=1

# 通过 Docker Compose 扩展容器实例
docker compose -f docker-compose.backend.yml up -d --scale backend-api=3

# 配置 Nginx 负载均衡
```

**优点**：
- 每个容器只有 1 个 worker，定时任务不重复
- 通过负载均衡实现高并发
- 容器间隔离，更稳定
- 可以独立重启、更新

## 验证修复

修复后，检查日志应该只看到一次任务执行：

```bash
# 查看日志
docker compose -f docker-compose.backend.yml logs -f backend-api | grep "开始执行日志压缩任务"

# 应该只看到一行：
# INFO 2026-02-22 15:00:00 开始执行日志压缩任务...
```

## 相关文件

- `backend/app/main.py` - 定时任务配置
- `backend/start.py` - uvicorn 启动配置
- `.env` - 环境变量配置
- `docker-compose.backend.yml` - Docker 配置
- `SCHEDULED_TASKS_AUDIT.md` - 定时任务审计报告

## 总结

1. **生产环境推荐使用 `WORKERS=1`**
2. 定时任务会在每个 worker 进程中独立执行
3. 如需高并发，使用容器扩展而不是多 worker
4. 确保 `.env` 文件中 `WORKERS=1` 配置生效
