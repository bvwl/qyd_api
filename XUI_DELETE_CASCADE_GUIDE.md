# XUI 服务器删除级联关系说明

## 当前删除逻辑

### 1. 删除 XUI 服务器

**API**: `DELETE /v1/xui/server/{id}`

**删除前检查**：
- ✅ 检查是否有关联的入站配置
- ❌ 如果有入站，**拒绝删除**，提示：`该服务器下还有 {count} 个入站配置，请先删除入站`

**删除顺序**：
```
1. 先删除所有入站配置
2. 再删除 XUI 服务器
```

### 2. 删除入站配置

**API**: `DELETE /v1/xui/inbound/{id}`

**删除前检查**：
- ✅ 检查是否有关联的账号
- ❌ 如果有账号，**拒绝删除**，提示：`该入站下还有 {count} 个账号，请先移除账号`

**删除顺序**：
```
1. 先移除所有账号（从入站中移除）
2. 再删除入站配置
```

### 3. 从入站移除账号

**API**: `DELETE /v1/xui/user/inbound-account`

**操作**：
- ✅ 从入站中移除账号（删除多对多关系）
- ✅ 更新账号的 `is_all_inbound_added` 状态
- ❌ **不会删除账号本身**（账号仍然存在于 ServerAccount 表中）

## 完整删除流程

如果要完全删除一个 XUI 服务器及其所有关联数据：

```
步骤 1: 从所有入站移除账号
  - 进入"入站列表"
  - 对每个入站，点击"账号管理"
  - 移除所有账号

步骤 2: 删除所有入站
  - 在"入站列表"中
  - 删除该服务器的所有入站

步骤 3: 删除 XUI 服务器
  - 在"服务器列表"中
  - 删除该服务器
```

## 数据库关系

```
XuiServer (XUI 服务器)
  ↓ (一对多，无级联删除)
XuiInbound (入站配置)
  ↓ (多对多，通过中间表)
ServerAccount (服务器账号)
```

### 外键配置

```python
# XuiInbound 模型
server = fields.ForeignKeyField(
    "models.XuiServer",
    related_name="inbounds",
    # 注意：没有设置 on_delete，默认为 RESTRICT
)

# 多对多关系
accounts = fields.ManyToManyField(
    "models.ServerAccount",
    related_name="xui_inbounds",
    through="xui_inbound_account"
)
```

## 同步入站对 ServerInfo 的影响

当你同步入站时，会自动创建或更新 `ServerInfo` 表中的记录：

```
XuiInbound (入站配置)
  ↓ (同步时自动创建/更新)
ServerInfo (服务器信息)
```

**注意**：
- 删除 XUI 入站**不会**自动删除对应的 ServerInfo
- 删除 XUI 服务器**不会**自动删除对应的 ServerInfo
- 如果需要清理 ServerInfo，需要手动删除

## 账号状态更新

删除操作会自动更新相关账号的状态：

1. **从入站移除账号**：
   - 自动更新账号的 `is_all_inbound_added` 状态
   - 如果账号不再添加到所有入站，状态变为 `false`

2. **删除入站**：
   - 不会自动更新账号状态（因为删除前必须先移除所有账号）

3. **同步入站**：
   - 自动更新所有账号的 `is_all_inbound_added` 状态

## 建议的改进方案

### 方案 1: 添加级联删除（激进）

```python
# 修改 XuiInbound 模型
server = fields.ForeignKeyField(
    "models.XuiServer",
    related_name="inbounds",
    on_delete=fields.CASCADE  # 删除服务器时自动删除入站
)
```

**优点**：
- 删除服务器时自动清理所有入站
- 操作简单，一键删除

**缺点**：
- 可能误删重要数据
- 无法恢复
- 不符合当前的安全设计

### 方案 2: 添加批量删除功能（推荐）

在前端添加"批量删除"功能：

```typescript
// 删除服务器及其所有关联数据
async function deleteServerWithRelations(serverId: string) {
  // 1. 获取所有入站
  const inbounds = await getInboundList({ server_id: serverId })
  
  // 2. 对每个入站，移除所有账号
  for (const inbound of inbounds) {
    const accounts = await getInboundAccounts(inbound.id)
    for (const account of accounts) {
      await removeAccountFromInbound(inbound.id, account.id)
    }
  }
  
  // 3. 删除所有入站
  for (const inbound of inbounds) {
    await deleteInbound(inbound.id)
  }
  
  // 4. 删除服务器
  await deleteServer(serverId)
}
```

### 方案 3: 添加软删除（最安全）

添加 `deleted_at` 字段，标记删除而不是真正删除：

```python
class XuiServer(BaseModel):
    deleted_at = fields.DatetimeField(null=True, description='删除时间')
```

**优点**：
- 可以恢复误删的数据
- 保留历史记录
- 安全性高

**缺点**：
- 需要修改所有查询逻辑
- 数据库会保留已删除的数据

## 常见问题

### Q1: 删除 XUI 服务器时提示"还有入站配置"

**原因**：服务器下还有入站配置未删除

**解决**：
1. 进入"入站列表"
2. 筛选该服务器的入站
3. 逐个删除入站（删除前需要先移除账号）

### Q2: 删除入站时提示"还有账号"

**原因**：入站下还有账号未移除

**解决**：
1. 点击入站的"账号管理"
2. 移除所有账号
3. 再删除入站

### Q3: 删除服务器后，ServerInfo 还在

**原因**：同步入站时创建的 ServerInfo 不会自动删除

**解决**：
1. 进入"服务器管理" → "服务器信息"
2. 手动删除对应的 ServerInfo 记录

### Q4: 账号的"入站状态"不准确

**原因**：添加/删除服务器或入站后，账号状态没有更新

**解决**：
1. 点击"同步入站"按钮（会自动更新所有账号状态）
2. 或者刷新页面

## 相关文档

- [XUI 后台任务更新](./XUI_BACKGROUND_TASK_UPDATE.md)
- [Docker 代码更新指南](./DOCKER_CODE_UPDATE_GUIDE.md)
