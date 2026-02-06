# XUI 登录 500 错误诊断指南

## 问题现象

从日志看到：
```
ERROR 2026-01-27 12:58:23 请求失败: POST https://zd16.0n.lv:10010/web3/login, 错误:
WARNING 正在重试 login 2/3 因错误: 登录失败，HTTP 状态码: 500
```

**好消息**：代理已经工作（curl 显示美国 IP）  
**问题**：XUI 面板登录返回 500 错误

## 可能的原因

### 1. 用户名或密码错误
XUI 面板返回 500 可能是因为认证失败。

**检查方法**：
```bash
# 在容器中测试
docker exec -it qyd-backend-api python -c "
import asyncio
from app.core.database import init_db
from app.models.xui import XuiServer
from app.core.tools import aes_decrypt

async def check():
    await init_db()
    servers = await XuiServer.all()
    for s in servers:
        print(f'服务器: {s.name}')
        print(f'  用户名: {s.username}')
        try:
            pwd = aes_decrypt(s.password, s.host)
            print(f'  密码: {pwd}')
        except:
            print(f'  密码: 解密失败')
        print()

asyncio.run(check())
"
```

### 2. web_path 配置错误
数据库中的 `web_path` 字段可能不正确。

**检查方法**：
```bash
# 查看数据库配置
docker exec -it qyd-backend-api python -c "
import asyncio
from app.core.database import init_db
from app.models.xui import XuiServer

async def check():
    await init_db()
    servers = await XuiServer.all()
    for s in servers:
        protocol = 'https' if s.is_ssl else 'http'
        host = s.domain if s.domain else s.host
        print(f'{s.name}: {protocol}://{host}:{s.port}{s.web_path}/login')

asyncio.run(check())
"
```

### 3. XUI 面板版本不兼容
不同版本的 XUI 面板 API 可能不同。

**常见的 web_path**：
- `/web3` - 新版本（默认）
- `` (空) - 旧版本
- `/xui` - 某些自定义版本

### 4. XUI 面板本身有问题
面板可能崩溃或配置错误。

**检查方法**：
```bash
# 直接用 curl 测试
curl -X POST "https://zd16.0n.lv:10010/web3/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=你的用户名&password=你的密码" \
  -k -v
```

## 解决方案

### 方案 1: 更新数据库中的 web_path

如果 XUI 面板不使用 `/web3` 前缀：

```sql
-- 连接到数据库
mysql -h 192.168.1.30 -u qyd -p qyd

-- 查看当前配置
SELECT id, name, host, port, web_path FROM xui_server;

-- 更新 web_path（如果面板不使用前缀）
UPDATE xui_server SET web_path = '' WHERE id = '你的服务器ID';

-- 或者更新为其他路径
UPDATE xui_server SET web_path = '/xui' WHERE id = '你的服务器ID';
```

### 方案 2: 手动测试不同的路径

```bash
# 测试 /web3/login
curl -X POST "https://zd16.0n.lv:10010/web3/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=yourpassword" \
  -k

# 测试 /login（无前缀）
curl -X POST "https://zd16.0n.lv:10010/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=yourpassword" \
  -k

# 测试 /xui/login
curl -X POST "https://zd16.0n.lv:10010/xui/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=yourpassword" \
  -k
```

### 方案 3: 检查 XUI 面板日志

登录到 XUI 面板所在的服务器：

```bash
# 查看 XUI 日志
docker logs <xui-container-name>

# 或者
journalctl -u x-ui -f
```

### 方案 4: 验证用户名密码

1. 在浏览器中访问 XUI 面板
2. 使用数据库中的用户名密码登录
3. 如果无法登录，说明密码不正确

## 快速诊断脚本

```bash
# 1. 检查数据库配置
docker exec -it qyd-backend-api python -c "
import asyncio
from app.core.database import init_db
from app.models.xui import XuiServer
from app.core.tools import aes_decrypt

async def main():
    await init_db()
    servers = await XuiServer.all()
    for s in servers:
        protocol = 'https' if s.is_ssl else 'http'
        host = s.domain if s.domain else s.host
        pwd = aes_decrypt(s.password, s.host)
        print(f'服务器: {s.name}')
        print(f'  URL: {protocol}://{host}:{s.port}{s.web_path}')
        print(f'  用户名: {s.username}')
        print(f'  密码: {pwd}')
        print()

asyncio.run(main())
"

# 2. 测试登录（替换为实际值）
curl -X POST "https://zd16.0n.lv:10010/web3/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=实际用户名&password=实际密码" \
  -k -v
```

## 常见错误码含义

- **500**: 服务器内部错误
  - 可能是用户名/密码错误
  - 可能是 XUI 面板崩溃
  - 可能是数据库连接失败

- **404**: 路径不存在
  - `web_path` 配置错误
  - XUI 面板版本不匹配

- **401/403**: 认证失败
  - 用户名或密码错误
  - Token 过期

## 下一步

1. 先运行快速诊断脚本，获取实际的登录 URL 和凭据
2. 用 curl 手动测试登录
3. 根据返回结果调整 `web_path` 配置
4. 重启服务测试

## 参考

- XUI 面板文档: https://github.com/vaxilu/x-ui
- 3X-UI 文档: https://github.com/MHSanaei/3x-ui
