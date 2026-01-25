# 项目文档索引

本文档提供项目所有文档的分类索引，方便快速查找。

## 📁 文档结构

```
docs/
├── features/           # 功能特性文档
│   ├── wallet/        # 钱包功能
│   ├── project/       # 项目管理
│   ├── xui/           # XUI集成
│   ├── server/        # 服务器管理
│   ├── security/      # 安全日志
│   ├── api-token/     # API Token
│   ├── frontend/      # 前端功能
│   ├── redis/         # Redis相关
│   └── proxy/         # 代理功能
├── development/       # 开发文档
│   └── clients/       # 客户端开发文档
├── infrastructure/    # 基础设施文档
├── api/              # API文档
├── encryption/       # 加密相关
├── export/           # 导出功能
├── fixes/            # 问题修复记录
├── guides/           # 使用指南
├── logs/             # 日志相关
├── mail/             # 邮件功能
├── performance/      # 性能优化
├── rbac/             # 权限管理
├── server/           # 服务器相关
└── summaries/        # 功能总结

backend/
└── examples/         # 代码示例

scripts/
├── test/             # 测试脚本
├── mysql/            # MySQL脚本
├── debug/            # 调试工具
└── utils/            # 工具脚本
```

## 🎯 快速导航

### 核心功能

- [快速开始指南](../QUICK_START_GUIDE.md)
- [项目README](../README.md)
- [项目结构说明](PROJECT_STRUCTURE.md)

### 钱包功能 (features/wallet/)

- [批量创建钱包功能说明](features/wallet/批量创建钱包功能说明.md)
- [批量创建钱包快速开始](features/wallet/批量创建钱包快速开始.md)
- [钱包功能完整实现总结](features/wallet/批量创建钱包完整实现总结.md)

### 项目管理 (features/project/)

- [项目文件管理功能](features/project/PROJECT_FILE_MANAGEMENT.md)
- [项目账号加密](features/project/PROJECT_ACCOUNT_ENCRYPTION_SUMMARY.md)
- [项目提现功能](features/project/PROJECT_WITHDRAWAL_FEATURE.md)
- [项目统计功能](features/project/项目统计功能-完整实现总结.md)

### XUI集成 (features/xui/)

- [XUI快速参考](features/xui/XUI_QUICK_REFERENCE.md)
- [XUI完整集成](features/xui/XUI_COMPLETE_INTEGRATION.md)
- [XUI同步功能](features/xui/XUI_SYNC_FEATURE.md)
- [XUI账号状态自动更新](features/xui/XUI_ACCOUNT_STATUS_AUTO_UPDATE.md)

### 服务器管理 (features/server/)

- [服务器列表筛选增强](features/server/SERVER_LIST_FILTER_ENHANCEMENT.md)
- [服务器代理类型识别](features/server/SERVER_PROXY_TYPE_FIX.md)
- [服务器分组批量删除](features/server/SERVER_GROUP_BATCH_DELETE.md)
- [代理测试功能](features/server/SERVER_PROXY_TEST_FEATURE.md)

### 安全功能 (features/security/)

- [安全日志实现](features/security/SECURITY_LOG_IMPLEMENTATION.md)
- [安全日志快速参考](features/security/SECURITY_LOG_QUICK_REFERENCE.md)

### API Token (features/api-token/)

- [API Token快速参考](features/api-token/API_TOKEN_QUICK_REFERENCE.md)
- [API Token流程图](features/api-token/API_TOKEN_FLOW_DIAGRAM.md)
- [Token批量操作](features/api-token/TOKEN_BATCH_OPERATIONS.md)

### 前端功能 (features/frontend/)

- [前端表单修复](features/frontend/FRONTEND_FORMS_FIX_COMPLETE.md)
- [仪表盘优化](features/frontend/仪表盘优化-移除项目列表.md)

### 代理功能 (features/proxy/)

- [代理检测API](features/proxy/PROXY_CHECK_API.md)
- [代理检测前端](features/proxy/PROXY_CHECK_FRONTEND.md)

### Redis相关 (features/redis/)

- [Redis数据库分离](features/redis/REDIS_DATABASE_SEPARATION.md)

### 基础设施 (infrastructure/)

- [读写分离配置](infrastructure/读写分离-轮询负载均衡.md)
- [时间参数修复](infrastructure/时间参数查询错误修复总结.md)

## 🔧 开发指南

### 客户端开发 (development/clients/)

- [XUI客户端README](development/clients/XUI_CLIENT_README.md)
- [XUI优化总结](development/clients/XUI_OPTIMIZATION_SUMMARY.md)

### XUI API开发 (development/xui-api/)

- [XUI API README](development/xui-api/XUI_API_README.md)
- [XUI集成指南](development/xui-api/XUI_INTEGRATION_GUIDE.md)
- [XUI API总结](development/xui-api/XUI_API_SUMMARY.md)
- [同步Inbounds指南](development/xui-api/SYNC_INBOUNDS_GUIDE.md)
- [默认凭证](development/xui-api/DEFAULT_CREDENTIALS.md)

### 测试 (development/testing/)

- [测试README](development/testing/TESTING_README.md)

### 日志 (development/logging/)

- [日志README](development/logging/LOGGING_README.md)
- [日志使用指南](development/logging/LOGGING_USAGE.md)

### 代码示例 (backend/examples/)

- `xui_example.py` - XUI客户端使用示例

### RBAC权限系统

- [RBAC设计文档](RBAC_DESIGN.md)
- [RBAC快速开始](RBAC_QUICK_START.md)
- [权限管理指南](guides/RBAC_README.md)

### 数据加密

- [项目账号加密](encryption/PROJECT_ACCOUNT_ENCRYPTION.md)
- [SOCKS5账号AES加密](encryption/SOCKS5_ACCOUNT_AES_ENCRYPTION.md)

### 导出功能

- [导出功能完整实现](export/EXPORT_FEATURE_COMPLETE.md)
- [导出快速参考](export/QUICK_REFERENCE_EXPORT.md)

### 邮件功能

- [邮件查看器快速开始](guides/MAIL_VIEWER_QUICK_START.md)
- [邮件查看器故障排除](guides/MAIL_VIEWER_TROUBLESHOOTING.md)

## 📝 问题修复记录

所有问题修复记录都在 [fixes/](fixes/) 目录下，包括：

- API认证修复
- 前端错误处理
- 数据库修正
- 权限系统修复
- 性能优化

## 🧪 测试脚本

测试脚本位于 `scripts/test/` 目录：

- `test_balance_fix.sh` - 余额修复测试
- `test_server_account_fix.sh` - 服务器账号测试
- `test_upsert_redis.sh` - Redis更新测试
- `fix_all_forms.sh` - 表单修复脚本

## 📊 MySQL相关

MySQL部署和管理文档：

- [MySQL主从复制](mysql主从.md)
- [单服务器快速部署](mysql主从-单服务器快速部署.md)
- [主从复制问题总结](mysql主从复制问题总结.md)

## 🔍 搜索建议

- 功能实现：查看 `features/` 对应分类
- 问题修复：查看 `fixes/` 目录
- 使用指南：查看 `guides/` 目录
- API文档：查看 `api/` 目录

## 📅 最后更新

2026-01-26
