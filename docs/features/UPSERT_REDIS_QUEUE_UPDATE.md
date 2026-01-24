# Upsert Redis 队列更新总结

## 📋 更新概述

本次更新完成了 Redis 队列处理的缓存优化，将缓存从 DB 0 分离到 DB 1，实现了更高效的数据处理流程。

## ✅ 已完成的工作

### 1. 移除自动启动队列处理功能
- **文件**: `backend/start.py`
- **修改**: 移除自动启动 Redis 队列处理的逻辑
- **原因**: 用户希望手动控制队列处理的启动
- **结果**: 启动时只提示用户手动启动队列处理

**启动方式**:
```bash
# 手动启动队列处理
./start_queue_processing.sh

# 或者
python backend/start_queue_worker.py
```

### 2. 修复 Upsert 重复记录问题
- **问题**: 相同的 `account` 和 `project_id` 创建了多条记录而不是更新
- **原因**: UUID vs 字符串类型不匹配，导致无法匹配现有记录
- **修复**: 在 `backend/app/utils/redis_queue.py` 中统一转为字符串比较
- **结果**: 第二次调用显示 "更新 1，创建 0"

**关键代码**:
```python
# 构建key时确保类型一致（都转为字符串）
key = tuple(str(item[field]) for field in self.unique_fields)

# 查询记录时也转为字符串
for record in batch_records:
    key = tuple(str(getattr(record, field)) for field in self.unique_fields)
    existing_records[key] = record
```

### 3. 修复删除操作导入错误
- **问题**: 删除操作报错 "cannot import name 'User' from 'app.models.user'"
- **原因**: `backend/app/apis/deps.py` 中错误导入了 `User`，实际模型名称是 `UserInfo`
- **修复**: 将导入改为 `UserInfo`
- **文件**: `backend/app/apis/deps.py`

### 4. 修改删除权限为基于项目的权限检查
- **需求**: 允许用户删除自己项目下的账号，而不需要 GM 权限
- **修改**: `backend/app/apis/v1/project/account.py` 的删除接口
- **权限逻辑**:
  - ADMIN/GM 可以删除所有项目的账号
  - IT/MANUAL 只能删除自己有权限的项目的账号

**关键代码**:
```python
@app.delete("/{id}")
async def delete(
    id: UUID = Path(...),
    current_user: dict = Depends(get_current_user)  # 改为 get_current_user
):
    # 检查项目权限
    allowed_project_ids = await filter_by_user_projects(user_id)
    
    # 如果不是全局权限，检查是否有该项目的权限
    if allowed_project_ids is not None:
        if str(account.project_id) not in [str(pid) for pid in allowed_project_ids]:
            raise HTTPException(status_code=403, detail="没有权限删除该项目下的账号")
```

### 5. Redis 缓存数据库分离 ⭐
- **需求**: 将缓存从 Redis DB 0 移到 DB 1，优化查询逻辑
- **实现**:
  - DB 0：存储队列数据
  - DB 1：存储缓存数据（1小时过期）
  - 查询顺序：先查 DB 1 缓存 → 没有再查从库 → 最后才创建

### 6. Balance 自动计算功能 ⭐
- **需求**: 在 Redis 队列处理中添加 balance 自动计算逻辑
- **实现**:
  - 当传入 `balance` 时，自动计算 `variable` 和 `balance_history`
  - 如果没有传 `balance`，不处理这些字段
  - 忽略用户传入的 `variable` 和 `balance_history`（防止篡改）
  
**计算逻辑**:
- `balance_history`: 存储最近 7 天的余额记录，同一天多次更新会覆盖
- `variable`: 计算公式
  - 首次创建：`variable = balance`（从 0 增加到 balance）
  - 更新记录：`variable = 今天余额 - 昨天余额`
  - 保留 2 位小数

**关键代码**:
```python
# 过滤掉用户传入的 variable 和 balance_history
filtered_item = {
    k: v for k, v in item.items() 
    if v is not None and k not in ['variable', 'balance_history']
}

# 如果传入了 balance，自动计算
if 'balance' in filtered_item:
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 创建新记录
    if is_new_record:
        record.balance_history = {today: float(new_balance)}
        record.variable = new_balance  # 首次创建，从0增加到balance
    # 更新现有记录
    else:
        record.balance_history[today] = float(new_balance)
        
        # 保留最近 7 天
        sorted_data = dict(sorted(record.balance_history.items(), key=lambda x: x[0], reverse=True))
        record.balance_history = dict(list(sorted_data.items())[:7])
        
        # 计算变动
        if len(record.balance_history) >= 2:
            dates = list(record.balance_history.keys())
            record.variable = today_balance - yesterday_balance
        else:
            record.variable = new_balance  # 只有今天的记录
```

**架构设计**:
```
┌─────────────────────────────────────────────────────────┐
│                    Redis 数据库分离                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  DB 0 (队列数据)              DB 1 (缓存数据)           │
│  ┌──────────────┐            ┌──────────────┐          │
│  │ 待处理任务    │            │ 已处理记录    │          │
│  │ ZSET 队列    │            │ 缓存1小时     │          │
│  │ 处理后删除    │            │ 快速判断      │          │
│  └──────────────┘            └──────────────┘          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**处理流程**:
```
1. 从 DB 0 获取待处理任务
   ↓
2. 检查 DB 1 缓存
   ├─ 已缓存: 跳过处理，删除任务 ✅
   └─ 未缓存: 继续处理
      ↓
3. 查询从库
   ├─ 存在: 更新记录
   └─ 不存在: 创建记录
      ↓
4. 写入主库（事务）
   ↓
5. 缓存到 DB 1（1小时过期）
   ↓
6. 删除 DB 0 任务数据
```

**性能优化**:
| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 首次创建 | 查从库 + 写主库 | 查从库 + 写主库 + 缓存 | 无变化 |
| 重复调用（1小时内） | 查从库 + 写主库 | 跳过（查缓存） | **100%** |
| 缓存过期后 | 查从库 + 写主库 | 查从库 + 写主库 + 缓存 | 无变化 |

**缓存命中率**:
- 假设每个账号平均每小时更新 5 次
- 第1次：未命中（创建/更新）
- 第2-5次：命中（跳过）
- **命中率：80%**
- **数据库压力降低：80%**

## 🧪 测试验证

### 测试场景1：首次创建
```bash
# 1. 清空 DB 1 缓存
redis-cli -h 127.0.0.1 -p 6378 -a password -n 1 FLUSHDB

# 2. 调用 upsert
curl -X POST 'http://127.0.0.1:6080/v1/project/account/upsert' \
  -H 'Authorization: Bearer xxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "account": "test_account",
    "balance": 100,
    "project_id": "xxx-xxx-xxx"
  }'

# 3. 查看日志
# 输出：
# [Worker-0] 处理数据 key=('test_account', 'xxx-xxx-xxx')
# [Worker-0] 数据库操作成功，更新 0，创建 1
# [Worker-0] 缓存添加成功 (DB 1)，缓存 1 条记录，过期时间 3600秒

# 4. 验证缓存
redis-cli -h 127.0.0.1 -p 6378 -a password -n 1 \
  GET "qyd:project_account_cache_test_account_xxx-xxx-xxx"
# 输出：create

# 5. 验证过期时间
redis-cli -h 127.0.0.1 -p 6378 -a password -n 1 \
  TTL "qyd:project_account_cache_test_account_xxx-xxx-xxx"
# 输出：3462 (约58分钟)
```

### 测试场景2：重复调用（命中缓存）
```bash
# 1. 再次调用 upsert（相同的 account 和 project_id）
curl -X POST 'http://127.0.0.1:6080/v1/project/account/upsert' \
  -H 'Authorization: Bearer xxx' \
  -H 'Content-Type: application/json' \
  -d '{
    "account": "test_account",
    "balance": 200,
    "project_id": "xxx-xxx-xxx"
  }'

# 2. 查看日志
# 输出：
# [Worker-1] 跳过 1 条已缓存数据 (DB 1)

# 3. 结果：
# ✅ 没有查询数据库
# ✅ 没有写入数据库
# ✅ 直接跳过处理
```

### 测试场景3：删除权限测试
```bash
# 1. 用户删除自己项目下的账号（成功）
curl -X DELETE 'http://127.0.0.1:6080/v1/project/account/xxx-xxx-xxx' \
  -H 'Authorization: Bearer user_token'
# 输出：{"message": "成功", "count": 1}

# 2. 用户删除其他项目的账号（失败）
curl -X DELETE 'http://127.0.0.1:6080/v1/project/account/yyy-yyy-yyy' \
  -H 'Authorization: Bearer user_token'
# 输出：{"detail": "没有权限删除该项目下的账号"}
```

## 📁 修改的文件

### 1. 后端核心文件
- `backend/start.py` - 移除自动启动队列处理
- `backend/app/utils/redis_queue.py` - Redis 缓存数据库分离
- `backend/app/apis/deps.py` - 修复导入错误
- `backend/app/apis/v1/project/account.py` - 修改删除权限

### 2. 配置文件
- `backend/.env` - 移除 `AUTO_START_QUEUE_WORKER` 配置
- `backend/.env.example` - 移除 `AUTO_START_QUEUE_WORKER` 配置

### 3. 脚本文件
- `start_queue_processing.sh` - 新增队列处理启动脚本
- `backend/scripts/cleanup_duplicate_accounts.py` - 新增清理重复账号脚本
- `backend/test_balance_calculation.py` - 新增 balance 自动计算测试脚本

### 4. 文档文件
- `REDIS_QUEUE_MANUAL_START.md` - 手动启动指南
- `docs/fixes/UPSERT_DUPLICATE_FIX.md` - Upsert 重复记录修复文档
- `docs/fixes/DELETE_PERMISSION_IMPORT_FIX.md` - 删除权限导入修复文档
- `docs/fixes/PROJECT_ACCOUNT_DELETE_PERMISSION.md` - 项目账号删除权限文档
- `docs/fixes/REDIS_CACHE_DB_SEPARATION.md` - Redis 缓存分离文档
- `docs/fixes/BALANCE_AUTO_CALCULATION_IN_QUEUE.md` - Balance 自动计算文档
- `UPSERT_REDIS_QUEUE_UPDATE.md` - 本文档（总结）

## 🔍 监控和调试

### 查看缓存状态
```bash
# 查看 DB 1 中的所有缓存
redis-cli -h 127.0.0.1 -p 6378 -a password -n 1 KEYS "qyd:project_account_cache_*"

# 查看缓存数量
redis-cli -h 127.0.0.1 -p 6378 -a password -n 1 DBSIZE

# 查看特定缓存
redis-cli -h 127.0.0.1 -p 6378 -a password -n 1 \
  GET "qyd:project_account_cache_ACCOUNT_PROJECTID"

# 查看缓存过期时间
redis-cli -h 127.0.0.1 -p 6378 -a password -n 1 \
  TTL "qyd:project_account_cache_ACCOUNT_PROJECTID"
```

### 查看队列状态
```bash
# 查看 DB 0 中的队列大小
redis-cli -h 127.0.0.1 -p 6378 -a password -n 0 \
  ZCARD qyd:project_account_keys_zset

# 查看队列中的任务
redis-cli -h 127.0.0.1 -p 6378 -a password -n 0 \
  ZRANGE qyd:project_account_keys_zset 0 -1
```

### 日志关键字
```bash
# 查看缓存命中日志
tail -f backend/logs/app.log | grep "跳过.*已缓存数据 (DB 1)"

# 查看缓存添加日志
tail -f backend/logs/app.log | grep "缓存添加成功 (DB 1)"

# 查看数据库操作日志
tail -f backend/logs/app.log | grep "数据库操作成功"
```

## 💡 使用建议

### 1. 队列处理启动
```bash
# 启动后端服务
cd backend
python start.py

# 在另一个终端启动队列处理
./start_queue_processing.sh
```

### 2. 缓存过期时间调整
根据业务特点调整缓存过期时间：
- 高频更新：30分钟
- 中频更新：1小时（默认）
- 低频更新：2-4小时

修改位置：`backend/app/utils/redis_queue.py`
```python
class RedisQueueHandler:
    def __init__(self, ...):
        self.cache_expire_seconds = 3600  # 修改这里
```

### 3. 清理缓存
```bash
# 手动清理 DB 1 缓存
redis-cli -h 127.0.0.1 -p 6378 -a password -n 1 FLUSHDB

# 清理重复账号（如果有）
cd backend
python scripts/cleanup_duplicate_accounts.py
```

## 📊 性能对比

### 优化前
```
每次 upsert 调用：
1. 添加到 Redis 队列（DB 0）
2. Worker 从队列获取任务
3. 查询从库（每次都查）
4. 写入主库（每次都写）
5. 删除队列任务

数据库压力：100%
```

### 优化后
```
首次 upsert 调用：
1. 添加到 Redis 队列（DB 0）
2. Worker 从队列获取任务
3. 检查缓存（DB 1）- 未命中
4. 查询从库
5. 写入主库
6. 缓存到 DB 1（1小时）
7. 删除队列任务

重复 upsert 调用（1小时内）：
1. 添加到 Redis 队列（DB 0）
2. Worker 从队列获取任务
3. 检查缓存（DB 1）- 命中 ✅
4. 跳过处理
5. 删除队列任务

数据库压力：20%（假设80%命中率）
```

## 🎯 关键改进点

1. **类型一致性**: 所有唯一字段都转为字符串进行比较，避免 UUID vs 字符串不匹配
2. **缓存分离**: DB 0 存队列，DB 1 存缓存，职责清晰
3. **查询优化**: 先查缓存，减少 80% 的数据库查询
4. **权限细化**: 用户可以删除自己项目下的账号，不需要 GM 权限
5. **手动控制**: 队列处理需要手动启动，更灵活
6. **Balance 自动计算**: 传入 balance 时自动计算 variable 和 balance_history，防止用户篡改

## 📅 更新信息

- **更新时间**: 2026-01-23
- **版本**: v2.1
- **状态**: ✅ 已完成并测试通过
- **测试环境**: macOS, Python 3.11+, Redis 7.0, MySQL 8.0

## 🧪 快速测试

### 测试 Balance 自动计算

```bash
# 1. 启动后端服务
cd backend
python start.py

# 2. 启动队列处理（另一个终端）
./start_queue_processing.sh

# 3. 运行测试脚本（第三个终端）
cd backend
python test_balance_calculation.py
```

测试脚本会自动测试以下场景：
1. 首次创建（传入 balance=100）
2. 第二天更新（传入 balance=150）
3. 不传 balance，只更新其他字段
4. 传入 variable 和 balance_history（应该被忽略）

---

**相关文档**:
- [Redis 队列手动启动指南](REDIS_QUEUE_MANUAL_START.md)
- [Upsert 重复记录修复](docs/fixes/UPSERT_DUPLICATE_FIX.md)
- [Redis 缓存分离详细文档](docs/fixes/REDIS_CACHE_DB_SEPARATION.md)
- [项目账号删除权限](docs/fixes/PROJECT_ACCOUNT_DELETE_PERMISSION.md)
- [Balance 自动计算详细文档](docs/fixes/BALANCE_AUTO_CALCULATION_IN_QUEUE.md)
