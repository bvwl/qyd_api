# XUI 默认凭证说明

## 默认入站账号

创建 XUI 入站时，如果不指定 `default_username` 和 `default_password`，系统会使用以下默认值：

- **默认用户名**: `cqrxy`
- **默认密码**: `Zpaily88`

## 使用说明

### 1. 使用默认账号创建入站

```bash
POST /api/v1/xui/inbound
{
  "server_id": "uuid",
  "listen_host": "192.168.1.100",
  "listen_port": 21000,
  "protocol": 1
}
```

此时会自动使用默认账号 `cqrxy:Zpaily88` 创建入站。

### 2. 自定义账号创建入站

```bash
POST /api/v1/xui/inbound
{
  "server_id": "uuid",
  "listen_host": "192.168.1.100",
  "listen_port": 21000,
  "protocol": 1,
  "default_username": "custom_user",
  "default_password": "custom_pass"
}
```

### 3. 批量创建入站（使用默认账号）

```bash
POST /api/v1/xui/inbound/batch
{
  "server_id": "uuid",
  "inbounds": [
    {
      "listen_host": "192.168.1.100",
      "listen_port": 21000,
      "protocol": 1
    },
    {
      "listen_host": "192.168.1.100",
      "listen_port": 31000,
      "protocol": 2
    }
  ]
}
```

所有入站都会使用默认账号 `cqrxy:Zpaily88`。

## 数据库存储

- `default_username` 字段默认值为 `'cqrxy'`
- `default_password` 会使用 AES 加密存储，加密 key 为 `"listen_host:listen_port"`

## 安全建议

1. **生产环境**: 建议修改默认账号密码
2. **多账号管理**: 使用 `ServerAccount` 模型管理多个账号
3. **定期更换**: 定期更换入站密码以提高安全性

## 账号管理

除了默认账号，还可以通过以下方式管理入站账号：

### 1. 创建服务器账号
```bash
POST /api/v1/server/account
{
  "username": "user1",
  "password": "pass1"
}
```

### 2. 添加账号到入站
```bash
POST /api/v1/xui/account/add
{
  "inbound_id": "uuid",
  "account_id": "uuid"
}
```

### 3. 批量添加账号
```bash
POST /api/v1/xui/account/batch-add
{
  "inbound_id": "uuid",
  "account_ids": ["uuid1", "uuid2", "uuid3"]
}
```

这样可以为一个入站配置多个不同的账号，每个账号都可以独立管理。

## 注意事项

1. **默认账号**: 仅在创建入站时使用，后续可以通过添加 `ServerAccount` 来管理更多账号
2. **密码加密**: 所有密码都会加密存储，包括默认密码
3. **同步到 XUI**: 创建入站时会自动将默认账号同步到 XUI 面板
4. **账号隔离**: 不同入站的默认账号是独立的，互不影响
