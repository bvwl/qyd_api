# 代理 URL 问题排查总结

## 问题描述

用户点击"复制代理"和"测试代理"时，代理 URL 显示默认的 `username:password`，没有获取到当前用户的服务器账号信息。

## 已完成的工作

### 1. 添加调试日志 ✅

在 `backend/app/crud/server/info.py` 的 `_generate_proxy_url` 方法中添加了详细的调试日志：

- 记录用户 ID 和用户信息
- 记录服务器账号查询结果
- 记录密码解密状态
- 记录异常情况

### 2. 创建检查脚本 ✅

创建了 `backend/check_server_account.py` 脚本，用于：

- 检查特定用户是否有服务器账号
- 列出所有服务器账号
- 验证密码加密/解密是否正常
- 提供创建账号的示例代码

### 3. 创建调试文档 ✅

- `PROXY_URL_DEBUG_GUIDE.md` - 完整的调试指南
- `PROXY_URL_DEBUG_QUICK_REF.md` - 快速参考

### 4. 提交到 Git ✅

所有代码和文档已提交并推送到 Git 仓库。

## 下一步操作（需要在服务器上执行）

### 步骤 1: 重启后端服务

应用新的调试日志：

```bash
cd /opt/zy/qyd_api
docker compose -f docker-compose.backend.yml restart backend-api
```

### 步骤 2: 检查用户服务器账号

```bash
# 进入容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 检查当前登录用户（替换为实际的用户邮箱）
python check_server_account.py zhiyu

# 或者列出所有账号
python check_server_account.py --list
```

### 步骤 3: 查看日志

在另一个终端窗口查看实时日志：

```bash
cd /opt/zy/qyd_api
docker compose -f docker-compose.backend.yml logs -f backend-api
```

然后在前端点击"复制代理"或"测试代理"，观察日志输出。

### 步骤 4: 根据日志结果采取行动

#### 情况 A: 用户没有服务器账号

日志显示：
```
WARNING: 未找到用户 xxx 的服务器账号，使用默认账号密码
```

**解决方法**：创建服务器账号

```bash
# 进入容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 启动 Python
python
```

在 Python 中执行：

```python
import asyncio
from app.models.user import UserInfo
from app.models.server import ServerAccount
from app.core.database import init_db
from app.core.tools import aes_encrypt

async def create_account():
    await init_db()
    
    # 查找用户（替换为实际的用户邮箱）
    user = await UserInfo.get(email='zhiyu')
    print(f"用户ID: {user.id}")
    
    # 创建账号（替换为实际的用户名和密码）
    username = 'your_proxy_username'
    password = 'your_proxy_password'
    
    encrypted_password = aes_encrypt(password, str(user.id))
    account = await ServerAccount.create(
        username=username,
        password=encrypted_password,
        user_id=user.id
    )
    
    print(f"✓ 账号创建成功: {account.username}")

asyncio.run(create_account())
```

#### 情况 B: 密码解密失败

日志显示：
```
ERROR: 密码解密失败: ...
```

**解决方法**：重新加密密码

```python
import asyncio
from app.models.user import UserInfo
from app.models.server import ServerAccount
from app.core.database import init_db
from app.core.tools import aes_encrypt

async def fix_password():
    await init_db()
    
    user = await UserInfo.get(email='zhiyu')
    account = await ServerAccount.get(user_id=user.id)
    
    # 重新加密密码
    new_password = 'your_proxy_password'
    account.password = aes_encrypt(new_password, str(user.id))
    await account.save()
    
    print(f"✓ 密码重新加密成功")

asyncio.run(fix_password())
```

#### 情况 C: 未提供用户信息

日志显示：
```
WARNING: 未提供用户信息，使用默认账号密码
```

这种情况不应该发生，因为 API 层已经正确传递了 `current_user`。如果出现这种情况，可能是：
1. JWT Token 无效或过期
2. 前端没有正确发送 Authorization 头

**解决方法**：
1. 检查前端是否正确发送 Token
2. 尝试重新登录获取新的 Token

### 步骤 5: 验证修复

创建或修复账号后：

1. 在前端刷新页面
2. 点击"复制代理"或"测试代理"
3. 检查代理 URL 格式

**预期结果**：
```
http://your_proxy_username:your_proxy_password@192.168.13.6:25000
```

或

```
socks5://your_proxy_username:your_proxy_password@192.168.13.6:35000
```

## 可能的根本原因

根据代码分析，最可能的原因是：

1. **用户没有服务器账号**（最可能）
   - 数据库中 `proxy_account` 表没有该用户的记录
   - 需要手动创建

2. **密码加密/解密问题**
   - 密码加密时使用的密钥与解密时不一致
   - 需要重新加密密码

3. **数据库关联问题**
   - `proxy_account.user_id` 与 `user_info.id` 不匹配
   - 需要检查数据完整性

## 技术细节

### 代理 URL 生成流程

```
1. API 层接收请求
   ↓
2. 从 JWT Token 获取 current_user
   ↓
3. 传递 current_user 到 CRUD 层
   ↓
4. CRUD 层调用 _generate_proxy_url
   ↓
5. 从 current_user 提取 user_id
   ↓
6. 查询 proxy_account 表
   ↓
7. 如果找到账号：
   - 使用账号的 username
   - 使用 user_id 解密 password
   ↓
8. 如果未找到账号：
   - 使用默认 "username:password"
   ↓
9. 生成代理 URL
```

### 数据库表关系

```
user_info (用户表)
    ↓ (一对一)
proxy_account (服务器账号表)
    - user_id (外键，关联 user_info.id)
    - username (代理用户名)
    - password (AES 加密的密码)
```

### 密码加密方式

- 算法：AES
- 密钥：`user_id`（字符串格式）
- 存储：TEXT 字段（加密后的密文）

## 相关文件

- `backend/app/crud/server/info.py` - 代理 URL 生成逻辑（已添加调试日志）
- `backend/app/apis/v1/server/info.py` - API 路由
- `backend/app/models/server.py` - ServerAccount 模型定义
- `backend/check_server_account.py` - 检查脚本（新增）
- `PROXY_URL_DEBUG_GUIDE.md` - 详细调试指南（新增）
- `PROXY_URL_DEBUG_QUICK_REF.md` - 快速参考（新增）

## Git 提交记录

```
88ba8ba - docs(proxy): 添加代理URL调试指南
6300666 - feat(server): 添加代理URL调试日志和检查脚本
```

## 总结

代码逻辑本身是正确的，问题很可能是数据层面的：用户在数据库中没有对应的服务器账号记录。通过运行检查脚本和查看日志，可以快速定位问题并创建缺失的账号。
