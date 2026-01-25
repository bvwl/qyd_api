# 批量创建钱包功能

## 功能概述

实现了批量创建区块链钱包的功能，支持ETH和Solana两种链，私钥和助记词使用AES加密存储，只有管理员可以查看解密后的敏感信息。

## 核心特性

### 1. 批量创建钱包
- 支持一次创建1-100个钱包
- 支持ETH（以太坊）和Solana两种链
- 自动生成私钥、公钥和助记词
- 私钥和助记词自动加密存储

### 2. AES加密机制
- **加密密钥**: MD5(项目名称 + "9527")
- **加密IV**: MD5("9527" + 项目名称) 取前16位
- **加密算法**: AES-128-CBC
- **编码方式**: Base64

### 3. 权限控制
- **创建权限**: 仅ADMIN角色可以批量创建钱包
- **查看权限**: 
  - ADMIN: 自动解密，可查看明文私钥和助记词
  - 其他角色: 只能看到加密后的数据

## API接口

### 1. 批量创建钱包

**接口**: `POST /api/v1/project/wallet/batch`

**权限**: 仅ADMIN

**请求参数**:
```json
{
  "project_name": "项目名称",
  "chain": "eth",  // 或 "solana"
  "count": 10,     // 1-100
  "remark": "备注信息（可选）"
}
```

**响应示例**:
```json
{
  "message": "成功创建 10 个钱包",
  "count": 10,
  "items": [
    {
      "id": "uuid",
      "private_key": "加密后的私钥",
      "public_key": "0x1234...",
      "mnemonic": "加密后的助记词",
      "chain": "eth",
      "remark": "备注",
      "create_time": "2026-01-25 10:00:00"
    }
  ]
}
```

### 2. 获取钱包详情

**接口**: `GET /api/v1/project/wallet/{id}`

**权限**: 所有登录用户

**行为**:
- ADMIN角色: 返回解密后的私钥和助记词
- 其他角色: 返回加密后的数据

**响应示例（ADMIN）**:
```json
{
  "id": "uuid",
  "private_key": "0xabcd1234...",  // 已解密
  "public_key": "0x1234...",
  "mnemonic": "word1 word2 word3...",  // 已解密
  "chain": "eth",
  "create_time": "2026-01-25 10:00:00"
}
```

### 3. 获取钱包列表

**接口**: `GET /api/v1/project/wallet`

**权限**: 所有登录用户

**查询参数**:
- `chain`: 链类型过滤（可选）
- `project_id`: 项目ID过滤（可选）
- `page`: 页码（默认1）
- `limit`: 每页数量（默认10，最大1000）

**行为**:
- ADMIN角色: 返回所有钱包，自动解密
- GM角色: 返回所有钱包，不解密
- IT/MANUAL角色: 只返回分配给该用户的项目的钱包，不解密

## 技术实现

### 1. 加密工具函数

```python
# backend/app/core/tools.py

def aes_encrypt_wallet(plaintext: str, project_name: str) -> str:
    """
    使用AES加密钱包敏感数据
    - key: MD5(项目名称 + "9527")
    - iv: MD5("9527" + 项目名称) 取前16位
    """
    key_string = f"{project_name}9527"
    key = hashlib.md5(key_string.encode('utf-8')).digest()
    
    iv_string = f"9527{project_name}"
    iv = hashlib.md5(iv_string.encode('utf-8')).digest()[:16]
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = pad(plaintext.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    
    return base64.b64encode(ciphertext).decode('utf-8')


def aes_decrypt_wallet(ciphertext: str, project_name: str) -> str:
    """
    使用AES解密钱包敏感数据
    """
    key_string = f"{project_name}9527"
    key = hashlib.md5(key_string.encode('utf-8')).digest()
    
    iv_string = f"9527{project_name}"
    iv = hashlib.md5(iv_string.encode('utf-8')).digest()[:16]
    
    encrypted_data = base64.b64decode(ciphertext)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = cipher.decrypt(encrypted_data)
    plaintext = unpad(padded_plaintext, AES.block_size)
    
    return plaintext.decode('utf-8')
```

### 2. 钱包客户端

```python
# backend/app/clients/wallet.py

class WalletClient:
    async def eth_create(self):
        """创建ETH钱包"""
        Account.enable_unaudited_hdwallet_features()
        account, mnemonic = Account.create_with_mnemonic()
        address = account.address
        private_key = account._private_key.hex()
        return private_key, address, mnemonic
    
    async def solana_create(self):
        """创建Solana钱包"""
        signing = SigningKey.generate()
        public_key = base58.b58encode(signing.verify_key.encode()).decode('utf-8')
        private_key = base58.b58encode(signing._signing_key).decode('utf-8')
        return private_key, public_key, None
```

### 3. CRUD批量创建

```python
# backend/app/crud/project/wallet.py

async def batch_create(self, item: BatchCreate) -> BatchCreateOut:
    """批量创建钱包"""
    chain = item.chain.lower()
    if chain not in ['eth', 'solana']:
        raise ValueError('链类型只支持 eth 或 solana')
    
    wallet_client = WalletClient()
    created_wallets = []
    
    for i in range(item.count):
        # 创建钱包
        if chain == 'eth':
            private_key, public_key, mnemonic = await wallet_client.eth_create()
        else:
            private_key, public_key, mnemonic = await wallet_client.solana_create()
        
        # 加密敏感数据
        encrypted_private_key = aes_encrypt_wallet(private_key, item.project_name)
        encrypted_mnemonic = aes_encrypt_wallet(mnemonic, item.project_name) if mnemonic else None
        
        # 保存到数据库
        wallet = await ProjectWallet.create(
            private_key=encrypted_private_key,
            public_key=public_key,
            mnemonic=encrypted_mnemonic,
            chain=chain,
            remark=item.remark
        )
        created_wallets.append(wallet)
    
    return BatchCreateOut(
        message=f'成功创建 {len(created_wallets)} 个钱包',
        count=len(created_wallets),
        items=[Out.model_validate(w) for w in created_wallets]
    )
```

### 4. API自动解密

```python
# backend/app/apis/v1/project/wallet.py

@app.get("/{id}")
async def get(id: UUID, current_user: dict = Depends(get_current_user)):
    """获取钱包详情（ADMIN自动解密）"""
    obj = await project_wallet_crud.get(id)
    
    # 检查是否是管理员
    user_roles = current_user.get('roles', [])
    is_admin = 'ADMIN' in user_roles
    
    # 如果是管理员，自动解密
    if is_admin and obj.project:
        project = await ProjectInfo.get_or_none(id=obj.project.id)
        if project:
            obj.private_key = aes_decrypt_wallet(obj.private_key, project.name)
            if obj.mnemonic:
                obj.mnemonic = aes_decrypt_wallet(obj.mnemonic, project.name)
    
    return obj
```

## 使用示例

### 1. 批量创建ETH钱包

```bash
curl -X POST "http://localhost:6080/api/v1/project/wallet/batch" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "DeFi项目A",
    "chain": "eth",
    "count": 10,
    "remark": "用于测试的ETH钱包"
  }'
```

### 2. 批量创建Solana钱包

```bash
curl -X POST "http://localhost:6080/api/v1/project/wallet/batch" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "NFT项目B",
    "chain": "solana",
    "count": 5,
    "remark": "用于NFT铸造"
  }'
```

### 3. 查看钱包详情（管理员）

```bash
curl -X GET "http://localhost:6080/api/v1/project/wallet/{wallet_id}" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 4. 查看钱包列表（管理员）

```bash
curl -X GET "http://localhost:6080/api/v1/project/wallet?chain=eth&limit=20" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 测试

运行测试脚本：

```bash
cd backend
python test_batch_wallet_creation.py
```

测试内容：
1. ✓ 批量创建ETH钱包
2. ✓ 批量创建Solana钱包
3. ✓ 验证加密存储
4. ✓ 验证管理员自动解密
5. ✓ 验证权限控制

## 安全说明

### 1. 加密存储
- 所有私钥和助记词都经过AES加密后存储
- 每个项目使用不同的加密密钥
- 数据库中不存储明文敏感信息

### 2. 权限控制
- 只有ADMIN角色可以批量创建钱包
- 只有ADMIN角色可以查看解密后的私钥和助记词
- 其他角色只能看到加密后的数据

### 3. 密钥管理
- 加密密钥基于项目名称动态生成
- 不需要额外的密钥管理系统
- 项目名称作为密钥的一部分，需要妥善保管

### 4. 最佳实践
- 定期备份钱包数据
- 限制ADMIN角色的分配
- 记录所有钱包访问日志
- 使用HTTPS传输数据

## 数据库结构

```sql
-- 项目钱包表
CREATE TABLE project_wallet (
    id CHAR(36) PRIMARY KEY,
    private_key TEXT NOT NULL COMMENT '私钥（AES加密）',
    public_key TEXT NOT NULL COMMENT '公钥',
    mnemonic TEXT COMMENT '助记词（AES加密）',
    chain VARCHAR(255) NOT NULL COMMENT '链',
    remark VARCHAR(255) COMMENT '备注',
    project_id CHAR(36) COMMENT '所属项目ID',
    create_time DATETIME NOT NULL,
    update_time DATETIME NOT NULL,
    INDEX idx_chain_create_time (chain, create_time),
    INDEX idx_create_time (create_time)
);
```

## 依赖包

```txt
# 已包含在 requirements.txt 中
eth-account>=0.8.0      # ETH钱包生成
PyNaCl>=1.5.0          # Solana钱包生成
base58>=2.1.1          # Base58编码
pycryptodome>=3.18.0   # AES加密
```

## 常见问题

### Q1: 如何修改加密密钥？
A: 修改 `backend/app/core/tools.py` 中的 `aes_encrypt_wallet` 和 `aes_decrypt_wallet` 函数，更改密钥生成规则。注意：修改后需要重新加密所有现有数据。

### Q2: 如何支持更多链类型？
A: 在 `backend/app/clients/wallet.py` 中添加新的钱包创建方法，然后在 `batch_create` 中添加对应的处理逻辑。

### Q3: 如何导出钱包数据？
A: 使用管理员账号调用钱包列表API，会自动解密所有数据，然后可以导出为CSV或Excel。

### Q4: 忘记项目名称怎么办？
A: 项目名称是解密的关键，如果忘记则无法解密。建议：
- 在创建时记录项目名称
- 使用项目ID关联到项目表
- 定期备份项目名称映射关系

## 更新日志

### 2026-01-25
- ✓ 实现批量创建钱包功能
- ✓ 添加AES加密存储
- ✓ 实现管理员自动解密
- ✓ 添加权限控制
- ✓ 支持ETH和Solana两种链
- ✓ 添加测试脚本和文档

## 相关文件

- `backend/app/core/tools.py` - 加密工具函数
- `backend/app/clients/wallet.py` - 钱包客户端
- `backend/app/schemas/project/wallet.py` - 钱包Schema
- `backend/app/crud/project/wallet.py` - 钱包CRUD
- `backend/app/apis/v1/project/wallet.py` - 钱包API
- `backend/test_batch_wallet_creation.py` - 测试脚本
