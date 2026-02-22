# 日志压缩服务快速开始

## 问题

在高并发环境下（WORKERS=4），原来的日志压缩任务会被4个Worker重复执行4次，浪费资源并影响性能。

## 解决方案

将日志压缩独立为单独的服务，与主服务分离。

## 快速开始

### 1. 启动所有服务（推荐）

```bash
bash force-rebuild-backend.sh
```

这会自动启动：
- Backend API (4 Workers)
- Queue Worker (16 并发)
- Log Compressor (独立服务) ✨

### 2. 查看日志压缩服务状态

```bash
# 查看服务状态
docker compose -f docker-compose.backend.yml ps log-compressor

# 查看实时日志
docker compose -f docker-compose.backend.yml logs -f log-compressor
```

### 3. 单独启动日志压缩服务

如果主服务已经在运行，只需添加日志压缩服务：

```bash
docker compose -f docker-compose.backend.yml up -d log-compressor
```

## 配置说明

在 `.env` 文件中：

```bash
# 日志压缩间隔（小时）
LOG_COMPRESS_INTERVAL_HOURS=2

# 启动时是否立即压缩
LOG_COMPRESS_ON_STARTUP=1

# 日志保留天数
LOG_RETENTION_DAYS=30

# 日志级别
LOG_LEVEL=WARNING
```

## 工作原理

```
之前：
主服务 (4 Workers)
├── Worker 1: API + 日志压缩 ❌
├── Worker 2: API + 日志压缩 ❌
├── Worker 3: API + 日志压缩 ❌
└── Worker 4: API + 日志压缩 ❌
问题：重复执行4次，浪费资源

现在：
主服务 (4 Workers)
├── Worker 1: 专注API ✅
├── Worker 2: 专注API ✅
├── Worker 3: 专注API ✅
└── Worker 4: 专注API ✅

日志压缩服务 (独立容器)
└── 专门处理日志压缩 ✅
优势：只执行1次，资源隔离
```

## 验证

启动后，查看日志确认服务正常运行：

```bash
docker compose -f docker-compose.backend.yml logs --tail=30 log-compressor
```

你应该看到类似输出：

```
============================================================
日志压缩服务启动中...
============================================================
配置信息:
  压缩间隔: 每 2 小时
  保留天数: 30 天
  日志目录: logs/
启动时执行首次压缩...
============================================================
开始执行日志压缩任务...
执行时间: 2026-02-22 10:30:00
...
日志压缩任务完成
============================================================
日志压缩服务已启动
```

## 常见问题

### Q: 主服务还会执行日志压缩吗？

A: 不会。已经从 `backend/app/main.py` 中完全移除了日志压缩相关代码。

### Q: 如何调整压缩频率？

A: 修改 `.env` 中的 `LOG_COMPRESS_INTERVAL_HOURS`，然后重启服务：

```bash
docker compose -f docker-compose.backend.yml restart log-compressor
```

### Q: 如何手动触发压缩？

A: 重启日志压缩服务（如果 `LOG_COMPRESS_ON_STARTUP=1`）：

```bash
docker compose -f docker-compose.backend.yml restart log-compressor
```

## 更多信息

详细文档请查看：[LOG_COMPRESSION_OPTIMIZATION.md](./LOG_COMPRESSION_OPTIMIZATION.md)
