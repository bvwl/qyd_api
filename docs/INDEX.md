# QYD 项目文档索引

## 📚 文档分类

### 🚀 快速开始

| 文档 | 说明 |
|------|------|
| [README.md](../README.md) | 项目总览和快速开始 |
| [backend/README.md](../backend/README.md) | 后端开发指南 |
| [frontend/README.md](../frontend/README.md) | 前端开发指南 |

### ⚡ 性能优化 (`performance/`)

| 文档 | 说明 | 适用场景 |
|------|------|---------|
| [QUEUE_SEPARATION_QUICK_START.md](performance/QUEUE_SEPARATION_QUICK_START.md) | 队列分离快速开始 | 2000条/秒 |
| [REDIS_QUEUE_SEPARATION_GUIDE.md](performance/REDIS_QUEUE_SEPARATION_GUIDE.md) | Redis队列分离完整指南 | 生产部署 |
| [REDIS_QUEUE_SEPARATION_COMPLETE.md](performance/REDIS_QUEUE_SEPARATION_COMPLETE.md) | 队列分离完成总结 | 实施验证 |
| [SCALE_TO_10K_GUIDE.md](performance/SCALE_TO_10K_GUIDE.md) | 扩展到10000+条/秒指南 | 高性能需求 |
| [SCALE_TO_10K_COMPLETE.md](performance/SCALE_TO_10K_COMPLETE.md) | 超高性能完成总结 | 实施验证 |
| [PERFORMANCE_QUICK_REFERENCE.md](performance/PERFORMANCE_QUICK_REFERENCE.md) | 性能配置快速参考 | 速查手册 |
| [UVICORN_WORKERS_VS_REDIS_WORKERS.md](performance/UVICORN_WORKERS_VS_REDIS_WORKERS.md) | Uvicorn Workers问题详解 | 问题排查 |
| [REDIS_QUEUE_PERFORMANCE_ANALYSIS.md](performance/REDIS_QUEUE_PERFORMANCE_ANALYSIS.md) | Redis队列性能分析 | 性能调优 |
| [QUICK_PERFORMANCE_GUIDE.md](performance/QUICK_PERFORMANCE_GUIDE.md) | 快速性能优化指南 | 快速优化 |

### 📖 使用指南 (`guides/`)

| 文档 | 说明 |
|------|------|
| [REDIS_QUEUE_GUIDE.md](guides/REDIS_QUEUE_GUIDE.md) | Redis队列使用指南 |
| [REDIS_CACHE_LOGIC.md](guides/REDIS_CACHE_LOGIC.md) | Redis缓存逻辑说明 |
| [REDIS_PIPELINE_SEPARATION.md](guides/REDIS_PIPELINE_SEPARATION.md) | Redis管道分离设计 |
| [PERMISSION_QUICK_START.md](guides/PERMISSION_QUICK_START.md) | 权限管理快速开始 |
| [RBAC_README.md](guides/RBAC_README.md) | RBAC使用指南 |
| [MAIL_VIEWER_QUICK_START.md](guides/MAIL_VIEWER_QUICK_START.md) | 邮件查看器快速开始 |
| [MENU_BINDING_GUIDE.md](guides/MENU_BINDING_GUIDE.md) | 菜单绑定指南 |
| [PERMISSION_MANAGE_README.md](guides/PERMISSION_MANAGE_README.md) | 权限管理详细说明 |

### 🎯 功能文档 (`features/`)

| 文档 | 说明 |
|------|------|
| [MAIL_VIEWER_FEATURE.md](features/MAIL_VIEWER_FEATURE.md) | 邮件查看器功能 |
| [WALLET_FEATURE_UPDATE.md](features/WALLET_FEATURE_UPDATE.md) | 钱包功能更新 |
| [PROJECT_USER_MANAGEMENT.md](features/PROJECT_USER_MANAGEMENT.md) | 项目用户管理 |
| [COPY_ID_FEATURE.md](features/COPY_ID_FEATURE.md) | 复制ID功能 |

### 🏗 RBAC设计 (`rbac/`)

| 文档 | 说明 |
|------|------|
| [COMPARISON.md](rbac/COMPARISON.md) | RBAC设计对比 |
| [ENTERPRISE_RBAC_DESIGN.md](rbac/ENTERPRISE_RBAC_DESIGN.md) | 企业级RBAC设计 |
| [MODERN_RBAC_DESIGN.md](rbac/MODERN_RBAC_DESIGN.md) | 现代RBAC设计 |
| [PRACTICAL_RBAC_DESIGN.md](rbac/PRACTICAL_RBAC_DESIGN.md) | 实用RBAC设计 |
| [V1_VS_V2_COMPARISON.md](rbac/V1_VS_V2_COMPARISON.md) | V1 vs V2对比 |
| [IMPLEMENTATION_GUIDE.md](rbac/IMPLEMENTATION_GUIDE.md) | 实施指南 |
| [QUICK_START.md](rbac/QUICK_START.md) | 快速开始 |

### 📊 功能总结 (`summaries/`)

| 文档 | 说明 |
|------|------|
| [REDIS_QUEUE_FINAL_SUMMARY.md](summaries/REDIS_QUEUE_FINAL_SUMMARY.md) | Redis队列实现总结 |
| [RBAC_COMPLETE.md](summaries/RBAC_COMPLETE.md) | RBAC实现总结 |
| [DATA_PERMISSION_SUMMARY.md](summaries/DATA_PERMISSION_SUMMARY.md) | 数据权限总结 |
| [MAIL_VIEWER_IMPLEMENTATION_SUMMARY.md](summaries/MAIL_VIEWER_IMPLEMENTATION_SUMMARY.md) | 邮件查看器实现总结 |
| [BATCH_OPERATIONS_SUMMARY.md](summaries/BATCH_OPERATIONS_SUMMARY.md) | 批量操作总结 |
| [SYSTEM_STATUS_SUMMARY.md](summaries/SYSTEM_STATUS_SUMMARY.md) | 系统状态总结 |

### 🔧 修复记录 (`fixes/`)

#### JWT认证相关
- [JWT_AUTH_ONLY.md](fixes/JWT_AUTH_ONLY.md) - JWT认证统一
- [JWT_UPDATE_SUMMARY.md](fixes/JWT_UPDATE_SUMMARY.md) - JWT更新总结
- [JWT_TOKEN_QUICK_START.md](fixes/JWT_TOKEN_QUICK_START.md) - JWT Token快速开始
- [SWAGGER_JWT_GUIDE.md](fixes/SWAGGER_JWT_GUIDE.md) - Swagger JWT指南
- [API_TOKEN_JWT_10YEARS.md](fixes/API_TOKEN_JWT_10YEARS.md) - 10年API Token
- [API_TOKEN_JWT_10YEARS_COMPLETE.md](fixes/API_TOKEN_JWT_10YEARS_COMPLETE.md) - 10年API Token完整版

#### RBAC权限相关
- [RBAC_CLEANUP_SUMMARY.md](fixes/RBAC_CLEANUP_SUMMARY.md) - RBAC清理总结
- [RBAC_API_REFERENCE.md](fixes/RBAC_API_REFERENCE.md) - RBAC API参考
- [RBAC_UNUSED_APIS.md](fixes/RBAC_UNUSED_APIS.md) - RBAC未使用API
- [PERMISSION_COMPLETE.md](fixes/PERMISSION_COMPLETE.md) - 权限系统完整文档
- [PERMISSION_FIX_FINAL_SUMMARY.md](fixes/PERMISSION_FIX_FINAL_SUMMARY.md) - 权限修复最终总结
- [DATA_PERMISSION_COMPLETE.md](fixes/DATA_PERMISSION_COMPLETE.md) - 数据权限完整文档

#### 日志系统相关
- [LOG_USER_ID_UPDATE.md](fixes/LOG_USER_ID_UPDATE.md) - 日志记录用户ID更新

#### 其他修复
- [UPSERT_PARTIAL_UPDATE.md](fixes/UPSERT_PARTIAL_UPDATE.md) - Upsert部分更新
- [MENU_FIX_COMPLETE.md](fixes/MENU_FIX_COMPLETE.md) - 菜单修复完整版
- [DASHBOARD_MULTI_ROLE_FIX.md](fixes/DASHBOARD_MULTI_ROLE_FIX.md) - 仪表盘多角色修复

### 🔌 API文档 (`api/`)

| 文档 | 说明 |
|------|------|
| [API_AUTH_IMPLEMENTATION.md](api/API_AUTH_IMPLEMENTATION.md) | API认证实现 |
| [API_AUTH_COMPLETE.md](api/API_AUTH_COMPLETE.md) | API认证完整文档 |
| [API_404_SILENT_HANDLING.md](api/API_404_SILENT_HANDLING.md) | API 404静默处理 |

## 🔍 按场景查找文档

### 我想开始使用这个项目

1. [README.md](../README.md) - 项目总览
2. [backend/README.md](../backend/README.md) - 后端快速开始
3. [frontend/README.md](../frontend/README.md) - 前端快速开始

### 我想优化性能

1. [PERFORMANCE_QUICK_REFERENCE.md](performance/PERFORMANCE_QUICK_REFERENCE.md) - 快速参考
2. [QUEUE_SEPARATION_QUICK_START.md](performance/QUEUE_SEPARATION_QUICK_START.md) - 队列分离（2000条/秒）
3. [SCALE_TO_10K_GUIDE.md](performance/SCALE_TO_10K_GUIDE.md) - 超高性能（10000+条/秒）

### 我想了解RBAC权限系统

1. [guides/RBAC_README.md](guides/RBAC_README.md) - RBAC使用指南
2. [rbac/QUICK_START.md](rbac/QUICK_START.md) - 快速开始
3. [rbac/IMPLEMENTATION_GUIDE.md](rbac/IMPLEMENTATION_GUIDE.md) - 实施指南

### 我想使用Redis队列

1. [guides/REDIS_QUEUE_GUIDE.md](guides/REDIS_QUEUE_GUIDE.md) - 使用指南
2. [guides/REDIS_CACHE_LOGIC.md](guides/REDIS_CACHE_LOGIC.md) - 缓存逻辑
3. [performance/REDIS_QUEUE_PERFORMANCE_ANALYSIS.md](performance/REDIS_QUEUE_PERFORMANCE_ANALYSIS.md) - 性能分析

### 我想部署到生产环境

1. [performance/REDIS_QUEUE_SEPARATION_GUIDE.md](performance/REDIS_QUEUE_SEPARATION_GUIDE.md) - 队列分离部署
2. [performance/SCALE_TO_10K_GUIDE.md](performance/SCALE_TO_10K_GUIDE.md) - 高性能部署
3. [README.md](../README.md#部署指南) - 部署指南

### 我遇到了问题

1. [performance/UVICORN_WORKERS_VS_REDIS_WORKERS.md](performance/UVICORN_WORKERS_VS_REDIS_WORKERS.md) - Workers问题
2. [backend/README.md](../backend/README.md#常见问题) - 常见问题
3. [fixes/](fixes/) - 修复记录

## 📝 文档更新记录

- **2026-01-23**: 完成性能优化文档，支持10000+条/秒
- **2026-01-23**: 完成队列分离部署文档
- **2026-01-23**: 完成JWT认证统一文档
- **2026-01-23**: 完成RBAC清理文档
- **2026-01-23**: 完成日志系统更新文档

## 🤝 贡献文档

如果你想为文档做贡献：

1. 文档使用Markdown格式
2. 放在对应的分类目录下
3. 更新本索引文件
4. 提交Pull Request

---

**最后更新**: 2026-01-23  
**文档总数**: 80+
