# 下一步操作指南

## 🎯 目标

排查并修复代理 URL 未获取用户服务器账号的问题。

## 📋 在服务器上执行以下命令

### 1️⃣ 拉取最新代码

```bash
cd /opt/zy/qyd_api
git pull
```

### 2️⃣ 重启后端服务（应用调试日志）

```bash
docker compose -f docker-compose.backend.yml restart backend-api
```

### 2.5️⃣ 重新构建并重启前端（应用前端调试日志）

```bash
# 重新构建前端镜像
docker compose -f docker-compose.frontend.yml build frontend

# 重启前端服务
docker compose -f docker-compose.frontend.yml restart frontend
```

### 3️⃣ 检查用户服务器账号

```bash
# 进入容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 检查当前登录用户（替换 zhiyu 为实际的用户邮箱）
python check_server_account.py zhiyu

# 退出容器
exit
```

### 4️⃣ 查看实时日志

**后端日志**（在一个终端窗口）：

```bash
cd /opt/zy/qyd_api
docker compose -f docker-compose.backend.yml logs -f backend-api
```

保持这个窗口打开，然后在前端点击"复制代理"或"测试代理"，观察日志输出。

### 5️⃣ 查看前端浏览器控制台

1. 在浏览器中打开前端页面（http://192.168.13.6:8080）
2. 按 `F12` 打开开发者工具
3. 切换到 "Console"（控制台）标签
4. 刷新页面，查看输出：
   ```
   服务器列表数据: {...}
   第一条数据: {proxy_url: "...", proxy_type: "..."}
   ```
5. 点击"复制代理"按钮，查看输出：
   ```
   复制代理 - proxyUrl: ... proxyType: ...
   ```

**重要**：检查 `proxy_url` 字段是否有值！

---

## 🔍 根据检查结果采取行动

### 情况 A：浏览器控制台显示 proxy_url 为空或 undefined

**说明**：后端没有正确生成代理 URL

**解决方法**：检查用户是否有服务器账号

如果 `check_server_account.py` 显示"未找到服务器账号"，执行：

```bash
# 进入容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 启动 Python
python
```

在 Python 中执行（**替换用户名和密码为实际值**）：

```python
import asyncio
from app.models.user import UserInfo
from app.models.server import ServerAccount
from app.core.database import init_db
from app.core.tools import aes_encrypt

async def create_account():
    await init_db()
    user = await UserInfo.get(email='zhiyu')  # 替换为实际邮箱
    encrypted_password = aes_encrypt('your_password', str(user.id))  # 替换密码
    account = await ServerAccount.create(
        username='your_username',  # 替换用户名
        password=encrypted_password,
        user_id=user.id
    )
    print(f"✓ 账号创建成功: {account.username}")

asyncio.run(create_account())
```

按 `Ctrl+D` 退出 Python，然后 `exit` 退出容器。

### 情况 B：浏览器控制台显示 proxy_url 有值，但复制失败

**说明**：前端功能正常，可能是浏览器权限问题

**解决方法**：
1. 检查浏览器是否允许访问剪贴板
2. 尝试使用 HTTPS 访问（HTTP 可能限制剪贴板访问）
3. 手动复制代理 URL

### 情况 C：密码解密失败

如果日志显示"密码解密失败"，执行：

```bash
docker compose -f docker-compose.backend.yml exec backend-api python
```

```python
import asyncio
from app.models.user import UserInfo
from app.models.server import ServerAccount
from app.core.database import init_db
from app.core.tools import aes_encrypt

async def fix_password():
    await init_db()
    user = await UserInfo.get(email='zhiyu')  # 替换为实际邮箱
    account = await ServerAccount.get(user_id=user.id)
    account.password = aes_encrypt('your_password', str(user.id))  # 替换密码
    await account.save()
    print(f"✓ 密码重新加密成功")

asyncio.run(fix_password())
```

---

## ✅ 验证修复

1. 在前端刷新页面
2. 点击"复制代理"或"测试代理"
3. 检查代理 URL 是否包含正确的用户名和密码

**预期结果**：
```
http://your_username:your_password@192.168.13.6:25000
```

---

## 📚 详细文档

- `FRONTEND_PROXY_DEBUG.md` - 前端调试指南（新增）
- `PROXY_URL_ISSUE_SUMMARY.md` - 问题排查总结
- `PROXY_URL_DEBUG_GUIDE.md` - 后端完整调试指南
- `PROXY_URL_DEBUG_QUICK_REF.md` - 快速参考

---

## 💡 提示

- 所有命令都需要在 `/opt/zy/qyd_api` 目录下执行
- 替换示例中的用户名、密码、邮箱为实际值
- 如果遇到问题，查看日志获取更多信息
- 日志文件位置：`logs/api.log`
