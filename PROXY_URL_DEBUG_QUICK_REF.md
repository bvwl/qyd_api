# 代理 URL 调试快速参考

## 快速诊断

### 1. 检查用户服务器账号

```bash
# 进入容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 检查特定用户
python check_server_account.py zhiyu

# 列出所有账号
python check_server_account.py --list
```

### 2. 查看实时日志

```bash
# 重启服务（应用新的调试日志）
docker compose -f docker-compose.backend.yml restart backend-api

# 查看日志
docker compose -f docker-compose.backend.yml logs -f backend-api
```

然后在前端点击"复制代理"，观察日志输出。

### 3. 创建服务器账号（如果不存在）

```bash
# 进入容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 启动 Python
python
```

```python
import asyncio
from app.models.user import UserInfo
from app.models.server import ServerAccount
from app.core.database import init_db
from app.core.tools import aes_encrypt

async def create_account():
    await init_db()
    
    # 查找用户
    user = await UserInfo.get(email='zhiyu')
    
    # 创建账号（替换为实际的用户名和密码）
    encrypted_password = aes_encrypt('your_password', str(user.id))
    account = await ServerAccount.create(
        username='your_username',
        password=encrypted_password,
        user_id=user.id
    )
    
    print(f"✓ 账号创建成功: {account.username}")

asyncio.run(create_account())
```

## 预期结果

### 有账号时的日志

```
INFO: 生成代理URL - 用户ID: xxx, 用户信息: {...}
INFO: 找到服务器账号 - 用户名: your_username
INFO: 密码解密成功
```

### 无账号时的日志

```
INFO: 生成代理URL - 用户ID: xxx, 用户信息: {...}
WARNING: 未找到用户 xxx 的服务器账号，使用默认账号密码
```

## 验证

创建账号后：
1. 刷新前端页面
2. 点击"复制代理"
3. 检查 URL 格式：`http://your_username:your_password@host:port`

## 详细文档

查看 `PROXY_URL_DEBUG_GUIDE.md` 获取完整的调试指南。
