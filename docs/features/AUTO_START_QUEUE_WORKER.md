# Redis 队列处理启动指南

## 🎯 功能说明

Redis 队列处理需要独立启动，用于异步处理批量数据操作。

## ✅ 启动方法

### 方式1：前台运行（开发环境）

```bash
cd backend
python start_queue_worker.py
```

### 方式2：后台运行（生产环境）

```bash
cd backend
nohup python start_queue_worker.py > logs/queue_worker.log 2>&1 &
```

### 方式3：使用 screen/tmux

```bash
# 使用 screen
screen -S queue_worker
cd backend
python start_queue_worker.py
# 按 Ctrl+A, D 分离会话

# 使用 tmux
tmux new -s queue_worker
cd backend
python start_queue_worker.py
# 按 Ctrl+B, D 分离会话
```

## 🔍 验证运行状态

### 检查进程

```bash
# 查看队列处理进程
ps aux | grep start_queue_worker

# 应该看到：
# python start_queue_worker.py
```

### 检查队列处理

```bash
# 查看队列大小
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ ZCARD qyd:project_account_keys_zset

# 查看处理日志
tail -f backend/logs/app.log | grep Worker
```

### 测试队列功能

```bash
# 添加数据到队列
curl -X POST 'http://127.0.0.1:6080/v1/project/account/upsert' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "account": "test_user",
    "balance": 100,
    "project_id": "xxx"
  }'

# 查看队列大小（应该很快变为0）
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ ZCARD qyd:project_account_keys_zset
```

## 🛑 停止服务

### 停止队列处理

```bash
# 查找进程ID
ps aux | grep start_queue_worker

# 停止进程
kill <PID>

# 或强制停止
pkill -f "start_queue_worker"
```

## ⚠️ 注意事项

### 1. 独立启动

队列处理需要独立启动，不会随后端服务自动启动。

### 2. 日志位置

- HTTP 服务日志：`backend/logs/api.log`
- 队列处理日志：`backend/logs/app.log`

### 3. 重启服务

重启后端服务时，需要手动重启队列处理进程。

## 🎯 使用场景

### 场景1：本地开发

```bash
# 终端1：启动后端
cd backend
python start.py

# 终端2：启动队列处理
cd backend
python start_queue_worker.py
```

### 场景2：生产环境（后台运行）

```bash
# 启动后端
cd backend
nohup python start.py > logs/http.log 2>&1 &

# 启动队列处理
nohup python start_queue_worker.py > logs/queue.log 2>&1 &
```

### 场景3：使用 Supervisor 管理

```ini
# /etc/supervisor/conf.d/qyd.conf
[program:qyd_http]
command=/path/to/python /path/to/backend/start.py
directory=/path/to/backend
autostart=true
autorestart=true
stdout_logfile=/path/to/backend/logs/http.log
stderr_logfile=/path/to/backend/logs/http_error.log

[program:qyd_queue]
command=/path/to/python /path/to/backend/start_queue_worker.py
directory=/path/to/backend
autostart=true
autorestart=true
stdout_logfile=/path/to/backend/logs/queue.log
stderr_logfile=/path/to/backend/logs/queue_error.log
```

## 📊 性能表现

### 单队列进程

| 指标 | 值 |
|------|-----|
| 队列进程 | 1 |
| Workers | 4 |
| 批处理大小 | 200 |
| 处理延迟 | < 1秒 |
| 吞吐量 | 2000-3000条/秒 |

### 多队列进程（高性能）

| 指标 | 值 |
|------|-----|
| 队列进程 | 3 |
| Workers | 12 |
| 批处理大小 | 200 |
| 处理延迟 | < 0.5秒 |
| 吞吐量 | 12000-15000条/秒 |

## 🔗 相关文档

- [队列分离快速开始](docs/performance/QUEUE_SEPARATION_QUICK_START.md)
- [扩展到10000+条/秒](docs/performance/SCALE_TO_10K_GUIDE.md)
- [性能快速参考](docs/performance/PERFORMANCE_QUICK_REFERENCE.md)
- [Upsert接口修复](UPSERT_REDIS_QUEUE_UPDATE.md)

## 📅 更新信息

- **更新时间**：2026-01-23
- **功能**：Redis 队列处理（手动启动）
- **适用版本**：v1.0.0+

---

**推荐**：生产环境使用独立进程，便于监控和管理
