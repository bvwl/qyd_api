# Queue Worker 未启动问题修复

## 问题描述

运行 `force-rebuild-backend.sh` 后，`queue-worker` 服务没有启动。

## 原因分析

原来的 `force-rebuild-backend.sh` 脚本只处理了 `backend-api` 服务，没有包含 `queue-worker` 服务的重建和启动。

## 解决方案

### 方案1：使用修复后的脚本（推荐）

已更新 `force-rebuild-backend.sh` 脚本，现在会同时处理两个服务：

```bash
# 在服务器上运行
bash force-rebuild-backend.sh
```

脚本会：
1. 停止 `backend-api` 和 `queue-worker`
2. 删除旧镜像
3. 重新构建两个服务
4. 启动两个服务
5. 显示服务状态和日志

### 方案2：单独重启 Queue Worker

如果只需要重启 `queue-worker`：

```bash
# 在服务器上运行
bash restart-queue-worker.sh
```

### 方案3：手动操作

```bash
# 停止服务
docker compose -f docker-compose.backend.yml stop queue-worker

# 删除容器
docker compose -f docker-compose.backend.yml rm -f queue-worker

# 重新构建（如果需要）
docker compose -f docker-compose.backend.yml build queue-worker

# 启动服务
docker compose -f docker-compose.backend.yml up -d queue-worker

# 查看状态
docker compose -f docker-compose.backend.yml ps queue-worker

# 查看日志
docker compose -f docker-compose.backend.yml logs -f queue-worker
```

## 诊断工具

使用诊断脚本检查服务状态：

```bash
# 在服务器上运行
bash diagnose-backend.sh
```

诊断脚本会检查：
1. Docker 服务状态
2. 容器是否存在
3. 镜像列表
4. Backend API 日志
5. Queue Worker 日志
6. Redis 连接
7. 数据库连接
8. 磁盘空间
9. 日志目录

## 验证修复

### 1. 检查服务状态

```bash
docker compose -f docker-compose.backend.yml ps
```

应该看到两个服务都在运行：

```
NAME                 IMAGE                      STATUS
qyd-backend-api      qyd_api-backend-api        Up
qyd-queue-worker     qyd_api-queue-worker       Up
```

### 2. 检查 Queue Worker 日志

```bash
docker compose -f docker-compose.backend.yml logs queue-worker
```

应该看到类似输出：

```
项目启动...
检查并压缩旧日志文件...
数据库初始化完成
Redis队列连接池初始化成功 (DB 0) [project_account]
Redis缓存连接池初始化成功 (DB 1) [project_account]
启动 4 个工作线程处理队列 [project_account]
```

### 3. 测试队列功能

通过 API 添加数据到队列，检查是否被处理：

```bash
# 查看队列大小
redis-cli -h 192.168.1.20 -p 6379 -a redis_password ZCARD qyd_project_account_keys_zset

# 查看 worker 日志
docker compose -f docker-compose.backend.yml logs -f queue-worker
```

## 常见问题

### Q: Queue Worker 启动后立即退出

**可能原因**：
1. Redis 连接失败
2. 数据库连接失败
3. 环境变量配置错误
4. 代码错误

**排查步骤**：

```bash
# 1. 查看详细日志
docker compose -f docker-compose.backend.yml logs queue-worker

# 2. 检查环境变量
docker compose -f docker-compose.backend.yml exec queue-worker env | grep -E "REDIS|DB_"

# 3. 测试 Redis 连接
redis-cli -h 192.168.1.20 -p 6379 -a redis_password PING

# 4. 测试数据库连接
nc -zv 192.168.1.30 3306
```

### Q: Queue Worker 运行但不处理任务

**可能原因**：
1. Redis 队列为空
2. Worker 配置错误
3. 数据格式错误

**排查步骤**：

```bash
# 1. 检查队列大小
redis-cli -h 192.168.1.20 -p 6379 -a redis_password ZCARD qyd_project_account_keys_zset

# 2. 查看 worker 日志
docker compose -f docker-compose.backend.yml logs -f queue-worker | grep -E "处理|成功|失败"

# 3. 检查错误统计
docker compose -f docker-compose.backend.yml exec queue-worker python -c "from app.utils.error_tracker import get_error_stats; import json; print(json.dumps(get_error_stats(), indent=2))"
```

### Q: 如何调整 Worker 数量

修改 `.env.backend` 文件：

```bash
# 增加 worker 数量（默认4个）
REDIS_QUEUE_NUM_WORKERS=8

# 重启服务
docker compose -f docker-compose.backend.yml restart queue-worker
```

### Q: 如何清空队列

```bash
# 清空所有队列数据
redis-cli -h 192.168.1.20 -p 6379 -a redis_password FLUSHDB

# 或者只清空特定队列
redis-cli -h 192.168.1.20 -p 6379 -a redis_password DEL qyd_project_account_keys_zset
```

## 新增脚本说明

### 1. force-rebuild-backend.sh（已更新）

强制重新构建后端服务（包括 backend-api 和 queue-worker）

**使用场景**：
- 代码更新后需要重新构建
- 依赖包更新
- 配置文件修改

**特点**：
- 不使用缓存，完全重新构建
- 同时处理两个服务
- 显示详细的构建和启动日志

### 2. restart-queue-worker.sh（新增）

快速重启 Queue Worker 服务

**使用场景**：
- Queue Worker 异常退出
- 需要重新加载配置
- 快速重启不需要重新构建

**特点**：
- 只重启 queue-worker
- 不重新构建镜像
- 快速执行

### 3. diagnose-backend.sh（新增）

后端服务诊断工具

**使用场景**：
- 服务异常排查
- 定期健康检查
- 问题报告收集

**特点**：
- 全面检查服务状态
- 检查外部依赖（Redis、数据库）
- 显示系统资源使用情况

## 预防措施

### 1. 监控 Queue Worker 状态

添加监控脚本到 crontab：

```bash
# 每5分钟检查一次
*/5 * * * * cd /path/to/project && docker compose -f docker-compose.backend.yml ps queue-worker | grep -q "Up" || docker compose -f docker-compose.backend.yml restart queue-worker
```

### 2. 日志告警

监控关键错误日志：

```bash
# 检查最近的错误
docker compose -f docker-compose.backend.yml logs --since 1h queue-worker | grep -i error
```

### 3. 定期健康检查

```bash
# 添加到定时任务
0 */6 * * * cd /path/to/project && bash diagnose-backend.sh > /tmp/backend-health.log
```

## 相关文档

- `REDIS_ERROR_FIX_SUMMARY.md` - Redis 错误修复总结
- `JSON_DATA_FIX.md` - JSON 数据错误修复
- `LOG_CONFIG_UPDATE.md` - 日志配置更新
- `docker-compose.backend.yml` - 后端服务配置

## 总结

通过以下改进：

1. ✅ 更新 `force-rebuild-backend.sh` 同时处理两个服务
2. ✅ 新增 `restart-queue-worker.sh` 快速重启脚本
3. ✅ 新增 `diagnose-backend.sh` 诊断工具
4. ✅ 提供详细的排查和修复指南

现在重建后端时，queue-worker 会自动一起重建和启动！
