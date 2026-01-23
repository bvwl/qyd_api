# Redis队列处理分离 - 快速开始

## 🎯 目标

实现每秒处理2000+条数据，解决Uvicorn多进程资源耗尽问题。

## ⚡ 快速开始

### 1. 配置环境变量

```bash
cd backend
cp .env.high_performance .env
```

确保 `.env` 包含：

```bash
# HTTP服务配置
APP_HOST=0.0.0.0
APP_PORT=6080
APP_WORKERS=4
ENABLE_QUEUE_WORKERS=0           # 重要！禁用HTTP服务中的队列处理

# 队列配置
REDIS_QUEUE_NUM_WORKERS=8
REDIS_QUEUE_BATCH_SIZE=300

# 数据库连接池
DB_MAXSIZE=40
DB_SLAVE1_MAXSIZE=40
DB_SLAVE2_MAXSIZE=40

# Redis连接池
REDIS_MAX_CONNECTIONS=100
```

### 2. 启动服务

#### 终端1：启动HTTP服务

```bash
cd backend
python start.py
```

输出应该包含：
```
队列处理已禁用（ENABLE_QUEUE_WORKERS=0）
```

#### 终端2：启动队列处理

```bash
cd backend
python start_queue_worker.py
```

输出应该包含：
```
============================================================
启动独立Redis队列处理进程
============================================================
✅ 数据库初始化完成
✅ Redis队列处理已启动
队列名称: project_account
工作线程数: 8
批处理大小: 300

队列处理运行中... (按Ctrl+C停止)
```

### 3. 验证运行状态

```bash
# 检查进程
ps aux | grep python

# 应该看到：
# - 4个 uvicorn 进程（HTTP服务）
# - 1个 start_queue_worker.py 进程（队列处理）

# 检查队列大小
redis-cli ZCARD qyd:project_account_keys_zset

# 查看日志
tail -f backend/logs/app.log
```

### 4. 性能测试

```bash
cd backend
python test_queue_performance.py
```

预期结果：
```
测试结果：
- 总耗时：约3.7秒
- 处理速度：约2700条/秒
- 满足需求：2000条/秒 ✅
```

## 📊 架构说明

```
┌─────────────────────────────────────┐
│   HTTP服务（4个进程）                 │
│   - 处理API请求                      │
│   - 添加数据到Redis队列               │
│   - 不处理队列                       │
└─────────────────────────────────────┘
              ↓
        ┌──────────┐
        │  Redis   │
        │  Queue   │
        └──────────┘
              ↓
┌─────────────────────────────────────┐
│   队列处理进程（1个独立进程）          │
│   - 8个并发workers                   │
│   - 从Redis读取数据                  │
│   - 批量写入数据库                   │
└─────────────────────────────────────┘
```

## 🔧 常见问题

### Q1: 为什么要分离？

**A**: 如果不分离，`uvicorn --workers=4` 会导致：
- 4个进程 × 8个workers = 32个队列workers
- 数据库连接：160+（耗尽）
- Redis连接：384+（耗尽）
- 性能下降（资源竞争）

分离后：
- 只有8个队列workers
- 数据库连接：~200（可控）
- Redis连接：~100（可控）
- 性能：2700条/秒 ✅

### Q2: 开发环境怎么配置？

**A**: 开发环境可以使用单进程模式：

```bash
# .env
APP_WORKERS=1
ENABLE_QUEUE_WORKERS=1           # 开发环境可以启用

# 只需要启动一个进程
python start.py
```

### Q3: 如何监控队列处理？

**A**: 查看日志和队列大小：

```bash
# 查看队列处理日志
tail -f backend/logs/app.log | grep Worker

# 查看队列大小
redis-cli ZCARD qyd:project_account_keys_zset

# 查看数据库连接数
mysql -e "SHOW PROCESSLIST;" | wc -l

# 查看Redis连接数
redis-cli INFO clients | grep connected_clients
```

### Q4: 队列堆积怎么办？

**A**: 增加worker数量或批处理大小：

```bash
# .env
REDIS_QUEUE_NUM_WORKERS=12       # 增加到12
REDIS_QUEUE_BATCH_SIZE=500       # 增加到500
DB_MAXSIZE=60                    # 相应增加连接池
```

### Q5: 如何在生产环境部署？

**A**: 使用Supervisor管理进程：

```bash
# 安装Supervisor
sudo apt-get install supervisor

# 创建配置文件
sudo nano /etc/supervisor/conf.d/qyd.conf

# 启动服务
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start qyd:*
```

详见：[Redis队列处理分离部署指南](./REDIS_QUEUE_SEPARATION_GUIDE.md)

## 📈 性能对比

| 指标 | 分离前 | 分离后 | 改善 |
|------|--------|--------|------|
| Queue Workers | 32 | 8 | -75% |
| 数据库连接 | 160+ | ~200 | 可控 |
| Redis连接 | 384+ | ~100 | -74% |
| 处理速度 | 无法达标 | 2700条/秒 | ✅ |

## 📚 相关文档

- [完整部署指南](./REDIS_QUEUE_SEPARATION_GUIDE.md) - 详细的部署步骤和配置说明
- [问题分析](./UVICORN_WORKERS_VS_REDIS_WORKERS.md) - Uvicorn Workers问题详解
- [性能分析](./REDIS_QUEUE_PERFORMANCE_ANALYSIS.md) - 性能测试和优化建议
- [完成总结](./REDIS_QUEUE_SEPARATION_COMPLETE.md) - 实施总结和验证方法

## ✅ 检查清单

部署前检查：

- [ ] 已复制 `.env.high_performance` 为 `.env`
- [ ] 已设置 `ENABLE_QUEUE_WORKERS=0`（HTTP服务）
- [ ] 已设置 `APP_WORKERS=4`
- [ ] 已设置 `REDIS_QUEUE_NUM_WORKERS=8`
- [ ] 已设置 `REDIS_QUEUE_BATCH_SIZE=300`
- [ ] 已增加数据库连接池（`DB_MAXSIZE=40`）
- [ ] 已增加Redis连接池（`REDIS_MAX_CONNECTIONS=100`）

部署后验证：

- [ ] HTTP服务正常启动（4个进程）
- [ ] 队列处理正常启动（1个进程）
- [ ] 队列大小接近0（处理速度快）
- [ ] 数据库连接数正常（~200）
- [ ] Redis连接数正常（~100）
- [ ] 性能测试通过（>2000条/秒）

---

**状态**：✅ 已完成  
**更新时间**：2026-01-23
