# 批量创建钱包功能 - 完整安装指南

## 功能概述

批量创建钱包功能允许管理员一次性创建多个区块链钱包（ETH 或 SOL），私钥和助记词自动加密存储到数据库。

## 功能特性

### ✅ 已实现

1. **批量创建**：一次创建 1-100 个钱包
2. **多链支持**：支持 ETH（以太坊）和 SOL（Solana）
3. **大写简写**：链类型使用大写简写（ETH、SOL）
4. **大小写不敏感**：输入 eth/ETH/Eth 都会转换为 ETH
5. **自动加密**：私钥和助记词使用 AES 加密存储
6. **自动解密**：API 返回时自动解密（仅 ADMIN）
7. **数据持久化**：钱包自动保存到数据库
8. **前端显示**：10 分钟临时显示，支持显示/隐藏切换
9. **Excel 导出**：支持导出为 Excel 文件
10. **权限控制**：只有 ADMIN 可以批量创建

## 链类型说明

### ETH (以太坊)
- **简写**：ETH（大写）
- **输入**：eth/ETH/Eth（大小写不敏感）
- **存储**：ETH（统一转换为大写）
- **包含**：私钥、公钥、助记词

### SOL (Solana)
- **简写**：SOL（大写）
- **输入**：sol/SOL/Sol（大小写不敏感）
- **存储**：SOL（统一转换为大写）
- **包含**：私钥、公钥（无助记词）

## API 使用

### 请求示例

#### 创建 ETH 钱包
```bash
curl -X POST 'http://127.0.0.1:6080/v1/project/wallet/batch' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{
    "project_name": "test",
    "chain": "ETH",
    "count": 10,
    "remark": "测试批量创建"
  }'
```

#### 创建 SOL 钱包
```bash
curl -X POST 'http://127.0.0.1:6080/v1/project/wallet/batch' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{
    "project_name": "test",
    "chain": "SOL",
    "count": 5
  }'
```

### 响应示例

#### ETH 钱包响应
```json
{
  "message": "成功创建 1 个钱包",
  "count": 1,
  "items": [
    {
      "private_key": "aa8c0782b9fdf55f325d2031c7412ae46fd05bc85ee5e1d9b67026447a90ee3c",
      "public_key": "0x629859DBae2d828eC8F13f33fCe90967c8CdC38A",
      "mnemonic": "ocean bring fancy palace case essence figure must demise excite timber bleak",
      "chain": "ETH",
      "remark": null,
      "message": "成功",
      "id": "7b830818-1ee0-4d61-9126-c63593c3686e",
      "create_time": "2026-01-25 17:44:32",
      "update_time": "2026-01-25 17:44:32",
      "project_id": null,
      "project": null
    }
  ]
}
```

#### SOL 钱包响应
```json
{
  "message": "成功创建 1 个钱包",
  "count": 1,
  "items": [
    {
      "private_key": "9qB5QwFMkiyz21Erdb7NtDfvkWwLs1h5FNoBJ3CCJYsCTHnbfa3zBoHTC5TgP7xo3znM8MjejUP1JMeiPBwZBPw",
      "public_key": "FiAMbxLQak1G93ijZt8juDFjUfQVVGUpD6JCw72mCury",
      "mnemonic": null,
      "chain": "SOL",
      "remark": null,
      "message": "成功",
      "id": "ed45a55a-680b-4773-b7ff-a614423e0ba0",
      "create_time": "2026-01-25 17:44:43",
      "update_time": "2026-01-25 17:44:43",
      "project_id": null,
      "project": null
    }
  ]
}
```

## 前端使用

### 访问路径
- **菜单**：项目管理 → 批量创建钱包
- **URL**：`/project/wallet/batch-create`

### 使用步骤

1. **登录系统**（使用 ADMIN 账号）
2. **进入页面**：项目管理 → 批量创建钱包
3. **填写表单**：
   - 项目名称：用于加密（必填）
   - 链类型：选择 ETH 或 SOL
   - 创建数量：1-100
   - 备注：可选
4. **点击创建**：系统自动创建并保存
5. **查看结果**：
   - 表格显示创建的钱包
   - 私钥/助记词默认隐藏
   - 点击眼睛图标显示/隐藏
   - 支持一键复制
6. **下载备份**：点击"下载钱包"导出 Excel
7. **10分钟后**：前端临时数据自动清除

### 前端界面

```
┌─────────────────────────────────────────────────────────┐
│ 批量创建钱包                                              │
├─────────────────────────────────────────────────────────┤
│ 功能说明：                                                │
│ 1. 支持批量创建 ETH 和 SOL 钱包                           │
│ 2. 私钥和助记词使用 AES 加密存储到数据库                   │
│ 3. 创建后的钱包会自动保存到数据库，同时在前端临时显示 10 分钟 │
│ 4. 可以下载为 Excel 文件（包含明文私钥和助记词）           │
│ 5. 10分钟后前端临时数据会清除，但数据库中的钱包仍然保留    │
├─────────────────────────────────────────────────────────┤
│ 项目名称: [__________]  链类型: [ETH ▼]  数量: [10]      │
│ 备注: [_____________________________________________]    │
│ [批量创建钱包]                                            │
├─────────────────────────────────────────────────────────┤
│ 创建数量: 10 个  |  剩余时间: 9:58  |  [下载钱包]         │
├─────────────────────────────────────────────────────────┤
│ 序号 | 链  | 公钥          | 私钥          | 助记词        │
│  1   | ETH | 0x629859... | ••••••••••• | ••••••••••• │
│  2   | ETH | 0xFAb04A... | ••••••••••• | ••••••••••• │
└─────────────────────────────────────────────────────────┘
```

## 技术实现

### 后端实现

#### 1. 链类型验证和转换
```python
# backend/app/crud/project/wallet.py
chain_upper = item.chain.upper()  # 转换为大写
if chain_upper not in ['ETH', 'SOL']:
    raise ValueError('链类型只支持 ETH 或 SOL')
```

#### 2. 钱包创建
```python
if chain_upper == 'ETH':
    private_key, public_key, mnemonic = await wallet_client.eth_create()
else:  # SOL
    private_key, public_key, mnemonic = await wallet_client.solana_create()
```

#### 3. 加密存储
```python
encrypted_private_key = aes_encrypt_wallet(private_key, item.project_name)
encrypted_mnemonic = aes_encrypt_wallet(mnemonic, item.project_name) if mnemonic else None

wallet = await ProjectWallet.create(
    private_key=encrypted_private_key,
    public_key=public_key,
    mnemonic=encrypted_mnemonic,
    chain=chain_upper,  # 存储大写链类型
    remark=item.remark
)
```

#### 4. 自动解密返回
```python
wallet_dict = {
    'id': wallet.id,
    'private_key': aes_decrypt_wallet(wallet.private_key, item.project_name),
    'public_key': wallet.public_key,
    'mnemonic': aes_decrypt_wallet(wallet.mnemonic, item.project_name) if wallet.mnemonic else None,
    'chain': wallet.chain,  # 返回大写链类型
    # ...
}
```

### 前端实现

#### 1. 链类型选择
```typescript
<Select>
  <Select.Option value="ETH">ETH (以太坊)</Select.Option>
  <Select.Option value="SOL">SOL (Solana)</Select.Option>
</Select>
```

#### 2. 默认值
```typescript
initialValues={{
  chain: 'ETH',  // 默认选择 ETH
  count: 10
}}
```

#### 3. 链类型显示
```typescript
{
  title: '链',
  dataIndex: 'chain',
  key: 'chain',
  width: 100
  // 直接显示，不需要转换（后端已返回大写）
}
```

## 数据库存储

### 表结构
```sql
CREATE TABLE project_wallet (
    id VARCHAR(36) PRIMARY KEY,
    private_key TEXT NOT NULL,        -- AES 加密
    public_key VARCHAR(255) NOT NULL,
    mnemonic TEXT,                    -- AES 加密（SOL 为 NULL）
    chain VARCHAR(20) NOT NULL,       -- 存储大写：ETH、SOL
    remark TEXT,
    project_id VARCHAR(36),
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL
);
```

### 存储示例
```
| id   | chain | public_key      | private_key (加密) | mnemonic (加密) |
|------|-------|-----------------|-------------------|-----------------|
| uuid | ETH   | 0x629859...     | encrypted_data    | encrypted_data  |
| uuid | SOL   | FiAMbxLQak...   | encrypted_data    | NULL            |
```

## 加密说明

### 加密算法
- **算法**：AES-256-CBC
- **密钥**：MD5(项目名称 + "9527")
- **IV**：MD5("9527" + 项目名称) 取前 16 位
- **编码**：Base64

### 加密字段
- ✅ 私钥（private_key）
- ✅ 助记词（mnemonic，SOL 无助记词）
- ❌ 公钥（public_key，明文存储）

### 解密权限
- **ADMIN**：自动解密，返回明文
- **其他角色**：返回加密数据

## 相关文件

### 后端
```
backend/
├── app/
│   ├── apis/v1/project/wallet.py      # API 端点
│   ├── crud/project/wallet.py         # CRUD 方法
│   ├── schemas/project/wallet.py      # 数据模型
│   ├── core/tools.py                  # 加密/解密工具
│   └── clients/wallet.py              # 钱包生成客户端
└── db/
    ├── init_routes.py                 # 路由初始化
    └── bind_admin_routes.py           # 权限绑定
```

### 前端
```
frontend/
├── src/
│   ├── App.tsx                        # 路由配置
│   ├── views/Project/
│   │   └── WalletBatchCreate.tsx     # 页面组件
│   ├── api/project.ts                 # API 调用
│   └── components/Layout/index.tsx    # 菜单配置
```

## 测试验证

### 后端测试

#### 测试 ETH 钱包（大写）
```bash
curl -X POST 'http://127.0.0.1:6080/v1/project/wallet/batch' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{"project_name":"test","chain":"ETH","count":1}'
```

#### 测试 ETH 钱包（小写）
```bash
curl -X POST 'http://127.0.0.1:6080/v1/project/wallet/batch' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{"project_name":"test","chain":"eth","count":1}'
```

#### 测试 SOL 钱包
```bash
curl -X POST 'http://127.0.0.1:6080/v1/project/wallet/batch' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -d '{"project_name":"test","chain":"SOL","count":1}'
```

### 前端测试

1. 刷新浏览器（Ctrl + Shift + R）
2. 登录 ADMIN 账号
3. 访问：项目管理 → 批量创建钱包
4. 测试创建 ETH 钱包
5. 测试创建 SOL 钱包
6. 验证显示/隐藏功能
7. 验证复制功能
8. 验证下载功能

## 注意事项

1. **项目名称很重要**：用于加密密钥，请妥善保管
2. **链类型大小写**：输入大小写不敏感，存储统一为大写
3. **及时下载**：前端数据只保留 10 分钟，请及时下载 Excel
4. **数据库保留**：即使前端数据过期，数据库中的钱包仍然保留
5. **权限限制**：只有 ADMIN 可以创建和查看解密后的钱包
6. **Excel 安全**：导出的 Excel 包含明文私钥，请妥善保管
7. **SOL 无助记词**：Solana 钱包不包含助记词

## 故障排除

### 问题：链类型验证失败
**错误**：`链类型只支持 ETH 或 SOL`
**原因**：输入了不支持的链类型
**解决**：只能输入 ETH 或 SOL（大小写不敏感）

### 问题：前端显示小写链类型
**原因**：后端返回了小写链类型
**解决**：已修复，后端统一返回大写

### 问题：Excel 中链类型显示不一致
**原因**：前端导出时使用了原始数据
**解决**：已修复，直接使用后端返回的大写链类型

## 更新日志

### 2026-01-25 17:45
- ✅ 修改链类型为大写简写（ETH、SOL）
- ✅ 支持大小写不敏感输入
- ✅ 后端统一转换为大写存储
- ✅ 前端默认选择 ETH
- ✅ 移除前端 toUpperCase() 转换
- ✅ 测试验证功能正常

### 之前的更新
- ✅ 修复 Pydantic 验证错误
- ✅ 修复前端路由配置
- ✅ 实现批量创建功能
- ✅ 添加 AES 加密
- ✅ 创建前端页面
- ✅ 添加 Excel 导出

## 总结

批量创建钱包功能现在完全正常工作，链类型使用大写简写（ETH、SOL），输入大小写不敏感，存储统一为大写。

**主要改进**：
1. 链类型从 eth/solana 改为 ETH/SOL
2. 支持大小写不敏感输入（eth/ETH/Eth 都可以）
3. 后端统一转换为大写存储
4. 前端默认选择 ETH
5. 移除不必要的前端转换逻辑

现在可以正常使用批量创建钱包功能了！🎉
