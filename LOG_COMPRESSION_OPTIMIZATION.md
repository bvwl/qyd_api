# 日志压缩服务优化方案

## 问题背景

在高并发环境下，原有的日志压缩方案存在以下问题：

1. **多Worker重复执行**：主服务配置了4个Worker，每个Worker都会启动调度器，导致日志压缩任务重复执行4次
2. **影响主服务性能**：日志压缩是CPU密集型操作，在主服务中执行会影响API响应性能
3. **资源竞争**：多个进程同时压缩日志可能导致文件锁冲突

## 解决方案

### 1. 独立日志压缩服务

创建独立的日志压缩服务 `start_log_compressor.py`，专门负责日志压缩任务：

```python
# backend/start_log_compressor.py
- 每2小时自动压缩旧日志
- 删除超过7天的压缩日志
- 按日期组织日志目录结构
- 支持优雅关闭
```

**优势**：
- 单独运行，不影响主服务性能
- 避免多Worker重复执行
- 资源隔离，便于监控和调试

### 2. 主服务禁用日志压缩

修改 `backend/app/main.py`，默认禁用主服务的日志压缩：

```python
# 通过环境变量控制
ENABLE_LOG_COMPRESSION=0  # 默认禁用
```

### 3. Docker Compose 配置

在 `docker-compose.backend.yml` 中添加日志压缩服务：

```yaml
services:
  log-compressor:
    build:
      context: ./backend
      target: log-compressor
    container_name: qyd-log-compressor
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs  # 共享日志目录
```

### 4. Dockerfile 多阶段构建

添加日志压缩服务的构建目标：

```dockerfile
FROM backend-base as log-compressor
COPY app/utils/logs.py app/utils/logs.py
COPY start_log_compressor.py .
CMD ["python", "start_log_compressor.py"]
```

## 使用方式

### 使用现有启动脚本（推荐）

```bash
bash force-rebuild-backend.sh
```

这个脚本会自动启动：
- Backend API (4 Workers)
- Queue Worker (16 并发)
- Log Compressor (独立服务)

### 手动启动

```bash
# 启动所有服务
docker compose -f docker-compose.backend.yml up -d backend-api queue-worker log-compressor

# 查看日志压缩服务状态
docker compose -f docker-compose.backend.yml logs -f log-compressor
```

### 仅启动日志压缩服务

```bash
# 如果主服务已经在运行，只需添加日志压缩服务
docker compose -f docker-compose.backend.yml up -d log-compressor
```

## 环境变量配置

在 `.env` 文件中配置：

```bash
# 日志压缩间隔（小时）- 用于独立服务
LOG_COMPRESS_INTERVAL_HOURS=2

# 启动时是否立即压缩
LOG_COMPRESS_ON_STARTUP=1

# 日志保留天数
LOG_RETENTION_DAYS=30

# 日志级别（高并发场景建议使用WARNING）
LOG_LEVEL=WARNING
```

注意：不再需要 `ENABLE_LOG_COMPRESSION` 环境变量，因为主服务已经完全移除了日志压缩代码。

## 性能对比

### 优化前

```
主服务 (4 Workers)
├── Worker 1: API处理 + 日志压缩 ❌
├── Worker 2: API处理 + 日志压缩 ❌
├── Worker 3: API处理 + 日志压缩 ❌
└── Worker 4: API处理 + 日志压缩 ❌

问题：
- 日志压缩任务执行4次（重复）
- 每个Worker都要处理压缩任务
- 影响API响应性能
- 浪费CPU和磁盘I/O资源
```

### 优化后

```
主服务 (4 Workers)
├── Worker 1: 专注API处理 ✅
├── Worker 2: 专注API处理 ✅
├── Worker 3: 专注API处理 ✅
└── Worker 4: 专注API处理 ✅

日志压缩服务 (独立容器)
└── 专门处理日志压缩 ✅

优势：
- 日志压缩只执行1次
- 主服务专注API处理
- 性能提升，资源隔离
- 代码更简洁，易于维护
```

## 监控和调试

### 查看日志压缩服务状态

```bash
# 查看服务状态
docker compose -f docker-compose.backend.yml ps log-compressor

# 查看实时日志
docker compose -f docker-compose.backend.yml logs -f log-compressor

# 查看最近的压缩记录
docker compose -f docker-compose.backend.yml logs --tail=50 log-compressor
```

### 手动触发压缩

```bash
# 进入容器手动执行
docker compose -f docker-compose.backend.yml exec log-compressor python -c "
from app.utils.logs import compress_all_logs
compress_all_logs()
"
```

### 查看日志统计

```bash
# 查看日志文件统计信息
docker compose -f docker-compose.backend.yml exec log-compressor python -c "
from app.utils.logs import get_log_statistics
import json
stats = get_log_statistics()
print(json.dumps(stats, indent=2, ensure_ascii=False))
"
```

## 日志目录结构

压缩后的日志按以下结构组织：

```
logs/
├── api/                    # API日志
│   ├── api.log            # 当前日志
│   └── 2026/              # 按年份
│       └── 02/            # 按月份
│           └── 22/        # 按日期
│               ├── api.log.1.gz
│               └── api.log.2.gz
├── app/                    # 应用日志
│   ├── app.log
│   └── 2026/02/22/
├── database/               # 数据库日志
│   ├── database.log
│   └── 2026/02/22/
└── scheduler/              # 调度器日志
    ├── scheduler.log
    └── 2026/02/22/
```

## 故障排查

### 问题1：日志压缩服务无法启动

**检查**：
```bash
docker compose -f docker-compose.backend.yml logs log-compressor
```

**可能原因**：
- 日志目录权限问题
- 环境变量配置错误
- 依赖包缺失

**解决**：
```bash
# 重新构建镜像
docker compose -f docker-compose.backend.yml build --no-cache log-compressor

# 重启服务
docker compose -f docker-compose.backend.yml restart log-compressor
```

### 问题2：日志没有被压缩

**检查**：
```bash
# 查看服务是否运行
docker compose -f docker-compose.backend.yml ps log-compressor

# 查看日志输出
docker compose -f docker-compose.backend.yml logs --tail=100 log-compressor
```

**可能原因**：
- 服务未启动
- 压缩间隔未到
- 没有需要压缩的日志文件

### 问题3：磁盘空间不足

**检查**：
```bash
# 查看日志目录大小
du -sh logs/

# 查看各模块日志大小
du -sh logs/*/
```

**解决**：
```bash
# 手动清理旧日志（超过30天）
find logs/ -name "*.log.*.gz" -mtime +30 -delete

# 或者调整保留天数
# 修改 .env 中的 LOG_RETENTION_DAYS
```

## 最佳实践

### 1. 高并发环境配置

```bash
# .env 配置
WORKERS=4                           # 4个API Worker
REDIS_QUEUE_NUM_WORKERS=16          # 16个队列Worker
LOG_LEVEL=WARNING                   # 减少日志量
LOG_RETENTION_DAYS=7                # 只保留7天
LOG_COMPRESS_INTERVAL_HOURS=1       # 每小时压缩一次
```

### 2. 开发环境配置

```bash
# .env 配置
WORKERS=1                           # 1个Worker
LOG_LEVEL=DEBUG                     # 详细日志
LOG_RETENTION_DAYS=30               # 保留30天
LOG_COMPRESS_INTERVAL_HOURS=24      # 每天压缩一次
ENABLE_LOG_COMPRESSION=1            # 可以在主服务中启用
```

### 3. 监控告警

建议监控以下指标：
- 日志目录总大小
- 压缩任务执行时间
- 压缩失败次数
- 磁盘使用率

## 总结

通过将日志压缩服务独立出来，我们实现了：

✅ **性能提升**：主服务专注API处理，不受日志压缩影响  
✅ **避免重复**：日志压缩只执行一次，不会因多Worker重复  
✅ **资源隔离**：独立容器，便于监控和调试  
✅ **灵活配置**：可以独立调整压缩策略，不影响主服务  
✅ **高可用性**：服务故障互不影响，提高系统稳定性  

这个方案特别适合高并发环境，能够显著提升系统性能和稳定性。
