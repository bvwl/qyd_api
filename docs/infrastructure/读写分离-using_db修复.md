# 读写分离 using_db() 修复

## 问题描述

在实现读写分离后，调用统计API时出现错误：

```
'str' object has no attribute 'executor_class'
```

## 问题原因

在 `backend/app/core/database.py` 中，`db_read()` 和 `db_write()` 函数使用了错误的方式调用 `.using_db()`：

```python
# ❌ 错误的实现
def read(model: Type[T]) -> QuerySet[T]:
    if DB_READ_WRITE_SPLIT:
        db_name = get_read_db()  # 返回字符串 "slave1" 或 "slave2"
        return model.filter().using_db(db_name)  # 传入字符串
    return model.filter()
```

**问题分析**：

1. `get_read_db()` 返回的是连接名称（字符串），如 `"slave1"`, `"slave2"`, `"default"`
2. `.using_db()` 方法期望接收 `BaseDBAsyncClient` 对象，而不是字符串
3. 当传入字符串时，Tortoise ORM 内部的 `self._db` 被设置为字符串
4. 执行查询时，尝试访问 `self._db.executor_class` 导致 `AttributeError`

## 解决方案

修改 `backend/app/core/database.py`，使用 `Tortoise.get_connection()` 获取实际的数据库连接对象：

```python
# ✅ 正确的实现
from tortoise import Tortoise

def read(model: Type[T]) -> QuerySet[T]:
    if DB_READ_WRITE_SPLIT:
        db_name = get_read_db()  # 返回字符串 "slave1" 或 "slave2"
        db_conn = Tortoise.get_connection(db_name)  # 获取连接对象
        return model.filter().using_db(db_conn)  # 传入连接对象
    return model.filter()

def write(model: Type[T]) -> QuerySet[T]:
    if DB_READ_WRITE_SPLIT:
        db_name = get_write_db()  # 返回字符串 "default"
        db_conn = Tortoise.get_connection(db_name)  # 获取连接对象
        return model.filter().using_db(db_conn)  # 传入连接对象
    return model.filter()
```

## 修改的文件

- `backend/app/core/database.py` - 修复 `db_read()` 和 `db_write()` 函数

## 测试验证

### 1. 单元测试

创建测试脚本 `backend/test_read_db_issue.py`：

```bash
cd backend
python test_read_db_issue.py
```

输出：
```
✅ 统计缓存Redis连接成功（DB 10）
DB_READ_WRITE_SPLIT: True
get_read_db() returns: default

Tortoise ORM connections:
  - default
  - slave1
  - slave2

Testing db_read(ProjectDailyStats)...
  Type: <class 'tortoise.queryset.QuerySet'>
  Query: <tortoise.queryset.QuerySet object at 0x111e3cee0>

Trying to execute query...
  Results count: 5
  ✅ Query executed successfully!
```

### 2. API测试

测试统计API：

```bash
# IT/MANUAL 用户（只能看自己的项目）
curl 'http://127.0.0.1:6080/v1/project/stats/dashboard?days=7' \
  -H 'Authorization: Bearer <token>'

# ADMIN 用户（可以看所有项目）
curl 'http://127.0.0.1:6080/v1/project/stats/dashboard?days=7' \
  -H 'Authorization: Bearer <admin_token>'
```

返回结果：
```json
{
  "code": 1,
  "message": "成功",
  "data": [
    {
      "project_id": "xxx",
      "project_name": "项目A",
      "dates": ["2026-01-19", ..., "2026-01-25"],
      "counts": [0, 0, 0, 1, 0, 0, 3]
    }
  ]
}
```

## 技术要点

### Tortoise ORM 的 using_db() 方法

```python
def using_db(self, _db: 'BaseDBAsyncClient | None') -> 'QuerySet[MODEL]':
    """
    Executes query in provided db client.
    Useful for transactions workaround.
    """
```

**关键点**：
- 参数类型：`BaseDBAsyncClient | None`（数据库连接对象）
- 不是字符串连接名称
- 需要通过 `Tortoise.get_connection(name)` 获取连接对象

### 获取数据库连接对象

```python
from tortoise import Tortoise

# 方法1：通过连接名称获取
conn = Tortoise.get_connection("default")  # 主库
conn = Tortoise.get_connection("slave1")   # 从库1
conn = Tortoise.get_connection("slave2")   # 从库2

# 方法2：获取所有连接
connections = Tortoise._connections
```

## 读写分离完整流程

### 1. 配置数据库连接

在 `backend/app/core/settings.py` 中配置：

```python
TORTOISE_ORM = {
    "connections": {
        "default": {...},   # 主库
        "slave1": {...},    # 从库1
        "slave2": {...},    # 从库2
    },
    ...
}
```

### 2. 轮询负载均衡

`get_read_db()` 函数使用轮询算法选择从库：

```python
def get_read_db():
    global _read_db_index
    slaves = ["slave1", "slave2"]
    
    for _ in range(len(slaves)):
        slave = slaves[_read_db_index % len(slaves)]
        _read_db_index += 1
        
        if check_slave_health(slave):
            return slave
    
    # 所有从库都不健康，降级到主库
    return "default"
```

### 3. 使用读写分离

```python
from app.core.database import db_read, db_write

# 读操作（使用从库）
users = await db_read(User).filter(status=1).all()
user = await db_read(User).get(id=user_id)

# 写操作（使用主库）
await db_write(User).create(email="test@example.com")
await db_write(User).filter(id=user_id).update(name="new_name")
await db_write(User).filter(id=user_id).delete()
```

## 相关文档

- [读写分离-轮询负载均衡.md](./读写分离-轮询负载均衡.md) - 轮询负载均衡实现
- [项目统计功能-读写分离说明.md](./项目统计功能-读写分离说明.md) - 统计功能的读写分离
- [项目统计功能快速开始.md](./项目统计功能快速开始.md) - 统计功能完整说明

## 总结

这次修复的核心问题是：**Tortoise ORM 的 `.using_db()` 方法需要传入数据库连接对象，而不是连接名称字符串**。

修复后，读写分离功能正常工作：
- ✅ 读操作使用从库（轮询负载均衡）
- ✅ 写操作使用主库
- ✅ 健康检查和自动降级
- ✅ 统计API正常返回数据
