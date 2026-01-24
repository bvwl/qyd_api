# 项目整理总结 - 2026年1月25日

## 本次会话完成的工作

### 1. ✅ 日志管理系统优化

**需求**：
- 日志保留期限从30天改为90天（3个月）
- 日志存储结构改为：`名称/年/月/日`（四层目录）
- 自动压缩旧日志为 .gz 格式
- 自动删除超过90天的旧日志

**实现**：
- 修改了 `backend/app/utils/logs.py`：
  - 日志保留期限：30天 → 90天
  - 目录结构：`名称/年-月` → `名称/年/月/日`
  - 自动压缩、自动删除、自动清理空目录
- 创建了整理脚本 `backend/scripts/organize_logs.py`
- 创建了验证脚本 `backend/test_log_structure.py`
- 成功迁移旧的三层结构到新的四层结构

**文档**：
- `LOG_MANAGEMENT_UPDATE.md` - 更新说明
- `LOG_QUICK_REFERENCE.md` - 快速参考
- `LOG_MANAGEMENT_SUMMARY.md` - 功能总结
- `LOG_SYSTEM_COMPLETE.md` - 完整文档

---

### 2. ✅ 修复"发送邮件"菜单无法显示

**问题**：
- 二级菜单"发送邮件"无法正常显示

**原因**：
- 前端路由配置缺少 `mail/send` 路由
- 默认菜单配置缺少"发送邮件"菜单项

**解决**：
- 修改了 `frontend/src/router/index.tsx`：添加 MailSend 路由
- 修改了 `frontend/src/components/Layout/index.tsx`：添加"发送邮件"菜单项

**文档**：
- `MAIL_SEND_MENU_FIX.md`

---

### 3. ✅ 重命名"邮件查看器"为"邮件查看"

**需求**：
- 将二级路由"邮件查看器"改为"邮件查看"

**实现**：
- 修改了前端默认菜单配置
- 修改了后端路由初始化脚本

**文档**：
- `MAIL_VIEWER_RENAME.md`

---

### 4. ✅ 项目账号敏感数据加密功能

**需求**：
- 项目账号的 `data` 字段中的 `private_key` 和 `mnemonic` 需要加密
- 使用 AES 加密，密钥基于项目名称
- 只有项目所属人和 ADMIN 可以解密
- Redis 队列也需要支持加密

**实现**：

#### 加密规则
- **加密字段**：`private_key`、`mnemonic`
- **加密方式**：AES-CBC
- **密钥（key）**：MD5(项目名称 + "9527")
- **初始向量（IV）**：MD5("9527" + 项目名称) 取前16位
- **递归加密**：支持所有层级的嵌套对象和数组

#### 权限控制
| 用户类型 | 查看权限 | 解密权限 |
|---------|---------|---------|
| ADMIN | ✅ 所有项目 | ✅ 所有项目 |
| 项目所属人 | ✅ 自己的项目 | ✅ 自己的项目 |
| GM | ✅ 所有项目 | ❌ 非自己的项目 |
| IT/MANUAL | ✅ 分配的项目 | ❌ 非自己的项目 |

#### 核心文件
1. **backend/app/core/tools.py**
   - 添加了 `aes_encrypt_project()` 和 `aes_decrypt_project()` 函数

2. **backend/app/utils/project_crypto.py**（新建）
   - `encrypt_sensitive_fields()` - 递归加密
   - `decrypt_sensitive_fields()` - 递归解密
   - `check_user_can_decrypt()` - 权限检查

3. **backend/app/crud/project/account.py**（修改）
   - `create()` - 创建时自动加密
   - `get()` - 查询时根据权限解密
   - `get_multi()` - 批量查询时根据权限解密
   - `update()` - 更新时自动加密
   - `upsert()` - 创建或更新时自动加密

4. **backend/app/apis/v1/project/account.py**（修改）
   - 传递用户ID和角色到 CRUD 层
   - 支持权限控制

5. **backend/app/utils/project_account_queue.py**（修改）
   - 重写 `add_to_queue()` 方法
   - 数据入队前自动加密敏感字段

#### 测试验证
```bash
# 加密功能测试
cd backend
python test_project_account_encryption.py

# Redis 队列加密测试
cd backend
python test_queue_encryption.py
```

**测试结果**：
- ✅ 递归加密所有层级的敏感字段
- ✅ 正确解密所有加密字段
- ✅ 权限检查（ADMIN、项目所属人、其他用户）
- ✅ 不同项目使用不同密钥
- ✅ Redis 队列数据自动加密

#### 数据流程

**创建流程**：
```
前端提交明文数据
    ↓
API 层接收
    ↓
添加到 Redis 队列（自动加密）
    ↓
Redis 存储加密数据
    ↓
队列处理器读取加密数据
    ↓
写入数据库（加密状态）
```

**查询流程**：
```
前端请求数据
    ↓
API 层接收（带用户信息）
    ↓
CRUD 层查询数据库
    ↓
检查用户权限
    ↓
有权限：解密敏感字段
无权限：保持加密状态
    ↓
返回给前端
```

**文档**：
- `PROJECT_ACCOUNT_ENCRYPTION.md` - 详细文档
- `PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md` - 快速参考
- `PROJECT_ACCOUNT_FEATURES_SUMMARY.md` - 功能总结
- `PROJECT_ORGANIZATION_SUMMARY.md` - 本文档

---

## 安全特性总结

### 1. 数据安全
- ✅ 敏感数据加密存储
- ✅ 每个项目独立密钥
- ✅ 密钥基于项目名称生成，无需额外存储
- ✅ 支持嵌套对象和数组的递归加密
- ✅ Redis 队列数据也加密存储

### 2. 权限隔离
- ✅ 基于角色的访问控制（RBAC）
- ✅ 项目级别的数据权限
- ✅ 只有授权用户可以解密
- ✅ 其他用户只能看到密文

### 3. 自动化
- ✅ 创建/更新时自动加密
- ✅ 查询时根据权限自动解密
- ✅ Redis 队列自动加密
- ✅ 开发者无需手动处理

---

## 重要注意事项

### ⚠️ 项目名称不能修改
- 加密密钥基于项目名称生成
- 修改项目名称会导致旧数据无法解密
- 如需修改，需要先解密所有数据，再用新名称重新加密

### ⚠️ 数据迁移
- 现有数据不会自动加密
- 需要手动迁移或在下次更新时自动加密

### ⚠️ 备份恢复
- 备份数据包含加密数据
- 恢复时需要确保项目名称一致

---

## 快速开始

### 1. 测试加密功能
```bash
cd backend
python test_project_account_encryption.py
```

### 2. 测试队列加密
```bash
cd backend
python test_queue_encryption.py
```

### 3. 启动队列处理器
```bash
cd backend
python start_queue_worker.py
```

### 4. 查看日志结构
```bash
cd backend
python test_log_structure.py
```

### 5. 整理旧日志
```bash
cd backend
python scripts/organize_logs.py
```

---

## API 使用示例

### 创建项目账号（自动加密）
```bash
curl -X POST http://localhost:6080/v1/project/account \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "account": "test@example.com",
    "project_id": "uuid",
    "data": {
      "private_key": "0xabcdef...",
      "mnemonic": "word1 word2 ..."
    }
  }'
```

### 查询项目账号（根据权限自动解密）
```bash
curl -X GET http://localhost:6080/v1/project/account/{id} \
  -H "Authorization: Bearer {token}"
```

### 批量创建/更新（Redis 队列）
```bash
curl -X POST http://localhost:6080/v1/project/account/batch-upsert \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "account": "test1@example.com",
      "project_id": "uuid",
      "data": { ... }
    },
    {
      "account": "test2@example.com",
      "project_id": "uuid",
      "data": { ... }
    }
  ]'
```

---

## 文件清单

### 新增文件
```
backend/
├── app/
│   └── utils/
│       └── project_crypto.py              # 加密工具函数
├── scripts/
│   └── organize_logs.py                   # 日志整理脚本
├── test_project_account_encryption.py     # 加密功能测试
├── test_queue_encryption.py               # 队列加密测试
└── test_log_structure.py                  # 日志结构验证

docs/
├── LOG_MANAGEMENT_UPDATE.md               # 日志管理更新
├── LOG_QUICK_REFERENCE.md                 # 日志快速参考
├── LOG_MANAGEMENT_SUMMARY.md              # 日志功能总结
├── LOG_SYSTEM_COMPLETE.md                 # 日志完整文档
├── MAIL_SEND_MENU_FIX.md                  # 发送邮件菜单修复
├── MAIL_VIEWER_RENAME.md                  # 邮件查看器重命名
├── PROJECT_ACCOUNT_ENCRYPTION.md          # 项目账号加密详细文档
├── PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md # 项目账号加密快速参考
├── PROJECT_ACCOUNT_FEATURES_SUMMARY.md    # 项目账号功能总结
└── PROJECT_ORGANIZATION_SUMMARY.md        # 本文档
```

### 修改文件
```
backend/
├── app/
│   ├── core/
│   │   └── tools.py                       # 添加 AES 加密函数
│   ├── utils/
│   │   ├── logs.py                        # 日志管理优化
│   │   └── project_account_queue.py       # Redis 队列加密支持
│   ├── crud/
│   │   └── project/
│   │       └── account.py                 # CRUD 层加密逻辑
│   └── apis/
│       └── v1/
│           └── project/
│               └── account.py             # API 层权限传递
└── db/
    └── init_routes.py                     # 路由初始化

frontend/
└── src/
    ├── router/
    │   └── index.tsx                      # 添加 MailSend 路由
    └── components/
        └── Layout/
            └── index.tsx                  # 添加菜单项
```

---

## 技术栈

### 后端
- **框架**：FastAPI（异步）
- **ORM**：Tortoise ORM
- **数据库**：MySQL 8.0
- **缓存/队列**：Redis 7.0
- **加密**：AES-CBC（Crypto.Cipher）
- **日志**：自定义日志系统（自动轮转、压缩）

### 前端
- **框架**：React 18
- **语言**：TypeScript 5
- **UI 库**：Ant Design 5
- **路由**：React Router v6
- **状态管理**：Zustand

---

## 总结

本次会话完成了以下核心功能：

1. ✅ **日志管理系统优化**
   - 保留期限：30天 → 90天
   - 目录结构：三层 → 四层
   - 自动压缩、删除、清理

2. ✅ **菜单修复和优化**
   - 修复"发送邮件"菜单显示问题
   - 重命名"邮件查看器"为"邮件查看"

3. ✅ **项目账号敏感数据加密**
   - AES-CBC 加密
   - 每个项目独立密钥
   - 基于权限的自动解密
   - Redis 队列加密支持
   - 递归加密所有层级
   - 完整测试覆盖

所有功能已完成开发、测试并通过验证，可以投入使用！🎉

---

**完成时间**：2026-01-25
**版本**：v1.0
**状态**：✅ 全部完成并测试通过
