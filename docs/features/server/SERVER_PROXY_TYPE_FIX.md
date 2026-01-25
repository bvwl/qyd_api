# 服务器代理类型自动识别功能

## 功能描述

根据服务器的代理端口自动识别代理类型（HTTP 或 SOCKS5），并生成相应格式的代理 URL。

## 端口范围规则

| 端口范围 | 代理类型 | URL 格式 |
|---------|---------|---------|
| 21999 < port < 29999 | HTTP | `http://username:password@host:port` |
| 31999 < port < 39999 | SOCKS5 | `socks5://username:password@host:port` |
| 其他 | SOCKS5（默认） | `socks5://username:password@host:port` |

## 实现细节

### 1. 后端修改

#### 文件：`backend/app/crud/server/info.py`

**修改 `_generate_proxy_url` 方法**：

```python
async def _generate_proxy_url(self, server: ServerInfo, current_user_id: UUID | None = None) -> tuple[str, str]:
    """
    生成代理URL和代理类型，使用当前用户的服务器账号
    
    Returns:
        tuple[str, str]: (proxy_url, proxy_type)
    """
    if server.port is None:
        return "", ""
    
    # 根据端口范围判断代理类型
    port = server.port
    if 21999 < port < 29999:
        proxy_type = "http"
        protocol = "http"
    elif 31999 < port < 39999:
        proxy_type = "socks5"
        protocol = "socks5"
    else:
        # 默认为 socks5
        proxy_type = "socks5"
        protocol = "socks5"
    
    # 获取当前用户的服务器账号
    username = "username"
    password = "password"
    
    if current_user_id:
        from app.models.server import ServerAccount
        
        try:
            account = await ServerAccount.get_or_none(user_id=current_user_id)
            if account:
                username = account.username
                # 解密密码
                try:
                    password = aes_decrypt(account.password, str(current_user_id))
                except Exception:
                    password = "password"
        except Exception:
            pass
    
    # 生成代理URL
    host = server.domain if server.domain else server.host
    proxy_url = f"{protocol}://{username}:{password}@{host}:{server.port}"
    
    return proxy_url, proxy_type
```

**更新所有调用处**：

```python
# 返回值从单个字符串改为元组
result.proxy_url, result.proxy_type = await self._generate_proxy_url(res, current_user_id)
```

#### 文件：`backend/app/schemas/server/info.py`

**添加 `proxy_type` 字段**：

```python
class Out(Base):
    """
    输出模型
    """
    message: str = Field('成功', description='提示信息')
    id: UUID = Field(..., description='ID')

    create_time: datetime = Field(..., description='创建时间')
    update_time: datetime = Field(..., description='更新时间')
    group_id: UUID = Field(..., description='分组ID')
    group: GroupBase = Field(..., description='分组信息')
    
    # proxy_url 和 proxy_type 将在 CRUD 层计算后设置
    proxy_url: str = Field("", description='代理URL')
    proxy_type: str = Field("", description='代理类型')  # ← 新增字段
```

### 2. 前端修改

#### 文件：`frontend/src/types/index.ts`

**添加 `proxy_type` 字段**：

```typescript
export interface ServerInfo {
  id: string
  host: string
  ssh_port?: number
  password?: string
  status: Status
  domain?: string
  is_sale: number
  port?: number
  proxy_url?: string  // 代理URL
  proxy_type?: string  // 代理类型 (http/socks5)  ← 新增字段
  group_id?: string
  group?: ServerGroup
  create_time: string
  update_time: string
}
```

#### 文件：`frontend/src/views/Server/ServerList.tsx`

**更新复制代理函数**：

```typescript
const handleCopyProxyUrl = (proxyUrl?: string, proxyType?: string) => {
  if (!proxyUrl) {
    message.warning('代理信息不可用')
    return
  }
  
  const typeText = proxyType === 'http' ? 'HTTP' : proxyType === 'socks5' ? 'SOCKS5' : ''
  
  navigator.clipboard.writeText(proxyUrl).then(() => {
    message.success(`${typeText} 代理信息已复制到剪贴板`)
  }).catch(() => {
    message.error('复制失败，请手动复制')
  })
}
```

**更新按钮调用**：

```typescript
<Button
  type="link"
  icon={<CopyOutlined />}
  onClick={() => handleCopyProxyUrl(record.proxy_url, record.proxy_type)}
  title={`复制${record.proxy_type === 'http' ? 'HTTP' : 'SOCKS5'}代理信息`}
>
  复制代理
</Button>
```

## API 返回示例

```json
{
  "message": "成功",
  "count": 51,
  "num": 10,
  "items": [
    {
      "host": "202.155.155.88",
      "port": 32024,
      "domain": "sd7.0n.lv",
      "proxy_url": "socks5://user_7914cbac:Yvlo1k5gP4sR@sd7.0n.lv:32024",
      "proxy_type": "socks5"
    },
    {
      "host": "202.155.155.88",
      "port": 22024,
      "domain": "sd7.0n.lv",
      "proxy_url": "http://user_7914cbac:Yvlo1k5gP4sR@sd7.0n.lv:22024",
      "proxy_type": "http"
    }
  ]
}
```

## 使用效果

### 复制 HTTP 代理

1. 端口在 22000-28999 范围内
2. 点击"复制代理"按钮
3. 提示：`HTTP 代理信息已复制到剪贴板`
4. 复制内容：`http://username:password@host:port`

### 复制 SOCKS5 代理

1. 端口在 32000-38999 范围内
2. 点击"复制代理"按钮
3. 提示：`SOCKS5 代理信息已复制到剪贴板`
4. 复制内容：`socks5://username:password@host:port`

## 按钮提示

鼠标悬停在"复制代理"按钮上时，会显示：
- HTTP 代理：`复制HTTP代理信息`
- SOCKS5 代理：`复制SOCKS5代理信息`

## 代理 URL 格式

### HTTP 代理

```
http://username:password@host:port
```

示例：
```
http://user_7914cbac:Yvlo1k5gP4sR@sd7.0n.lv:22024
```

### SOCKS5 代理

```
socks5://username:password@host:port
```

示例：
```
socks5://user_7914cbac:Yvlo1k5gP4sR@sd7.0n.lv:32024
```

## 域名优先级

生成代理 URL 时，优先使用域名：
- 如果 `domain` 字段有值，使用 `domain`
- 如果 `domain` 为空，使用 `host`（IP 地址）

## 用户账号

代理 URL 中的用户名和密码来自当前登录用户的服务器账号：
- 如果用户有服务器账号，使用该账号的用户名和密码
- 如果用户没有服务器账号，使用默认值 `username:password`

## 注意事项

1. **端口范围**：
   - HTTP: 21999 < port < 29999
   - SOCKS5: 31999 < port < 39999
   - 其他端口默认为 SOCKS5

2. **密码解密**：
   - 服务器账号密码使用 AES 加密存储
   - 生成代理 URL 时自动解密

3. **域名优先**：
   - 优先使用域名而不是 IP 地址
   - 域名通常更稳定且支持 HTTPS

4. **用户隔离**：
   - 每个用户看到的代理 URL 包含自己的账号信息
   - 不同用户复制的代理 URL 不同

## 相关文件

- `backend/app/crud/server/info.py` - 服务器信息 CRUD（代理 URL 生成逻辑）
- `backend/app/schemas/server/info.py` - 服务器信息 Schema
- `frontend/src/views/Server/ServerList.tsx` - 服务器列表页面
- `frontend/src/types/index.ts` - 前端类型定义

## 测试验证

### 测试命令

```bash
curl -s 'http://127.0.0.1:6080/v1/server/info?page=1&limit=5&res_count=true' \
  -H 'Authorization: Bearer <token>' | python -m json.tool
```

### 测试结果

重启后端服务后，测试通过：

```json
{
  "port": 22024,
  "proxy_url": "http://user_7914cbac:Yvlo1k5gP4sR@sd7.0n.lv:22024",
  "proxy_type": "http"
}
{
  "port": 32024,
  "proxy_url": "socks5://user_7914cbac:Yvlo1k5gP4sR@sd7.0n.lv:32024",
  "proxy_type": "socks5"
}
```

✅ HTTP端口（22000-28999）正确生成 `http://` 协议  
✅ SOCKS5端口（32000-38999）正确生成 `socks5://` 协议  
✅ 域名优先于IP地址  
✅ `proxy_type` 字段正确返回  

### 重要提示

**修改后端代码后必须重启服务才能生效！**

```bash
# 查找进程
ps aux | grep "python.*start.py" | grep -v grep

# 停止服务
kill <PID>

# 启动服务
cd backend && python start.py
```

## 完成时间

2026-01-25 23:37
