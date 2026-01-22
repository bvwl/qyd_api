# MySQL读写分离使用指南

## 📋 概述

本项目已配置MySQL主从复制和读写分离：
- **主库（端口3307）**：处理所有写操作（INSERT、UPDATE、DELETE）
- **从库1（端口3308）**：处理读操作（SELECT）
- **从库2（端口3309）**：处理读操作（SELECT）

读操作会在两个从库之间随机负载均衡。

## 🔧 配置说明

### 环境变量配置（.env）

```ini
# 主库配置（写操作）
DB_HOST=192.168.11.150
DB_PORT=3307
DB_USER=root
DB_PASSWORD=zhiyu666
DB_NAME=qyd

# 启用读写分离
DB_READ_WRITE_SPLIT=1

# 从库1配置
DB_SLAVE1_HOST=192.168.11.150
DB_SLAVE1_PORT=3308
DB_SLAVE1_USER=root
DB_SLAVE1_PASSWORD=zhiyu666
DB_SLAVE1_NAME=qyd

# 从库2配置
DB_SLAVE2_HOST=192.168.11.150
DB_SLAVE2_PORT=3309
DB_SLAVE2_USER=root
DB_SLAVE2_PASSWORD=zhiyu666
DB_SLAVE2_NAME=qyd
```

### 禁用读写分离

如果需要临时禁用读写分离（所有操作都走主库）：

```ini
DB_READ_WRITE_SPLIT=0
```

## 💻 代码使用方法

### 方法1：使用ReadWriteRouter（推荐）

```python
from app.core.database import ReadWriteRouter, db_read, db_write
from app.models.user import User

# ============================================
# 读操作（从从库读取）
# ============================================

# 查询所有用户
users = await db_read(User).all()

# 查询单个用户
user = await db_read(User).get(id=1)

# 条件查询
active_users = await db_read(User).filter(is_active=True).all()

# 分页查询
users = await db_read(User).offset(0).limit(10).all()

# 统计
count = await db_read(User).count()

# 关联查询
user = await db_read(User).get(id=1).prefetch_related("roles")


# ============================================
# 写操作（写入主库）
# ============================================

# 创建新记录
user = await db_write(User).create(
    username="test",
    email="test@example.com",
    password="hashed_password"
)

# 更新记录
user = await db_write(User).get(id=1)
user.username = "new_name"
await user.save()

# 批量更新
await db_write(User).filter(is_active=False).update(status="inactive")

# 删除记录
await db_write(User).filter(id=1).delete()

# 批量删除
await db_write(User).filter(created_at__lt=some_date).delete()
```

### 方法2：使用using_db（手动指定）

```python
from app.models.user import User

# 从从库1读取
users = await User.using_db("slave1").all()

# 从从库2读取
users = await User.using_db("slave2").all()

# 从主库读取（如果需要读取最新数据）
user = await User.using_db("default").get(id=1)

# 写入主库
user = await User.using_db("default").create(username="test")
```

## 📝 实际应用示例

### 示例1：用户CRUD操作

```python
from app.core.database import db_read, db_write
from app.models.user import User

class UserService:
    """用户服务"""
    
    async def get_user_list(self, page: int = 1, size: int = 10):
        """获取用户列表（读操作 - 从库）"""
        offset = (page - 1) * size
        users = await db_read(User).offset(offset).limit(size).all()
        total = await db_read(User).count()
        return {"users": users, "total": total}
    
    async def get_user_by_id(self, user_id: int):
        """获取用户详情（读操作 - 从库）"""
        return await db_read(User).get(id=user_id)
    
    async def create_user(self, username: str, email: str, password: str):
        """创建用户（写操作 - 主库）"""
        return await db_write(User).create(
            username=username,
            email=email,
            password=password
        )
    
    async def update_user(self, user_id: int, **kwargs):
        """更新用户（写操作 - 主库）"""
        user = await db_write(User).get(id=user_id)
        for key, value in kwargs.items():
            setattr(user, key, value)
        await user.save()
        return user
    
    async def delete_user(self, user_id: int):
        """删除用户（写操作 - 主库）"""
        await db_write(User).filter(id=user_id).delete()
```

### 示例2：项目管理

```python
from app.core.database import db_read, db_write
from app.models.project import Project

class ProjectService:
    """项目服务"""
    
    async def search_projects(self, keyword: str = None):
        """搜索项目（读操作 - 从库）"""
        query = db_read(Project)
        if keyword:
            query = query.filter(name__icontains=keyword)
        return await query.all()
    
    async def create_project(self, name: str, description: str):
        """创建项目（写操作 - 主库）"""
        return await db_write(Project).create(
            name=name,
            description=description
        )
    
    async def update_project_status(self, project_id: int, status: str):
        """更新项目状态（写操作 - 主库）"""
        await db_write(Project).filter(id=project_id).update(status=status)
```

### 示例3：在API路由中使用

```python
from fastapi import APIRouter, Depends
from app.core.database import db_read, db_write
from app.models.user import User

router = APIRouter()

@router.get("/users")
async def get_users():
    """获取用户列表（读操作）"""
    users = await db_read(User).all()
    return {"users": users}

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    """获取用户详情（读操作）"""
    user = await db_read(User).get(id=user_id)
    return user

@router.post("/users")
async def create_user(username: str, email: str):
    """创建用户（写操作）"""
    user = await db_write(User).create(
        username=username,
        email=email
    )
    return user

@router.put("/users/{user_id}")
async def update_user(user_id: int, username: str):
    """更新用户（写操作）"""
    user = await db_write(User).get(id=user_id)
    user.username = username
    await user.save()
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """删除用户（写操作）"""
    await db_write(User).filter(id=user_id).delete()
    return {"message": "User deleted"}
```

## ⚠️ 注意事项

### 1. 主从延迟问题

主从复制可能存在微小延迟（通常小于1秒），如果需要读取刚写入的数据，应该从主库读取：

```python
# 错误示例：可能读不到刚创建的数据
user = await db_write(User).create(username="test")
user_check = await db_read(User).get(id=user.id)  # 可能失败

# 正确示例：从主库读取刚写入的数据
user = await db_write(User).create(username="test")
user_check = await User.using_db("default").get(id=user.id)  # 从主库读取
```

### 2. 事务处理

事务操作必须在主库上进行：

```python
from tortoise.transactions import in_transaction

# 正确：在主库上执行事务
async with in_transaction("default") as conn:
    user = await User.create(username="test", using_db=conn)
    await Project.create(name="test", user=user, using_db=conn)
```

### 3. 写后立即读

如果业务逻辑是"写入后立即读取"，建议从主库读取：

```python
# 创建用户
user = await db_write(User).create(username="test")

# 立即读取（从主库）
user_detail = await User.using_db("default").get(id=user.id)
```

### 4. 统计数据

对于实时性要求高的统计数据，建议从主库读取：

```python
# 实时统计（从主库）
total_users = await User.using_db("default").count()

# 非实时统计（从从库，性能更好）
total_users = await db_read(User).count()
```

## 🔍 监控和调试

### 查看数据库配置信息

```python
from app.core.database import get_db_info

# 获取数据库配置
db_info = get_db_info()
print(db_info)

# 输出示例：
# {
#     "read_write_split": True,
#     "master": {
#         "host": "192.168.11.150",
#         "port": 3307,
#         "database": "qyd"
#     },
#     "slaves": [
#         {
#             "name": "slave1",
#             "host": "192.168.11.150",
#             "port": 3308,
#             "database": "qyd"
#         },
#         {
#             "name": "slave2",
#             "host": "192.168.11.150",
#             "port": 3309,
#             "database": "qyd"
#         }
#     ]
# }
```

### 添加数据库信息API

```python
from fastapi import APIRouter
from app.core.database import get_db_info

router = APIRouter()

@router.get("/system/database")
async def get_database_info():
    """获取数据库配置信息"""
    return get_db_info()
```

## 🚀 性能优化建议

### 1. 连接池配置

根据实际负载调整连接池大小：

```ini
# 主库（写操作较少，连接池可以小一些）
DB_MINSIZE=10
DB_MAXSIZE=40

# 从库（读操作较多，连接池可以大一些）
DB_SLAVE1_MINSIZE=20
DB_SLAVE1_MAXSIZE=80
DB_SLAVE2_MINSIZE=20
DB_SLAVE2_MAXSIZE=80
```

### 2. 负载均衡策略

当前使用随机负载均衡，如需更复杂的策略（如轮询、权重），可以修改 `settings.py` 中的 `get_read_db()` 函数。

### 3. 读写比例监控

建议添加日志记录读写操作的比例，用于优化配置：

```python
import logging

logger = logging.getLogger(__name__)

def get_read_db():
    """获取读数据库连接名称"""
    if not DB_READ_WRITE_SPLIT:
        return "default"
    
    db = random.choice(["slave1", "slave2"])
    logger.debug(f"Read operation routed to: {db}")
    return db
```

## 📚 相关文档

- [MySQL主从复制部署文档](../docs/mysql主从.md)
- [单服务器部署教程](../docs/mysql主从-单服务器分步部署教程.md)
- [问题排查指南](../docs/mysql主从复制问题总结.md)
- [Tortoise ORM文档](https://tortoise.github.io/)

