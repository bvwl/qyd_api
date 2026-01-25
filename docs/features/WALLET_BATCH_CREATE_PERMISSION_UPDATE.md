# 批量创建钱包权限更新

## 更新日期
2026-01-26

## 更新内容

将批量创建钱包功能从"仅管理员可用"改为"所有登录用户可用"。

## 修改文件

### 1. 后端 API 权限修改

**文件**: `backend/app/apis/v1/project/wallet.py`

**修改内容**:
- 将 `/batch` 端点的依赖从 `get_admin_user` 改为 `get_current_user`
- 更新文档说明：从"仅管理员"改为"所有用户可用"

```python
# 修改前
async def batch_create(
    item: BatchCreate = Body(..., description="批量创建参数"),
    admin_user: dict = Depends(get_admin_user)  # 仅管理员
):
    """批量创建钱包（仅管理员）"""

# 修改后
async def batch_create(
    item: BatchCreate = Body(..., description="批量创建参数"),
    current_user: dict = Depends(get_current_user)  # 所有登录用户
):
    """批量创建钱包（所有用户可用）"""
```

### 2. 前端权限检查移除

**文件**: `frontend/src/views/Project/WalletBatchCreate.tsx`

**修改内容**:
- 移除管理员角色检查逻辑
- 移除"权限不足"提示组件
- 移除未使用的 `useUserStore` 导入
- 更新功能说明，添加"所有登录用户均可使用此功能"

```typescript
// 移除的代码
const isAdmin = userStore.userInfo?.roles?.some((role: any) => role.code === 'ADMIN') || false

if (!isAdmin) {
  return (
    <Alert
      message="权限不足"
      description="只有管理员可以批量创建钱包"
      type="warning"
      showIcon
    />
  )
}
```

## 功能说明

### API 端点
- **路径**: `POST /api/v1/project/wallet/batch`
- **权限**: 所有登录用户（需要有效的 JWT Token 或 API Token）
- **限制**: 单次创建 1-100 个钱包

### 参数说明
```json
{
  "project_name": "项目名称",  // 用于加密私钥和助记词
  "chain": "ETH",             // 链类型：ETH 或 SOL
  "count": 10,                // 创建数量：1-100
  "remark": "备注信息"         // 可选
}
```

### 安全特性
1. **加密存储**: 私钥和助记词使用 AES 加密存储到数据库
2. **加密密钥**: MD5(项目名称 + "9527")
3. **加密 IV**: MD5("9527" + 项目名称) 取前16位
4. **前端临时显示**: 创建后在前端显示 10 分钟，之后自动清除
5. **数据库永久保存**: 钱包数据加密保存在数据库中
6. **管理员特权**: 只有管理员查询钱包时会自动解密显示明文

### 使用流程
1. 登录系统（任何角色）
2. 进入"项目管理" -> "批量创建钱包"
3. 填写项目名称、选择链类型、设置创建数量
4. 点击"批量创建钱包"
5. 创建成功后，前端显示钱包列表（10分钟有效期）
6. 可以下载为 Excel 文件保存（包含明文私钥和助记词）
7. 钱包数据已加密保存到数据库

## 权限对比

| 功能 | 修改前 | 修改后 |
|------|--------|--------|
| 批量创建钱包 | 仅 ADMIN | 所有登录用户 |
| 查看加密钱包 | 所有登录用户 | 所有登录用户 |
| 查看解密钱包 | 仅 ADMIN | 仅 ADMIN |
| 删除钱包 | 仅 ADMIN | 仅 ADMIN |

## 测试建议

### 1. 测试不同角色的访问
```bash
# 使用不同角色的用户登录测试
# - ADMIN
# - GM
# - IT
# - MANUAL
```

### 2. 测试 API 调用
```bash
# 使用 JWT Token
curl -X POST "http://localhost:6080/api/v1/project/wallet/batch" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "测试项目",
    "chain": "ETH",
    "count": 5
  }'

# 使用 API Token
curl -X POST "http://localhost:6080/api/v1/project/wallet/batch" \
  -H "API-TOKEN: YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "测试项目",
    "chain": "SOL",
    "count": 3
  }'
```

### 3. 验证加密存储
```python
# 检查数据库中的钱包是否加密
python backend/test_wallet_encryption.py
```

## 注意事项

1. **项目名称重要性**: 项目名称用于加密，请妥善保管，丢失后无法解密
2. **下载及时性**: 前端临时数据 10 分钟后清除，请及时下载 Excel 文件
3. **文件安全**: 下载的 Excel 文件包含明文私钥和助记词，请妥善保管
4. **数据库备份**: 定期备份数据库，防止数据丢失
5. **权限审计**: 虽然所有用户都可以创建，但建议定期审计创建记录

## 相关文档

- [钱包功能更新](./WALLET_FEATURE_UPDATE.md)
- [项目账户加密](../encryption/PROJECT_ACCOUNT_ENCRYPTION.md)
- [API 认证完整文档](../api/API_AUTH_COMPLETE.md)
- [开发规范](../../.kiro/steering/conventions.md)
