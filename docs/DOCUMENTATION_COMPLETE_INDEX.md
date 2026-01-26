# QYD 项目文档完整索引

所有项目文档的完整索引和导航。

## 📋 目录

- [快速开始](#快速开始)
- [部署文档](#部署文档)
- [开发文档](#开发文档)
- [功能文档](#功能文档)
- [性能优化](#性能优化)
- [安全与加密](#安全与加密)
- [日志管理](#日志管理)
- [测试文档](#测试文档)
- [脚本工具](#脚本工具)
- [故障排查](#故障排查)

---

## 快速开始

### 核心文档

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [README.md](../README.md) | 项目总览 | ⭐⭐⭐⭐⭐ |
| [STARTUP_GUIDE.md](../STARTUP_GUIDE.md) | 启动指南（所有场景） | ⭐⭐⭐⭐⭐ |
| [QUICK_START.md](../QUICK_START.md) | 快速开始（本地部署） | ⭐⭐⭐⭐ |
| [DOCKER_QUICK_START.md](../DOCKER_QUICK_START.md) | Docker 快速部署 | ⭐⭐⭐⭐⭐ |

### 选择指南

- **首次使用**: 阅读 [README.md](../README.md) 了解项目
- **本地开发**: 参考 [STARTUP_GUIDE.md](../STARTUP_GUIDE.md) 场景 1
- **快速体验**: 使用 [DOCKER_QUICK_START.md](../DOCKER_QUICK_START.md)
- **生产部署**: 参考 [STARTUP_GUIDE.md](../STARTUP_GUIDE.md) 场景 3 或 4

---

## 部署文档

### 部署指南 (`docs/deployment/`)

| 文档 | 说明 | 适用场景 |
|------|------|---------|
| [DEPLOYMENT_ARCHITECTURE.md](deployment/DEPLOYMENT_ARCHITECTURE.md) | 部署架构说明 | 了解系统架构 |
| [DOCKER_DEPLOYMENT.md](deployment/DOCKER_DEPLOYMENT.md) | Docker 完整部署 | Docker 生产部署 |
| [DOCKER_QUICK_REFERENCE.md](deployment/DOCKER_QUICK_REFERENCE.md) | Docker 快速参考 | Docker 命令速查 |
| [FRONTEND_DEPLOYMENT.md](deployment/FRONTEND_DEPLOYMENT.md) | 前端部署详解 | 前端部署 |
| [COMPLETE_DEPLOYMENT_SETUP.md](deployment/COMPLETE_DEPLOYMENT_SETUP.md) | 完整部署设置 | 完整部署流程 |

### 根目录部署文档

| 文档 | 说明 | 适用场景 |
|------|------|---------|
| [NATIVE_DEPLOYMENT.md](../NATIVE_DEPLOYMENT.md) | 本地部署指南 | 传统部署方式 |
| [HIGH_CONCURRENCY_DEPLOYMENT.md](../HIGH_CONCURRENCY_DEPLOYMENT.md) | 高并发部署 | 高性能生产环境 |
| [DEPLOYMENT_CHECKLIST.md](../DEPLOYMENT_CHECKLIST.md) | 部署检查清单 | 部署前检查 |

### 后端部署文档 (`backend/`)

| 文档 | 说明 | 适用场景 |
|------|------|---------|
| [backend/DEPLOYMENT_GUIDE.md](../backend/DEPLOYMENT_GUIDE.md) | 后端部署指南 | 后端详细部署 |
| [backend/QUICK_DEPLOY_REFERENCE.md](../backend/QUICK_DEPLOY_REFERENCE.md) | 后端快速部署 | 后端快速参考 |

---

## 开发文档

### 开发规范

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [.kiro/steering/conventions.md](../.kiro/steering/conventions.md) | 开发规范和最佳实践 | ⭐⭐⭐⭐⭐ |
| [.kiro/steering/structure.md](../.kiro/steering/structure.md) | 项目结构说明 | ⭐⭐⭐⭐⭐ |
| [.kiro/steering/tech.md](../.kiro/steering/tech.md) | 技术栈说明 | ⭐⭐⭐⭐ |
| [.kiro/steering/product.md](../.kiro/steering/product.md) | 产品概述 | ⭐⭐⭐ |

### 后端开发

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [backend/README.md](../backend/README.md) | 后端开发指南 | ⭐⭐⭐⭐⭐ |
| [backend/docs/README.md](../backend/docs/README.md) | 后端文档索引 | ⭐⭐⭐⭐ |

### 前端开发

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [frontend/README.md](../frontend/README.md) | 前端开发指南 | ⭐⭐⭐⭐⭐ |

---

## 功能文档

### 核心功能 (`docs/features/`)

#### 用户管理

| 文档 | 说明 |
|------|------|
| [PROJECT_USER_MANAGEMENT.md](features/PROJECT_USER_MANAGEMENT.md) | 项目用户管理 |
| [WALLET_FEATURE_UPDATE.md](features/WALLET_FEATURE_UPDATE.md) | 钱包功能更新 |

#### 项目管理 (`docs/features/project/`)

| 文档 | 说明 |
|------|------|
| [PROJECT_ACCOUNT_FEATURES_SUMMARY.md](features/PROJECT_ACCOUNT_FEATURES_SUMMARY.md) | 项目账号功能总结 |
| [PROJECT_ACCOUNT_STATS_FEATURE.md](features/PROJECT_ACCOUNT_STATS_FEATURE.md) | 项目账号统计功能 |
| [PROJECT_STATS_EXPORT_FEATURE.md](features/PROJECT_STATS_EXPORT_FEATURE.md) | 项目统计导出功能 |

#### 服务器管理 (`docs/server/`)

| 文档 | 说明 |
|------|------|
| [SERVER_ACCOUNT_FINAL_SUMMARY.md](server/SERVER_ACCOUNT_FINAL_SUMMARY.md) | 服务器账号功能总结 |
| [SERVER_ACCOUNT_PASSWORD_VISIBILITY_TOGGLE.md](server/SERVER_ACCOUNT_PASSWORD_VISIBILITY_TOGGLE.md) | 密码显示切换 |

#### 邮件管理 (`docs/mail/`)

| 文档 | 说明 |
|------|------|
| [MAIL_VIEWER_FINAL_UPDATE.md](mail/MAIL_VIEWER_FINAL_UPDATE.md) | 邮件查看器最终更新 |
| [MAIL_SEND_FEATURE.md](mail/MAIL_SEND_FEATURE.md) | 邮件发送功能 |

#### API Token (`docs/features/api-token/`)

| 文档 | 说明 |
|------|------|
| [API_TOKEN_JWT_10YEARS_COMPLETE.md](fixes/API_TOKEN_JWT_10YEARS_COMPLETE.md) | API Token 10年有效期 |

#### Redis 队列 (`docs/features/redis/`)

| 文档 | 说明 |
|------|------|
| [REDIS_QUEUE_MANUAL_START.md](features/REDIS_QUEUE_MANUAL_START.md) | Redis 队列手动启动 |
| [AUTO_START_QUEUE_WORKER.md](features/AUTO_START_QUEUE_WORKER.md) | 队列 Worker 自动启动 |

---

## 性能优化

### 性能文档 (`docs/performance/`)

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [PERFORMANCE_QUICK_REFERENCE.md](performance/PERFORMANCE_QUICK_REFERENCE.md) | 性能配置快速参考 | ⭐⭐⭐⭐⭐ |
| [SCALE_TO_10K_GUIDE.md](performance/SCALE_TO_10K_GUIDE.md) | 扩展到 10000+ QPS | ⭐⭐⭐⭐⭐ |
| [ULTRA_HIGH_PERFORMANCE_GUIDE.md](performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md) | 超高性能指南 | ⭐⭐⭐⭐ |
| [REDIS_QUEUE_SEPARATION_GUIDE.md](performance/REDIS_QUEUE_SEPARATION_GUIDE.md) | Redis 队列分离指南 | ⭐⭐⭐⭐ |
| [QUEUE_SEPARATION_QUICK_START.md](performance/QUEUE_SEPARATION_QUICK_START.md) | 队列分离快速开始 | ⭐⭐⭐⭐ |
| [UVICORN_WORKERS_VS_REDIS_WORKERS.md](performance/UVICORN_WORKERS_VS_REDIS_WORKERS.md) | Workers 对比说明 | ⭐⭐⭐ |

### 性能配置对比

| 配置 | 队列进程 | Workers | 批处理 | 性能 | 文档 |
|------|---------|---------|--------|------|------|
| 标准 | 1 | 8 | 300 | 2700条/秒 | [QUEUE_SEPARATION_QUICK_START.md](performance/QUEUE_SEPARATION_QUICK_START.md) |
| 高性能 | 2 | 10 | 400 | 6000条/秒 | [REDIS_QUEUE_SEPARATION_GUIDE.md](performance/REDIS_QUEUE_SEPARATION_GUIDE.md) |
| 超高性能 | 3 | 12 | 500 | 12000条/秒 | [SCALE_TO_10K_GUIDE.md](performance/SCALE_TO_10K_GUIDE.md) |
| 极限性能 | 5 | 12 | 800 | 20000条/秒 | [ULTRA_HIGH_PERFORMANCE_GUIDE.md](performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md) |

---

## 安全与加密

### 加密文档 (`docs/encryption/`)

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [PROJECT_ACCOUNT_ENCRYPTION.md](encryption/PROJECT_ACCOUNT_ENCRYPTION.md) | 项目账号加密详细文档 | ⭐⭐⭐⭐⭐ |
| [PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md](encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md) | 加密功能快速参考 | ⭐⭐⭐⭐⭐ |
| [PROJECT_ACCOUNT_ENCRYPTION_FLOW.md](encryption/PROJECT_ACCOUNT_ENCRYPTION_FLOW.md) | 加密流程图 | ⭐⭐⭐⭐ |
| [SOCKS5_ACCOUNT_AES_ENCRYPTION.md](encryption/SOCKS5_ACCOUNT_AES_ENCRYPTION.md) | SOCKS5 账号加密 | ⭐⭐⭐ |

### 安全功能

- ✅ AES-CBC 加密（项目账号敏感数据）
- ✅ 每个项目独立密钥
- ✅ 基于权限的自动解密
- ✅ JWT Token 认证
- ✅ bcrypt 密码加密
- ✅ API Token 管理

---

## 日志管理

### 日志文档 (`docs/logs/`)

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [LOG_SYSTEM_COMPLETE.md](logs/LOG_SYSTEM_COMPLETE.md) | 日志系统完整文档 | ⭐⭐⭐⭐⭐ |
| [LOG_QUICK_REFERENCE.md](logs/LOG_QUICK_REFERENCE.md) | 日志快速参考 | ⭐⭐⭐⭐⭐ |
| [LOG_MANAGEMENT_UPDATE.md](logs/LOG_MANAGEMENT_UPDATE.md) | 日志管理更新说明 | ⭐⭐⭐ |
| [LOG_MANAGEMENT_SUMMARY.md](logs/LOG_MANAGEMENT_SUMMARY.md) | 日志管理总结 | ⭐⭐⭐ |

### 日志特性

- ✅ 按模块分类（api、app、database、scheduler）
- ✅ 自动轮转（按小时）
- ✅ 自动压缩（.gz 格式）
- ✅ 90 天保留期
- ✅ 四层目录结构

---

## 测试文档

### 测试说明

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [backend/tests/README.md](../backend/tests/README.md) | 后端测试说明 | ⭐⭐⭐⭐⭐ |
| [frontend/tests/README.md](../frontend/tests/README.md) | 前端测试说明 | ⭐⭐⭐⭐ |

### 测试类型

| 类型 | 目录 | 说明 |
|------|------|------|
| API 测试 | `backend/tests/api/` | 接口功能测试 |
| 集成测试 | `backend/tests/integration/` | 系统集成测试 |
| 性能测试 | `backend/tests/performance/` | 性能压测 |
| 单元测试 | `backend/tests/unit/` | 单元功能测试 |

---

## 脚本工具

### 脚本索引

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [scripts/SCRIPTS_INDEX.md](../scripts/SCRIPTS_INDEX.md) | 脚本工具完整索引 | ⭐⭐⭐⭐⭐ |
| [backend/scripts/README.md](../backend/scripts/README.md) | 后端脚本说明 | ⭐⭐⭐⭐ |

### 脚本分类

| 类型 | 目录 | 说明 |
|------|------|------|
| 部署脚本 | 根目录 | 环境安装、项目部署 |
| 服务管理 | 根目录 | 启动、重启、更新服务 |
| 数据库脚本 | `scripts/mysql/`, `backend/db/` | MySQL 管理、数据迁移 |
| 测试脚本 | `scripts/test/` | API 测试、权限测试 |
| 调试脚本 | `scripts/debug/` | 问题诊断、调试工具 |
| 工具脚本 | `scripts/utils/`, `backend/scripts/` | 备份、日志管理等 |

---

## 故障排查

### 故障排查文档 (`docs/fixes/`)

#### 常见问题

| 文档 | 说明 |
|------|------|
| [TROUBLESHOOTING.md](fixes/TROUBLESHOOTING.md) | 故障排查指南 |
| [PORT_ALREADY_IN_USE_FIX.md](fixes/PORT_ALREADY_IN_USE_FIX.md) | 端口占用问题 |
| [FIX_502_ERROR.md](fixes/FIX_502_ERROR.md) | 502 错误修复 |

#### 权限问题

| 文档 | 说明 |
|------|------|
| [PERMISSION_COMPLETE.md](fixes/PERMISSION_COMPLETE.md) | 权限系统完整文档 |
| [DATA_PERMISSION_QUICK_REFERENCE.md](fixes/DATA_PERMISSION_QUICK_REFERENCE.md) | 数据权限快速参考 |
| [PERMISSION_FIX_FINAL_SUMMARY.md](fixes/PERMISSION_FIX_FINAL_SUMMARY.md) | 权限修复总结 |

#### JWT 认证

| 文档 | 说明 |
|------|------|
| [JWT_TOKEN_QUICK_START.md](fixes/JWT_TOKEN_QUICK_START.md) | JWT Token 快速开始 |
| [JWT_AUTH_FIX.md](fixes/JWT_AUTH_FIX.md) | JWT 认证修复 |
| [SWAGGER_JWT_GUIDE.md](fixes/SWAGGER_JWT_GUIDE.md) | Swagger JWT 使用指南 |

#### 数据库问题

| 文档 | 说明 |
|------|------|
| [DATABASE_CORRECTION.md](fixes/DATABASE_CORRECTION.md) | 数据库修正 |
| [REDIS_CACHE_DB_SEPARATION.md](fixes/REDIS_CACHE_DB_SEPARATION.md) | Redis 缓存数据库分离 |

---

## RBAC 权限系统

### RBAC 设计文档 (`docs/rbac/`)

| 文档 | 说明 | 推荐指数 |
|------|------|---------|
| [QUICK_START.md](rbac/QUICK_START.md) | RBAC 快速开始 | ⭐⭐⭐⭐⭐ |
| [PRACTICAL_RBAC_DESIGN.md](rbac/PRACTICAL_RBAC_DESIGN.md) | 实用 RBAC 设计 | ⭐⭐⭐⭐⭐ |
| [MODERN_RBAC_DESIGN.md](rbac/MODERN_RBAC_DESIGN.md) | 现代 RBAC 设计 | ⭐⭐⭐⭐ |
| [ENTERPRISE_RBAC_DESIGN.md](rbac/ENTERPRISE_RBAC_DESIGN.md) | 企业级 RBAC 设计 | ⭐⭐⭐⭐ |
| [V1_VS_V2_COMPARISON.md](rbac/V1_VS_V2_COMPARISON.md) | V1 vs V2 对比 | ⭐⭐⭐ |
| [COMPARISON.md](rbac/COMPARISON.md) | RBAC 方案对比 | ⭐⭐⭐ |

### RBAC 使用指南 (`docs/guides/`)

| 文档 | 说明 |
|------|------|
| [RBAC_README.md](guides/RBAC_README.md) | RBAC 使用指南 |
| [PERMISSION_QUICK_START.md](guides/PERMISSION_QUICK_START.md) | 权限快速开始 |
| [PERMISSION_MANAGE_GUIDE.md](guides/PERMISSION_MANAGE_GUIDE.md) | 权限管理指南 |
| [MENU_BINDING_GUIDE.md](guides/MENU_BINDING_GUIDE.md) | 菜单绑定指南 |

---

## 导出功能

### 导出文档 (`docs/export/`)

| 文档 | 说明 |
|------|------|
| [EXPORT_FEATURE_COMPLETE.md](export/EXPORT_FEATURE_COMPLETE.md) | 导出功能完整文档 |
| [QUICK_REFERENCE_EXPORT.md](export/QUICK_REFERENCE_EXPORT.md) | 导出快速参考 |
| [FINAL_EXPORT_SUMMARY.md](export/FINAL_EXPORT_SUMMARY.md) | 导出功能总结 |

---

## API 文档

### API 认证文档 (`docs/api/`)

| 文档 | 说明 |
|------|------|
| [API_AUTH_COMPLETE.md](api/API_AUTH_COMPLETE.md) | API 认证完整文档 |
| [API_AUTH_IMPLEMENTATION.md](api/API_AUTH_IMPLEMENTATION.md) | API 认证实现 |

### 在线 API 文档

- **Swagger UI**: http://localhost:6080/docs
- **ReDoc**: http://localhost:6080/redoc

---

## 项目总结

### 总结文档 (`docs/summaries/`)

| 文档 | 说明 |
|------|------|
| [PROJECT_ORGANIZATION_COMPLETE.md](summaries/PROJECT_ORGANIZATION_COMPLETE.md) | 项目整理完整总结 |
| [FINAL_SUMMARY_20260121.md](fixes/FINAL_SUMMARY_20260121.md) | 2026-01-21 总结 |

---

## 使用指南 (`docs/guides/`)

### Redis 相关

| 文档 | 说明 |
|------|------|
| [REDIS_QUEUE_GUIDE.md](guides/REDIS_QUEUE_GUIDE.md) | Redis 队列使用指南 |
| [REDIS_CACHE_LOGIC.md](guides/REDIS_CACHE_LOGIC.md) | Redis 缓存逻辑 |
| [REDIS_PIPELINE_SEPARATION.md](guides/REDIS_PIPELINE_SEPARATION.md) | Redis 管道分离 |

### 邮件相关

| 文档 | 说明 |
|------|------|
| [MAIL_VIEWER_QUICK_START.md](guides/MAIL_VIEWER_QUICK_START.md) | 邮件查看器快速开始 |
| [MAIL_VIEWER_TROUBLESHOOTING.md](guides/MAIL_VIEWER_TROUBLESHOOTING.md) | 邮件查看器故障排查 |

---

## 基础设施

### 数据库文档 (`docs/infrastructure/`)

| 文档 | 说明 |
|------|------|
| [mysql主从.md](mysql主从.md) | MySQL 主从复制 |
| [mysql主从-单服务器快速部署.md](mysql主从-单服务器快速部署.md) | 单服务器主从部署 |
| [mysql主从-单服务器分步部署教程.md](mysql主从-单服务器分步部署教程.md) | 分步部署教程 |
| [读写分离-using_db修复.md](infrastructure/读写分离-using_db修复.md) | 读写分离修复 |
| [读写分离-轮询负载均衡.md](infrastructure/读写分离-轮询负载均衡.md) | 负载均衡 |

---

## 文档导航建议

### 新手入门路径

1. [README.md](../README.md) - 了解项目
2. [STARTUP_GUIDE.md](../STARTUP_GUIDE.md) - 选择启动方式
3. [DOCKER_QUICK_START.md](../DOCKER_QUICK_START.md) - 快速体验
4. [.kiro/steering/conventions.md](../.kiro/steering/conventions.md) - 学习开发规范

### 开发者路径

1. [backend/README.md](../backend/README.md) - 后端开发
2. [frontend/README.md](../frontend/README.md) - 前端开发
3. [.kiro/steering/conventions.md](../.kiro/steering/conventions.md) - 开发规范
4. [backend/tests/README.md](../backend/tests/README.md) - 测试指南

### 运维路径

1. [NATIVE_DEPLOYMENT.md](../NATIVE_DEPLOYMENT.md) - 本地部署
2. [HIGH_CONCURRENCY_DEPLOYMENT.md](../HIGH_CONCURRENCY_DEPLOYMENT.md) - 高并发部署
3. [performance/SCALE_TO_10K_GUIDE.md](performance/SCALE_TO_10K_GUIDE.md) - 性能优化
4. [scripts/SCRIPTS_INDEX.md](../scripts/SCRIPTS_INDEX.md) - 脚本工具

### 故障排查路径

1. [fixes/TROUBLESHOOTING.md](fixes/TROUBLESHOOTING.md) - 故障排查指南
2. [scripts/SCRIPTS_INDEX.md](../scripts/SCRIPTS_INDEX.md) - 调试脚本
3. [logs/LOG_QUICK_REFERENCE.md](logs/LOG_QUICK_REFERENCE.md) - 日志查看
4. 相关功能文档

---

## 文档维护

### 文档更新规范

1. **命名规范**: 使用大写字母和下划线，描述性命名
2. **格式规范**: 使用 Markdown 格式，统一标题层级
3. **内容规范**: 包含目录、说明、示例、相关文档链接
4. **版本信息**: 文档末尾注明最后更新日期和版本

### 文档分类

- **快速开始**: 简洁明了，快速上手
- **详细指南**: 完整详细，深入讲解
- **快速参考**: 速查表格，命令列表
- **故障排查**: 问题诊断，解决方案

---

## 相关资源

### 外部文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [React 官方文档](https://react.dev/)
- [Ant Design 文档](https://ant.design/)
- [Docker 官方文档](https://docs.docker.com/)
- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [Redis 官方文档](https://redis.io/documentation)

### 社区资源

- GitHub Issues
- Stack Overflow
- 技术博客

---

**最后更新**: 2026-01-26  
**文档总数**: 200+  
**版本**: v1.0.0
