# 代理 URL 调试指南

## 问题描述

点击"复制代理"和"测试代理"时，代理 URL 显示默认的 `username:password`，没有获取到当前用户的服务器账号信息。

## 调试步骤

### 1. 检查用户是否有服务器账号

运行检查脚本查看用户是否在数据库中有服务器账号：

```bash
# 进入后端容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 检查特定用户（替换为实际的用户邮箱）
python check_server_account.py zhiyu

# 或者列出所有服务器账号
python check_server_account.py --list
```

**预期输出**：

如果用户有服务器账号：
```
==============================================================
检查用户服务器账号: zhiyu
==============================================================

1. 查找用户...
   ✓ 用户ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ✓ 昵称: 管理员
   ✓ 状态: 1

2. 查找服务器账号...
   ✓ 账号ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ✓ 用户名: your_username
   ✓ 密码(加密): xxxxxxxxxxxxx...
   ✓ 是否已添加到所有入站: False

3. 尝试解密密码...
   ✓ 密码解密成功
   ✓ 明文密码: your_password

4. 代理 URL 示例:
   HTTP:    http://your_username:your_password@proxy.example.com:25000
   SOCKS5:  socks5://your_username:your_password@proxy.example.com:35000
```

如果用户没有服务器账号：
```
==============================================================
检查用户服务器账号: zhiyu
==============================================================

1. 查找用户...
   ✓ 用户ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ✓ 昵称: 管理员
   ✓ 状态: 1

2. 查找服务器账号...
   ✗ 未找到服务器账号

   建议: 为用户创建服务器账号
   ```python
   from app.models.server import ServerAccount
   from app.core.tools import aes_encrypt
   
   encrypted_password = aes_encrypt('your_password', 'user_id_here')
   account = await ServerAccount.create(
       username='your_username',
       password=encrypted_password,
       user_id='user_id_here'
   )
   ```
```

### 2. 查看后端日志

重启后端服务以应用新的调试日志：

```bash
# 重启后端服务
docker compose -f docker-compose.backend.yml restart backend-api

# 查看实时日志
docker compose -f docker-compose.backend.yml logs -f backend-api
```

然后在前端点击"复制代理"或"测试代理"，观察日志输出：

**正常情况**（找到服务器账号）：
```
INFO: 生成代理URL - 用户ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, 用户信息: {'user_id': '...', 'email': 'zhiyu', ...}
INFO: 找到服务器账号 - 用户名: your_username
INFO: 密码解密成功
```

**异常情况1**（未找到服务器账号）：
```
INFO: 生成代理URL - 用户ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, 用户信息: {'user_id': '...', 'email': 'zhiyu', ...}
WARNING: 未找到用户 xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx 的服务器账号，使用默认账号密码
```

**异常情况2**（密码解密失败）：
```
INFO: 生成代理URL - 用户ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx, 用户信息: {'user_id': '...', 'email': 'zhiyu', ...}
INFO: 找到服务器账号 - 用户名: your_username
ERROR: 密码解密失败: ...
```

**异常情况3**（未提供用户信息）：
```
WARNING: 未提供用户信息，使用默认账号密码
```

### 3. 创建服务器账号（如果不存在）

如果用户没有服务器账号，需要创建一个：

```bash
# 进入后端容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 启动 Python 交互式环境
python
```

在 Python 环境中执行：

```python
import asyncio
from app.models.user import UserInfo
from app.models.server import ServerAccount
from app.core.database import init_db
from app.core.tools import aes_encrypt

async def create_server_account():
    # 初始化数据库
    await init_db()
    
    # 1. 查找用户（替换为实际的用户邮箱）
    user = await UserInfo.get(email='zhiyu')
    print(f"用户ID: {user.id}")
    
    # 2. 创建服务器账号
    # 替换为实际的用户名和密码
    username = 'your_proxy_username'
    password = 'your_proxy_password'
    
    # 使用用户ID加密密码
    encrypted_password = aes_encrypt(password, str(user.id))
    
    # 创建账号
    account = await ServerAccount.create(
        username=username,
        password=encrypted_password,
        user_id=user.id
    )
    
    print(f"✓ 服务器账号创建成功")
    print(f"  账号ID: {account.id}")
    print(f"  用户名: {account.username}")

# 运行
asyncio.run(create_server_account())
```

### 4. 验证修复

创建服务器账号后，再次测试：

1. 在前端刷新页面
2. 点击"复制代理"或"测试代理"
3. 检查代理 URL 是否包含正确的用户名和密码

**预期结果**：
```
http://your_proxy_username:your_proxy_password@192.168.13.6:25000
```

或

```
socks5://your_proxy_username:your_proxy_password@192.168.13.6:35000
```

## 常见问题

### Q1: 为什么需要服务器账号？

A: 系统设计为每个用户使用自己的代理账号，而不是共享同一个账号。这样可以：
- 更好地追踪每个用户的代理使用情况
- 提供更细粒度的访问控制
- 避免账号冲突

### Q2: 如何批量创建服务器账号？

A: 可以编写脚本批量创建：

```python
import asyncio
from app.models.user import UserInfo
from app.models.server import ServerAccount
from app.core.database import init_db
from app.core.tools import aes_encrypt

async def batch_create_accounts():
    await init_db()
    
    # 获取所有没有服务器账号的用户
    users = await UserInfo.all()
    
    for user in users:
        # 检查是否已有账号
        existing = await ServerAccount.get_or_none(user_id=user.id)
        if existing:
            print(f"跳过 {user.email}，已有账号")
            continue
        
        # 创建账号（可以根据需要自定义用户名和密码生成规则）
        username = f"user_{user.email}"
        password = "default_password"  # 建议使用随机密码
        
        encrypted_password = aes_encrypt(password, str(user.id))
        
        await ServerAccount.create(
            username=username,
            password=encrypted_password,
            user_id=user.id
        )
        
        print(f"✓ 为 {user.email} 创建服务器账号")

asyncio.run(batch_create_accounts())
```

### Q3: 密码解密失败怎么办？

A: 密码解密失败通常是因为：
1. 密码加密时使用的密钥与解密时不一致
2. 密码数据损坏

解决方法：
```python
# 重新加密密码
from app.core.tools import aes_encrypt

# 获取账号
account = await ServerAccount.get(user_id=user_id)

# 重新加密密码
new_encrypted_password = aes_encrypt('new_password', str(user_id))
account.password = new_encrypted_password
await account.save()
```

### Q4: 如何修改现有账号的密码？

A: 使用以下脚本：

```python
import asyncio
from app.models.user import UserInfo
from app.models.server import ServerAccount
from app.core.database import init_db
from app.core.tools import aes_encrypt

async def update_password():
    await init_db()
    
    # 查找用户
    user = await UserInfo.get(email='zhiyu')
    
    # 查找服务器账号
    account = await ServerAccount.get(user_id=user.id)
    
    # 更新密码
    new_password = 'new_proxy_password'
    account.password = aes_encrypt(new_password, str(user.id))
    await account.save()
    
    print(f"✓ 密码更新成功")

asyncio.run(update_password())
```

## 技术细节

### 代理 URL 生成逻辑

1. **端口范围判断**：
   - HTTP 代理：22000-29999
   - SOCKS5 代理：32000-39999

2. **账号获取**：
   - 从 JWT Token 中获取 `user_id`
   - 查询 `proxy_account` 表（ServerAccount 模型）
   - 使用 `user_id` 作为外键关联

3. **密码解密**：
   - 使用 AES 加密算法
   - 密钥为 `user_id`（字符串格式）
   - 解密失败时使用默认密码 "password"

4. **URL 格式**：
   ```
   {protocol}://{username}:{password}@{host}:{port}
   ```

### 数据库表结构

```sql
CREATE TABLE `proxy_account` (
  `id` char(36) NOT NULL,
  `username` varchar(36) NOT NULL,
  `password` text NOT NULL,
  `is_all_inbound_added` tinyint(1) NOT NULL DEFAULT 0,
  `user_id` char(36) DEFAULT NULL,
  `create_time` datetime(6) NOT NULL,
  `update_time` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `idx_proxy_account_username` (`username`),
  KEY `idx_proxy_account_user_id_create_time` (`user_id`, `create_time`),
  KEY `idx_proxy_account_is_all_inbound_added` (`is_all_inbound_added`)
);
```

## 相关文件

- `backend/app/crud/server/info.py` - 代理 URL 生成逻辑
- `backend/app/apis/v1/server/info.py` - API 路由
- `backend/app/models/server.py` - ServerAccount 模型定义
- `backend/check_server_account.py` - 检查脚本
- `backend/PROXY_URL_FEATURE.md` - 功能文档

## 下一步

1. 运行 `check_server_account.py` 检查用户是否有服务器账号
2. 查看后端日志确认调试信息
3. 如果没有账号，创建服务器账号
4. 验证代理 URL 是否正确生成
