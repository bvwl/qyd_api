# QYD 项目文档索引

## 📚 文档目录

### 🚀 快速开始
- [QUICK_START_GUIDE.md](../QUICK_START_GUIDE.md) - 快速开始指南（推荐新手阅读）
- [README.md](../README.md) - 项目总览
- [backend/README.md](../backend/README.md) - 后端文档
- [frontend/README.md](../frontend/README.md) - 前端文档

---

## 🔐 加密功能文档 (`encryption/`)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [PROJECT_ACCOUNT_ENCRYPTION_UPDATE.md](../PROJECT_ACCOUNT_ENCRYPTION_UPDATE.md) | **项目账号加密更新（2026-01-25）** | ⭐⭐⭐⭐ |
| [PROJECT_ACCOUNT_ENCRYPTION_SUMMARY.md](../PROJECT_ACCOUNT_ENCRYPTION_SUMMARY.md) | 加密更新快速总结 | ⭐⭐⭐⭐ |
| [PROJECT_ACCOUNT_ENCRYPTION.md](encryption/PROJECT_ACCOUNT_ENCRYPTION.md) | 项目账号加密详细文档 | ⭐⭐⭐ |
| [PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md](encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md) | 加密功能快速参考 | ⭐⭐⭐ |
| [PROJECT_ACCOUNT_ENCRYPTION_FLOW.md](encryption/PROJECT_ACCOUNT_ENCRYPTION_FLOW.md) | 加密流程图（含详细说明） | ⭐⭐ |
| [SOCKS5_ACCOUNT_AES_ENCRYPTION.md](encryption/SOCKS5_ACCOUNT_AES_ENCRYPTION.md) | SOCKS5账号加密实现 | ⭐ |
| [SOCKS5_ACCOUNT_IMPLEMENTATION_SUMMARY.md](encryption/SOCKS5_ACCOUNT_IMPLEMENTATION_SUMMARY.md) | SOCKS5账号实现总结 | ⭐ |

**最新更新（2026-01-25）**：
- ✅ 加密密钥从"项目名称+9527"改为"项目账号+9527"
- ✅ 新增 password 字段加密支持
- ✅ 不需要查询关联的项目信息
- ✅ 每个账号使用独立密钥

**核心特性**：
- AES-CBC 加密
- 每个账号独立密钥
- 基于权限的自动解密
- Redis 队列数据加密
- 递归加密所有层级

---

## 📝 日志管理文档 (`logs/`)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [LOG_SYSTEM_COMPLETE.md](logs/LOG_SYSTEM_COMPLETE.md) | 日志系统完整文档 | ⭐⭐⭐ |
| [LOG_QUICK_REFERENCE.md](logs/LOG_QUICK_REFERENCE.md) | 日志快速参考 | ⭐⭐⭐ |
| [LOG_MANAGEMENT_UPDATE.md](logs/LOG_MANAGEMENT_UPDATE.md) | 日志管理更新说明 | ⭐⭐ |
| [LOG_MANAGEMENT_SUMMARY.md](logs/LOG_MANAGEMENT_SUMMARY.md) | 日志功能总结 | ⭐⭐ |
| [LOG_SYSTEM_FINAL_SUMMARY.md](logs/LOG_SYSTEM_FINAL_SUMMARY.md) | 日志系统最终总结 | ⭐ |
| [LOG_SYSTEM_VERIFICATION.md](logs/LOG_SYSTEM_VERIFICATION.md) | 日志系统验证 | ⭐ |
| [LOG_README.md](logs/LOG_README.md) | 日志系统说明 | ⭐ |

**核心特性**：
- 90天保留期
- 四层目录结构（名称/年/月/日）
- 自动压缩为 .gz
- 自动删除过期日志
- 按模块分类

---

## 📊 导出功能文档 (`export/`)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [EXPORT_FEATURE_COMPLETE.md](export/EXPORT_FEATURE_COMPLETE.md) | 导出功能完整文档 | ⭐⭐⭐ |
| [QUICK_REFERENCE_EXPORT.md](export/QUICK_REFERENCE_EXPORT.md) | 导出功能快速参考 | ⭐⭐ |
| [EXPORT_STATUS_COLUMN_AND_FIX.md](export/EXPORT_STATUS_COLUMN_AND_FIX.md) | 导出状态列和修复 | ⭐⭐ |
| [EXPORT_USER_COLUMN_UPDATE.md](export/EXPORT_USER_COLUMN_UPDATE.md) | 导出用户列更新 | ⭐ |
| [FINAL_EXPORT_SUMMARY.md](export/FINAL_EXPORT_SUMMARY.md) | 导出功能最终总结 | ⭐ |
| [INSTALL_OPENPYXL.md](export/INSTALL_OPENPYXL.md) | 安装 openpyxl 库 | ⭐ |

**核心特性**：
- Excel 导出
- 项目统计导出
- 状态列显示
- 用户信息显示

---

## 🖥️ 服务器管理文档 (`server/`)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [SERVER_ACCOUNT_FINAL_SUMMARY.md](server/SERVER_ACCOUNT_FINAL_SUMMARY.md) | 服务器账号最终总结 | ⭐⭐⭐ |
| [SERVER_ACCOUNT_FIX_SUMMARY.md](server/SERVER_ACCOUNT_FIX_SUMMARY.md) | 服务器账号修复总结 | ⭐⭐ |
| [SERVER_ACCOUNT_PASSWORD_VISIBILITY_TOGGLE.md](server/SERVER_ACCOUNT_PASSWORD_VISIBILITY_TOGGLE.md) | 密码显示切换功能 | ⭐⭐ |
| [SERVER_ACCOUNT_ONE_PER_USER.md](server/SERVER_ACCOUNT_ONE_PER_USER.md) | 每用户一个账号限制 | ⭐ |
| [SERVER_ACCOUNT_ADMIN_PERMISSION_UPDATE.md](server/SERVER_ACCOUNT_ADMIN_PERMISSION_UPDATE.md) | 管理员权限更新 | ⭐ |
| [SERVER_ACCOUNT_PASSWORD_DISPLAY_FIX.md](server/SERVER_ACCOUNT_PASSWORD_DISPLAY_FIX.md) | 密码显示修复 | ⭐ |
| [SERVER_ACCOUNT_PASSWORD_FIELD_UPDATE.md](server/SERVER_ACCOUNT_PASSWORD_FIELD_UPDATE.md) | 密码字段更新 | ⭐ |
| [SERVER_ACCOUNT_FINAL_FIX.md](server/SERVER_ACCOUNT_FINAL_FIX.md) | 服务器账号最终修复 | ⭐ |
| [SERVER_ACCOUNT_STATUS.md](server/SERVER_ACCOUNT_STATUS.md) | 服务器账号状态 | ⭐ |
| [SERVER_ACCOUNT_QUICK_TEST.md](server/SERVER_ACCOUNT_QUICK_TEST.md) | 快速测试 | ⭐ |
| [SERVER_IS_SALE_FIELD_FIX.md](server/SERVER_IS_SALE_FIELD_FIX.md) | is_sale 字段修复 | ⭐ |
| [SERVER_LIST_UI_UPDATE.md](server/SERVER_LIST_UI_UPDATE.md) | 服务器列表UI更新 | ⭐ |

---

## 📧 邮件功能文档 (`mail/`)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [MAIL_VIEWER_FINAL_UPDATE.md](mail/MAIL_VIEWER_FINAL_UPDATE.md) | 邮件查看器最终更新 | ⭐⭐⭐ |
| [MAIL_SEND_MENU_FIX.md](mail/MAIL_SEND_MENU_FIX.md) | 发送邮件菜单修复 | ⭐⭐ |
| [MAIL_VIEWER_RENAME.md](mail/MAIL_VIEWER_RENAME.md) | 邮件查看器重命名 | ⭐⭐ |
| [MAIL_SEND_FEATURE.md](mail/MAIL_SEND_FEATURE.md) | 发送邮件功能 | ⭐⭐ |
| [MAIL_VIEWER_FIX.md](mail/MAIL_VIEWER_FIX.md) | 邮件查看器修复 | ⭐ |
| [MAIL_VIEWER_TROUBLESHOOTING.md](mail/MAIL_VIEWER_TROUBLESHOOTING.md) | 邮件查看器故障排查 | ⭐ |

---

## ⚡ 性能优化文档 (`performance/`)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [PERFORMANCE_QUICK_REFERENCE.md](performance/PERFORMANCE_QUICK_REFERENCE.md) | 性能配置快速参考 | ⭐⭐⭐ |
| [QUEUE_SEPARATION_QUICK_START.md](performance/QUEUE_SEPARATION_QUICK_START.md) | 队列分离快速开始 | ⭐⭐⭐ |
| [SCALE_TO_10K_GUIDE.md](performance/SCALE_TO_10K_GUIDE.md) | 扩展到10000+条/秒指南 | ⭐⭐⭐ |
| [REDIS_QUEUE_SEPARATION_GUIDE.md](performance/REDIS_QUEUE_SEPARATION_GUIDE.md) | Redis队列分离完整指南 | ⭐⭐ |
| [ULTRA_HIGH_PERFORMANCE_GUIDE.md](performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md) | 超高性能指南 | ⭐⭐ |
| [QUICK_PERFORMANCE_GUIDE.md](performance/QUICK_PERFORMANCE_GUIDE.md) | 快速性能指南 | ⭐⭐ |
| [REDIS_QUEUE_PERFORMANCE_ANALYSIS.md](performance/REDIS_QUEUE_PERFORMANCE_ANALYSIS.md) | Redis队列性能分析 | ⭐ |
| [REDIS_QUEUE_SEPARATION_COMPLETE.md](performance/REDIS_QUEUE_SEPARATION_COMPLETE.md) | Redis队列分离完成 | ⭐ |
| [SCALE_TO_10K_COMPLETE.md](performance/SCALE_TO_10K_COMPLETE.md) | 扩展到10K完成 | ⭐ |
| [UVICORN_WORKERS_VS_REDIS_WORKERS.md](performance/UVICORN_WORKERS_VS_REDIS_WORKERS.md) | Uvicorn Workers问题详解 | ⭐ |

**性能对比**：
- 标准配置：2700条/秒
- 高性能配置：6000条/秒
- 超高性能配置：12000条/秒
- 极限性能配置：20000条/秒

---

## 📖 使用指南 (`guides/`)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [REDIS_QUEUE_GUIDE.md](guides/REDIS_QUEUE_GUIDE.md) | Redis队列使用指南 | ⭐⭐⭐ |
| [PERMISSION_QUICK_START.md](guides/PERMISSION_QUICK_START.md) | 权限快速开始 | ⭐⭐⭐ |
| [RBAC_README.md](guides/RBAC_README.md) | RBAC使用指南 | ⭐⭐⭐ |
| [MAIL_VIEWER_QUICK_START.md](guides/MAIL_VIEWER_QUICK_START.md) | 邮件查看器快速开始 | ⭐⭐ |
| [REDIS_CACHE_LOGIC.md](guides/REDIS_CACHE_LOGIC.md) | Redis缓存逻辑说明 | ⭐⭐ |
| [REDIS_PIPELINE_SEPARATION.md](guides/REDIS_PIPELINE_SEPARATION.md) | Redis管道分离 | ⭐⭐ |
| [MENU_BINDING_GUIDE.md](guides/MENU_BINDING_GUIDE.md) | 菜单绑定指南 | ⭐⭐ |
| [QUICK_REFERENCE.md](guides/QUICK_REFERENCE.md) | 快速参考 | ⭐⭐ |
| [PERMISSION_MANAGE_README.md](guides/PERMISSION_MANAGE_README.md) | 权限管理说明 | ⭐ |
| [PERMISSION_DEBUG.md](guides/PERMISSION_DEBUG.md) | 权限调试 | ⭐ |
| [MAIL_VIEWER_TROUBLESHOOTING.md](guides/MAIL_VIEWER_TROUBLESHOOTING.md) | 邮件查看器故障排查 | ⭐ |
| [REDIS_QUEUE_CONFIG_UPDATE.md](guides/REDIS_QUEUE_CONFIG_UPDATE.md) | Redis队列配置更新 | ⭐ |

---

## 🎯 功能文档 (`features/`)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [PROJECT_ACCOUNT_FEATURES_SUMMARY.md](features/PROJECT_ACCOUNT_FEATURES_SUMMARY.md) | 项目账号功能总结 | ⭐⭐⭐ |
| [PROJECT_ORGANIZATION_SUMMARY.md](features/PROJECT_ORGANIZATION_SUMMARY.md) | 项目整理总结 | ⭐⭐⭐ |
| [MAIL_VIEWER_FEATURE.md](features/MAIL_VIEWER_FEATURE.md) | 邮件查看器功能 | ⭐⭐ |
| [PROJECT_USER_MANAGEMENT.md](features/PROJECT_USER_MANAGEMENT.md) | 项目用户管理 | ⭐⭐ |
| [WALLET_FEATURE_UPDATE.md](features/WALLET_FEATURE_UPDATE.md) | 钱包功能更新 | ⭐⭐ |
| [COPY_ID_FEATURE.md](features/COPY_ID_FEATURE.md) | 复制ID功能 | ⭐ |
| [PROJECT_ACCOUNT_STATS_FEATURE.md](features/PROJECT_ACCOUNT_STATS_FEATURE.md) | 项目账号统计功能 | ⭐ |
| [PROJECT_STATS_EXPORT_FEATURE.md](features/PROJECT_STATS_EXPORT_FEATURE.md) | 项目统计导出功能 | ⭐ |
| [PROJECT_STRUCTURE.md](features/PROJECT_STRUCTURE.md) | 项目结构说明 | ⭐ |
| [BALANCE_AUTO_CALCULATION_FIX.md](features/BALANCE_AUTO_CALCULATION_FIX.md) | 余额自动计算修复 | ⭐ |
| [AUTO_START_QUEUE_WORKER.md](features/AUTO_START_QUEUE_WORKER.md) | 自动启动队列处理器 | ⭐ |
| [REDIS_QUEUE_MANUAL_START.md](features/REDIS_QUEUE_MANUAL_START.md) | Redis队列手动启动 | ⭐ |
| [UPSERT_REDIS_QUEUE_UPDATE.md](features/UPSERT_REDIS_QUEUE_UPDATE.md) | Upsert Redis队列更新 | ⭐ |
| [REMOVE_RAW_PASSWORD_FIELD.md](features/REMOVE_RAW_PASSWORD_FIELD.md) | 移除原始密码字段 | ⭐ |
| [EMAIL_SERVER_RELATION_FIX.md](features/EMAIL_SERVER_RELATION_FIX.md) | 邮件服务器关系修复 | ⭐ |
| [ANTD_MESSAGE_WARNING_FIX.md](features/ANTD_MESSAGE_WARNING_FIX.md) | Ant Design消息警告修复 | ⭐ |

---

## 🏗️ RBAC设计文档 (`rbac/`)

| 文档 | 说明 | 优先级 |
|------|------|--------|
| [QUICK_START.md](rbac/QUICK_START.md) | RBAC快速开始 | ⭐⭐⭐ |
| [PRACTICAL_RBAC_DESIGN.md](rbac/PRACTICAL_RBAC_DESIGN.md) | 实用RBAC设计 | ⭐⭐ |
| [MODERN_RBAC_DESIGN.md](rbac/MODERN_RBAC_DESIGN.md) | 现代RBAC设计 | ⭐⭐ |
| [ENTERPRISE_RBAC_DESIGN.md](rbac/ENTERPRISE_RBAC_DESIGN.md) | 企业级RBAC设计 | ⭐⭐ |
| [COMPARISON.md](rbac/COMPARISON.md) | RBAC设计对比 | ⭐ |
| [V1_VS_V2_COMPARISON.md](rbac/V1_VS_V2_COMPARISON.md) | V1 vs V2对比 | ⭐ |
| [IMPLEMENTATION_GUIDE.md](rbac/IMPLEMENTATION_GUIDE.md) | 实现指南 | ⭐ |

---

## 🔧 修复记录 (`fixes/`)

包含详细的修复和更新记录，按功能分类：

### JWT认证相关
- JWT_AUTH_FIX.md
- JWT_AUTH_ONLY.md
- JWT_INTEGRATION.md
- JWT_TOKEN_QUICK_START.md
- JWT_UPDATE_SUMMARY.md
- JWT_VERIFICATION_REFACTOR.md

### RBAC权限相关
- RBAC_IMPLEMENTATION_COMPLETE.md
- RBAC_V2_COMPLETE.md
- RBAC_V2_IMPLEMENTATION.md
- RBAC_V2_QUICK_START.md
- PERMISSION_COMPLETE.md
- PERMISSION_FIX_FINAL_SUMMARY.md

### 数据库相关
- DATABASE_CORRECTION.md
- REDIS_CACHE_DB_SEPARATION.md
- REDIS_CACHE_UPDATE_LOGIC_FIX.md

### 前端相关
- FRONTEND_COMPLETION_SUMMARY.md
- FRONTEND_ERROR_HANDLING_FIX.md
- FRONTEND_JWT_SUMMARY.md
- FRONTEND_PERMISSION_FIX.md

### 其他修复
- 查看 `fixes/` 目录获取完整列表

---

## 📊 功能总结 (`summaries/`)

| 文档 | 说明 |
|------|------|
| [RBAC_COMPLETE.md](summaries/RBAC_COMPLETE.md) | RBAC完成总结 |
| [RBAC_FINAL_SUMMARY.md](summaries/RBAC_FINAL_SUMMARY.md) | RBAC最终总结 |
| [REDIS_QUEUE_FINAL_SUMMARY.md](summaries/REDIS_QUEUE_FINAL_SUMMARY.md) | Redis队列最终总结 |
| [SYSTEM_STATUS_SUMMARY.md](summaries/SYSTEM_STATUS_SUMMARY.md) | 系统状态总结 |
| [CLEANUP_COMPLETE.md](summaries/CLEANUP_COMPLETE.md) | 清理完成 |

---

## 🗂️ API文档 (`api/`)

| 文档 | 说明 |
|------|------|
| [API_AUTH_COMPLETE.md](api/API_AUTH_COMPLETE.md) | API认证完成 |
| [API_AUTH_IMPLEMENTATION.md](api/API_AUTH_IMPLEMENTATION.md) | API认证实现 |
| [API_404_SILENT_HANDLING.md](api/API_404_SILENT_HANDLING.md) | API 404静默处理 |

---

## 📌 优先级说明

- ⭐⭐⭐ **高优先级**：新手必读，核心功能文档
- ⭐⭐ **中优先级**：重要功能和配置文档
- ⭐ **低优先级**：详细实现和历史记录

---

## 🔍 快速查找

### 我想了解...

#### 如何快速开始？
→ [QUICK_START_GUIDE.md](../QUICK_START_GUIDE.md)

#### 如何配置加密功能？
→ [PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md](encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md)

#### 如何优化性能？
→ [PERFORMANCE_QUICK_REFERENCE.md](performance/PERFORMANCE_QUICK_REFERENCE.md)

#### 如何管理日志？
→ [LOG_QUICK_REFERENCE.md](logs/LOG_QUICK_REFERENCE.md)

#### 如何使用Redis队列？
→ [REDIS_QUEUE_GUIDE.md](guides/REDIS_QUEUE_GUIDE.md)

#### 如何配置权限？
→ [PERMISSION_QUICK_START.md](guides/PERMISSION_QUICK_START.md)

#### 如何导出数据？
→ [QUICK_REFERENCE_EXPORT.md](export/QUICK_REFERENCE_EXPORT.md)

---

## 📝 文档更新日志

### 2026-01-25
- ✅ 新增加密功能文档
- ✅ 新增日志管理文档
- ✅ 更新快速开始指南
- ✅ 整理文档目录结构

### 2026-01-23
- ✅ 初始文档创建
- ✅ 性能优化文档
- ✅ RBAC设计文档
- ✅ API文档

---

**最后更新**: 2026-01-25  
**文档版本**: v1.1.0
