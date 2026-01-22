# 前端项目钱包和账号更新

## 修改时间
2026-01-21

## 修改概述

根据后端的项目钱包和项目账号模型更新，修改前端代码以保持一致。

## 修改内容

### 1. TypeScript 类型定义 (frontend/src/types/index.ts)

#### ProjectWallet 接口更新

**修改前**:
```typescript
export interface ProjectWallet {
  id: string
  private_key: string
  public_key: string
  mnemonic: string  // 必填
  chain: string
  remark?: string
  project_id: string  // 必填
  project?: Project
  create_time: string
  update_time: string
}
```

**修改后**:
```typescript
export interface ProjectWallet {
  id: string
  private_key: string
  public_key: string
  mnemonic?: string  // ← 改为可选，私钥导入的钱包可能没有助记词
  chain: string
  remark?: string
  project_id?: string  // ← 改为可选，钱包可以独立存在
  project?: Project
  create_time: string
  update_time: string
}
```

#### ProjectAccount 接口
✅ 无需修改，`project_id` 已经是必填的（正确）

### 2. API 方法 (frontend/src/api/project.ts)

#### 添加钱包 Upsert 方法

```typescript
export const upsertProjectWallet = (data: Partial<ProjectWallet>) => {
  return api.post<any, ProjectWallet>('/v1/project/wallet/upsert', data)
}
```

### 3. 项目钱包页面 (frontend/src/views/Project/ProjectWallet.tsx)

#### 表单字段修改

**修改前**:
```tsx
<Form.Item
  label="项目"
  name="project_id"
  rules={[{ required: true, message: '请选择项目' }]}  // 必填
>
  <Select placeholder="请选择项目" ... />
</Form.Item>

<Form.Item
  label="助记词"
  name="mnemonic"
  rules={[{ required: true, message: '请输入助记词' }]}  // 必填
>
  <Input.TextArea placeholder="请输入助记词" rows={3} />
</Form.Item>
```

**修改后**:
```tsx
<Form.Item
  label="项目"
  name="project_id"
  tooltip="可选，不选择则创建独立钱包"  // ← 添加提示
>
  <Select 
    placeholder="请选择项目（可选）" 
    allowClear  // ← 允许清空
    ... 
  />
</Form.Item>

<Form.Item
  label="助记词"
  name="mnemonic"
  tooltip="可选，私钥导入的钱包可以不填"  // ← 添加提示
>
  <Input.TextArea placeholder="请输入助记词（可选）" rows={3} />
</Form.Item>
```

#### 其他优化
- 私钥输入框提示改为"请输入私钥（加密存储）"
- 链名称提示改为"请输入链名称（如：ETH、BSC、Polygon）"

### 4. 项目账号页面 (frontend/src/views/Project/ProjectAccount.tsx)

✅ 无需修改，`project_id` 保持必填（正确）

## 功能说明

### 项目钱包的三种使用场景

#### 场景1: 创建独立钱包（不关联项目）
```typescript
await createProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",
  chain: "ETH",
  remark: "独立钱包"
  // 不传 project_id 和 mnemonic
})
```

#### 场景2: 创建项目钱包（有助记词）
```typescript
await createProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",
  mnemonic: "word1 word2 ...",
  chain: "ETH",
  project_id: "project-uuid",
  remark: "项目主钱包"
})
```

#### 场景3: 私钥导入钱包（无助记词）
```typescript
await createProjectWallet({
  private_key: "encrypted_private_key",
  public_key: "0x...",
  chain: "ETH",
  project_id: "project-uuid",
  remark: "私钥导入的钱包"
  // 不传 mnemonic
})
```

#### 场景4: 使用 Upsert（根据公钥判断）
```typescript
// 如果公钥已存在则更新，否则创建
await upsertProjectWallet({
  public_key: "0x...",  // 根据公钥判断唯一性
  private_key: "encrypted_private_key",
  chain: "ETH",
  project_id: "project-uuid"
})
```

### 项目账号的使用

项目账号必须关联到项目：

```typescript
await createProjectAccount({
  account: "user@example.com",
  password: "encrypted_password",
  status: 1,
  account_type: 1,
  project_id: "project-uuid"  // 必填
})
```

## 用户界面变化

### 钱包表单

**之前**:
- 项目：必填（红色星号）
- 助记词：必填（红色星号）

**现在**:
- 项目：可选（无红色星号，有提示图标）
  - 提示：可选，不选择则创建独立钱包
- 助记词：可选（无红色星号，有提示图标）
  - 提示：可选，私钥导入的钱包可以不填

### 账号表单

✅ 保持不变，项目仍然是必填

## 数据验证

### 前端验证规则

**钱包表单**:
- ✅ 私钥：必填
- ✅ 公钥：必填
- ✅ 链：必填
- ⭕ 项目：可选
- ⭕ 助记词：可选
- ⭕ 备注：可选

**账号表单**:
- ✅ 账号：必填
- ✅ 账号类型：必填
- ✅ 状态：必填
- ✅ 项目：必填
- ⭕ 密码：可选

## 兼容性

### 向后兼容
- ✅ 现有的项目钱包数据仍然可以正常显示和编辑
- ✅ 现有的项目账号数据不受影响
- ✅ 支持新的独立钱包模式
- ✅ 支持无助记词的钱包

### 数据迁移
- 前端无需数据迁移
- 后端已有迁移文件处理数据库变更

## 测试建议

### 钱包功能测试

1. **创建独立钱包**
   - 不选择项目
   - 不填写助记词
   - 验证可以成功创建

2. **创建项目钱包**
   - 选择项目
   - 填写完整信息
   - 验证可以成功创建

3. **编辑钱包**
   - 修改项目关联（可以设置为空）
   - 修改助记词（可以设置为空）
   - 验证可以成功更新

4. **查询钱包**
   - 按项目过滤
   - 查看独立钱包（project 显示为 "-"）
   - 验证数据显示正确

5. **Upsert 功能**
   - 使用相同公钥多次调用
   - 验证不会创建重复记录

### 账号功能测试

1. **创建账号**
   - 必须选择项目
   - 验证表单验证正确

2. **编辑账号**
   - 修改项目关联
   - 验证可以成功更新

## 相关文件

### 前端文件
- ✅ `frontend/src/types/index.ts` - 类型定义
- ✅ `frontend/src/api/project.ts` - API 方法
- ✅ `frontend/src/views/Project/ProjectWallet.tsx` - 钱包页面
- ⭕ `frontend/src/views/Project/ProjectAccount.tsx` - 账号页面（无需修改）

### 后端文件（参考）
- `backend/app/models/project.py` - 模型定义
- `backend/app/schemas/project/wallet.py` - Schema 定义
- `backend/app/apis/v1/project/wallet.py` - API 端点

### 文档
- ✅ `docs/fixes/FRONTEND_WALLET_ACCOUNT_UPDATE.md` - 本文档
- `docs/fixes/PROJECT_WALLET_RELATION_FINAL.md` - 后端完整文档
- `docs/fixes/WALLET_MNEMONIC_NULLABLE.md` - 助记词可空文档

## 总结

✅ TypeScript 类型定义已更新
✅ API 方法已添加 upsert
✅ 钱包表单已修改为可选字段
✅ 账号表单保持不变（正确）
✅ 支持三种钱包类型：完整钱包、私钥导入钱包、独立钱包
✅ 向后兼容现有数据
✅ 用户界面更友好，有清晰的提示

前端现在完全匹配后端的数据模型，提供了更灵活的钱包管理功能！
