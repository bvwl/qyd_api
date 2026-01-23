# Redis 队列处理 - 手动启动模式

## 📋 变更说明

已将 Redis 队列处理改为**手动启动模式**，不再随后端服务自动启动。

## ✅ 启动方式

### 方式1：直接启动（推荐用于开发）

```bash
cd backend
python start_queue_worker.py
```

### 方式2：使用启动脚本

```bash
./start_queue_processing.sh
```

### 方式3：后台运行（推荐用于生产）

```bash
cd backend
nohup python start_queue_worker.py > logs/queue_worker.log 2>&1 &
```

## 🔧 配置变更

### 移除的配置

从 `.env` 和 `.env.example` 中移除了：

```bash
# 已移除
AUTO_START_QUEUE_WORKER=1
```

### 启动提示

现在启动后端时会显示：

```
2026-01-23 17:30:00 - root - INFO - 启动服务: 0.0.0.0:6080
2026-01-23 17:30:00 - root - INFO - 调试模式: False
2026-01-23 17:30:00 - root - INFO - 工作进程: 1
2026-01-23 17:30:00 - root - INFO - 提示: 如需队列处理，请手动运行: python start_queue_worker.py
```

## 📊 完整的启动流程

### 开发环境

```bash
# 终端1：启动后端
cd backend
python start.py

# 终端2：启动队列处理
cd backend
python start_queue_worker.py
```

### 生产环境

```bash
# 1. 启动后端（后台）
cd backend
nohup python start.py > logs/http.log 2>&1 &

# 2. 启动队列处理（后台）
nohup python start_queue_worker.py > logs/queue.log 2>&1 &

# 3. 查看进程
ps aux | grep python

# 4. 查看日志
tail -f logs/app.log | grep Worker
```

## 🐛 已修复的问题

### 1. Upsert 重复记录问题

**问题**：相同的 `account` 和 `project_id` 创建了多条记录

**原因**：UUID vs 字符串类型不匹配

**修复**：统一转为字符串进行比较

**详细文档**：[UPSERT_DUPLICATE_FIX.md](docs/fixes/UPSERT_DUPLICATE_FIX.md)

### 2. 日志记录问题

**问题**：队列处理日志不输出

**原因**：使用了 `loguru.logger` 而不是自定义 logger

**修复**：改用 `getLogger('app')`

### 3. Redis 连接问题

**问题**：连接到错误的 Redis 端口（6379 而不是 6378）

**原因**：环境变量加载顺序错误

**修复**：在导入 settings 之前加载 .env 文件

### 4. 数据库查询问题

**问题**：`'str' object has no attribute 'executor_class'`

**原因**：`using_db()` 使用不当

**修复**：使用 `Tortoise.get_connection()`

## 📝 修改的文件

1. `backend/start.py` - 移除自动启动逻辑
2. `backend/.env` - 移除 AUTO_START_QUEUE_WORKER 配置
3. `backend/.env.example` - 移除 AUTO_START_QUEUE_WORKER 配置
4. `backend/app/utils/redis_queue.py` - 修复类型匹配问题
5. `backend/start_queue_worker.py` - 修复环境变量加载
6. `AUTO_START_QUEUE_WORKER.md` - 更新为手动启动文档
7. `start_queue_processing.sh` - 新增启动脚本

## 🎯 使用建议

### 开发环境

- 使用两个终端分别运行后端和队列处理
- 便于查看日志和调试

### 生产环境

- 使用 `nohup` 后台运行
- 或使用 Supervisor/systemd 管理进程
- 配置自动重启和日志轮转

## 🔗 相关文档

- [Redis 队列处理启动指南](AUTO_START_QUEUE_WORKER.md)
- [Upsert 重复记录修复](docs/fixes/UPSERT_DUPLICATE_FIX.md)
- [队列处理完成文档](docs/fixes/QUEUE_WORKER_AUTO_START_COMPLETE.md)
- [Upsert Redis 队列更新](UPSERT_REDIS_QUEUE_UPDATE.md)

## 📅 更新信息

- **更新时间**：2026-01-23
- **变更**：改为手动启动模式
- **原因**：用户需要独立控制队列处理进程
- **状态**：✅ 已完成

---

**重要提示**：启动后端后，记得手动启动队列处理进程，否则数据会堆积在 Redis 中不被处理。
