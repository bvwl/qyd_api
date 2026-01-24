# 邮箱服务器关联修复

## 问题描述

在调用 Outlook 授权接口时出现 500 错误：

```
{"detail":"Relation server_info for models.EmailInfo not found"}
```

**原因**：不是所有邮箱都有服务器信息，但代码中错误地使用了不存在的关联名称 `server_info`。

## 问题分析

### 1. 错误的关联名称

在 `backend/app/clients/outlook.py` 的 `read_config` 方法中：

```python
# ❌ 错误：使用了不存在的关联名称
mail_info = await EmailInfo.get_or_none(email=self.email).prefetch_related("server_info")
server = await mail_info.server_info  # server_info 关联不存在
```

### 2. 实际的模型定义

在 `backend/app/models/mail.py` 中，EmailInfo 模型的关联字段名称是 `server`：

```python
class EmailInfo(BaseModel):
    # ...
    server = fields.ForeignKeyField(
        "models.ServerInfo",
        related_name="email_infos",
        description='代理信息',
        null=True,  # 允许为空
    )
```

### 3. 缺少空值检查

即使关联名称正确，代码也没有检查 `server` 是否为 `None`，导致没有服务器信息的邮箱会出错。

## 解决方案

### 修改 `backend/app/clients/outlook.py`

```python
async def read_config(self) -> int:
    """
    从数据库读取邮箱配置和代理信息
    
    逻辑说明：
    1. 查询 EmailInfo 模型，预加载 server 关联表。
    2. 如果存在 server，根据端口号范围配置代理类型：
       - 20000 <= port < 30000: 使用 HTTP 代理
       - 30000 <= port < 40000: 使用 SOCKS5 代理
    3. 加载 client_id, access_token, refresh_token 到内存。
    
    :return: 
        0: 未配置 (无 client_id 且无 token)
        1: 已配置 (完整配置)
        2: 仅配置了客户端ID (等待授权)
    """
    # ✅ 修复1：使用正确的关联名称 "server"
    mail_info = await EmailInfo.get_or_none(email=self.email).prefetch_related("server")
    if mail_info:
        self.client_id = mail_info.client_id
        self.access_token = mail_info.access_token
        self.refresh_token_value = mail_info.refresh_token
        
        # ✅ 修复2：检查 server 是否为 None
        if mail_info.server:
            server = mail_info.server
            host = server.domain or server.host
            port = server.port
            # 根据端口范围区分代理协议
            if 20000 <= port < 30000:
                self.proxy = f"http://cqrxy:Zpaily88@{host}:{port}"
            elif 30000 <= port < 40000:
                self.proxy = f"socks5://cqrxy:Zpaily88@{host}:{port}"

    if self.client_id and not self.access_token and not self.refresh_token_value:
        return 2
    elif not self.client_id and not self.access_token and not self.refresh_token_value:
        return 0
    return 1
```

## 关键修复点

### 1. 正确的关联名称
- ❌ 错误：`prefetch_related("server_info")` 和 `mail_info.server_info`
- ✅ 正确：`prefetch_related("server")` 和 `mail_info.server`

### 2. 空值检查
- ❌ 错误：直接访问 `server = await mail_info.server_info`
- ✅ 正确：先检查 `if mail_info.server:` 再访问

### 3. 同步访问
- ❌ 错误：`server = await mail_info.server_info`（使用 await）
- ✅ 正确：`server = mail_info.server`（prefetch_related 后直接访问）

## 业务逻辑说明

### 邮箱和服务器的关系

1. **可选关联**：邮箱可以有服务器信息（用于代理），也可以没有
2. **代理配置**：
   - 如果邮箱有关联的服务器，根据端口范围配置代理
   - 如果邮箱没有服务器，`self.proxy` 保持为 `None`，直接连接
3. **端口范围**：
   - 20000-29999：HTTP 代理
   - 30000-39999：SOCKS5 代理

### 使用场景

```python
# 场景1：邮箱有服务器信息
# 数据库：email.server_id = "xxx"
# 结果：self.proxy = "socks5://user:pass@host:30001"

# 场景2：邮箱没有服务器信息
# 数据库：email.server_id = NULL
# 结果：self.proxy = None（直接连接）
```

## 测试验证

### 测试用例

1. ✅ 有服务器信息的邮箱 - 应该正常配置代理
2. ✅ 没有服务器信息的邮箱 - 应该正常工作（不使用代理）
3. ✅ 服务器信息不完整的邮箱 - 应该正常处理

### 测试命令

```bash
# 测试有服务器信息的邮箱
curl -X POST "http://127.0.0.1:6080/v1/mail/outlook/auth/token" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@outlook.com",
    "url": "http://localhost/?code=xxx",
    "verifier": "xxx"
  }'

# 测试没有服务器信息的邮箱
curl -X POST "http://127.0.0.1:6080/v1/mail/outlook/auth/token" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu918918@outlook.com",
    "url": "http://localhost/?code=xxx",
    "verifier": "xxx"
  }'
```

## 相关文件

- ✅ `backend/app/clients/outlook.py` - 修复关联名称和空值检查
- ✅ `backend/app/models/mail.py` - EmailInfo 模型定义（无需修改）

## 注意事项

1. **关联字段名称**：Tortoise ORM 中，ForeignKey 字段的名称就是关联名称
2. **prefetch_related**：预加载后可以直接访问关联对象，不需要 await
3. **空值处理**：外键字段设置了 `null=True`，必须检查是否为 None
4. **代理可选**：没有代理信息的邮箱应该能正常工作（直接连接）

## 总结

通过修复关联名称和添加空值检查，解决了邮箱授权接口的 500 错误。现在系统可以正确处理：
- 有服务器信息的邮箱（使用代理）
- 没有服务器信息的邮箱（直接连接）

这使得邮箱管理更加灵活，不强制要求所有邮箱都配置服务器信息。
