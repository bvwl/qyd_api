# 钱包-项目关系重构完成

## 概述
成功重构了项目钱包和项目账号的关系模型，将钱包从项目账号关联改为直接关联项目。

## 变更内容

### 1. 数据库模型变更 (backend/app/models/project.py)

**ProjectWallet (项目钱包)**
- ✅ 添加 `project` 外键字段，直接关联 `ProjectInfo`
- ✅ 添加索引：`(project_id, chain, create_time)`

**ProjectAccount (项目账号)**
- ✅ 移除 `wallet` 外键字段
- ✅ 移除 `wallet_id` 相关索引

### 2. Schema 变更

**backend/app/schemas/project/wallet.py**
- ✅ 添加 `project_id: UUID` 字段
- ✅ 添加 `project: ProjectInfoBase` 关联信息
- ✅ 使用 `ProjectInfoBase` 而非 dict 类型

**backend/app/schemas/project/account.py**
- ✅ 移除 `wallet_id` 字段
- ✅ 移除 `wallet` 关联信息

### 3. CRUD 变更

**backend/app/crud/project/wallet.py**
- ✅ 添加 `project_id` 查询参数
- ✅ 添加 `project` 预加载
- ✅ 更新过滤逻辑

**backend/app/crud/project/account.py**
- ✅ 移除 `wallet_id` 参数
- ✅ 移除 `wallet` 预加载

### 4. API 变更

**backend/app/apis/v1/project/wallet.py**
- ✅ 添加 `project_id` 查询参数支持

### 5. 数据库迁移

**backend/migrations/models/1_20260121155309_wallet_project_relation.py**
- ✅ 生成迁移文件
- ✅ 修复外键约束顺序问题
- ✅ 成功执行迁移

迁移内容：
```sql
-- 移除项目账号的钱包关联
ALTER TABLE `project_account` DROP FOREIGN KEY `fk_project__project__93399a32`;
ALTER TABLE `project_account` DROP INDEX `idx_project_acc_wallet__29c3f9`;
ALTER TABLE `project_account` DROP COLUMN `wallet_id`;

-- 添加钱包的项目关联
ALTER TABLE `project_wallet` ADD `project_id` CHAR(36) NOT NULL COMMENT '所属项目';
ALTER TABLE `project_wallet` ADD CONSTRAINT `fk_project__project__cba39da5` 
    FOREIGN KEY (`project_id`) REFERENCES `project_info` (`id`) ON DELETE CASCADE;
ALTER TABLE `project_wallet` ADD INDEX `idx_project_wal_project_7a4c7e` 
    (`project_id`, `chain`, `create_time`);
```

### 6. 前端类型定义变更 (frontend/src/types/index.ts)

**ProjectWallet**
- ✅ 添加 `project_id: string` 字段
- ✅ 添加 `project?: Project` 关联信息

**ProjectAccount**
- ✅ 移除 `wallet_id?: string` 字段
- ✅ 移除 `wallet?: ProjectWallet` 关联信息

### 7. 前端 API 变更 (frontend/src/api/project.ts)

**getProjectWalletList**
- ✅ 添加 `project_id?: string` 查询参数

### 8. 前端页面变更

**frontend/src/views/Project/ProjectWallet.tsx**
- ✅ 添加项目列表获取
- ✅ 添加项目选择器（搜索栏）
- ✅ 添加项目选择器（表单）
- ✅ 表格显示项目名称列
- ✅ 支持按项目筛选钱包

**frontend/src/views/Project/ProjectAccount.tsx**
- ✅ 确认已移除钱包选择器（之前已完成）

## 新的数据关系

### 之前的关系
```
ProjectInfo (项目信息)
    ↓
ProjectAccount (项目账号)
    ↓
ProjectWallet (项目钱包) [独立]
```

### 现在的关系
```
ProjectInfo (项目信息)
    ↓                    ↓
ProjectAccount      ProjectWallet
(项目账号)          (项目钱包)
```

## 功能特性

### 钱包管理页面
1. **搜索功能**
   - 按链名称搜索
   - 按项目筛选
   - 按创建时间范围筛选
   - 按更新时间范围筛选

2. **表格显示**
   - 公钥（可显示/隐藏）
   - 链名称
   - 所属项目
   - 备注
   - 创建时间

3. **表单功能**
   - 项目选择（必填，支持搜索）
   - 私钥输入
   - 公钥输入
   - 助记词输入
   - 链名称输入
   - 备注输入

### 账号管理页面
- 已移除钱包选择器
- 保留项目选择器

## 测试验证

### 后端验证
- ✅ 数据库连接正常
- ✅ 迁移执行成功
- ✅ 服务启动正常
- ✅ API 端点可用（需要认证）

### 前端验证
- ✅ TypeScript 编译无错误
- ✅ 类型定义正确
- ✅ API 参数类型完整
- ⏳ 功能测试（需要登录后在浏览器中测试）

## 注意事项

1. **数据迁移**
   - 现有钱包数据需要手动关联到项目
   - 如果有现有数据，需要执行数据迁移脚本
   - 新创建的钱包必须选择项目

2. **权限控制**
   - 只有 ADMIN 和 GM 角色可以创建/编辑/删除钱包
   - 普通用户只能查看

3. **级联删除**
   - 删除项目时会自动删除关联的钱包
   - 请谨慎操作

4. **前端测试**
   - 需要登录系统后测试钱包管理功能
   - 确认项目选择器工作正常
   - 确认钱包列表显示项目信息

## 相关文件

### 后端
- `backend/app/models/project.py`
- `backend/app/schemas/project/wallet.py`
- `backend/app/schemas/project/account.py`
- `backend/app/crud/project/wallet.py`
- `backend/app/crud/project/account.py`
- `backend/app/apis/v1/project/wallet.py`
- `backend/migrations/models/1_20260121155309_wallet_project_relation.py`

### 前端
- `frontend/src/types/index.ts`
- `frontend/src/api/project.ts`
- `frontend/src/views/Project/ProjectWallet.tsx`
- `frontend/src/views/Project/ProjectAccount.tsx`

## 完成时间
2026-01-21 15:59

## 状态
✅ 完成
