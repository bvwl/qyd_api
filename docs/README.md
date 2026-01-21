# QYD 项目文档

本目录包含项目的所有文档和修复记录。

## 文档结构

```
docs/
├── README.md           # 本文档
└── fixes/              # 修复记录和开发文档
    ├── JWT认证相关
    ├── 密码加密相关
    ├── 前端功能开发
    ├── 后端API修复
    └── ...
```

## 修复记录文档

所有的修复记录和开发文档都在 `fixes/` 目录中，按时间顺序记录了项目的开发过程。

### 主要文档列表

#### 认证与安全
- `JWT_AUTH_FIX.md` - JWT认证实现和修复
- `SECURITY_FIX_PASSWORD_ENCRYPTION.md` - 密码加密方案
- `BACKEND_AUTH_AND_DOCS_SUMMARY.md` - 后端认证总结

#### 前端功能
- `FRONTEND_COMPLETION_SUMMARY.md` - 前端功能完成总结
- `DASHBOARD_IMPLEMENTATION.md` - 仪表盘实现
- `API_DOCS_MENU_SUMMARY.md` - API文档菜单实现
- `TIME_FILTER_UPDATE_GUIDE.md` - 时间过滤功能
- `SEARCH_FUNCTIONALITY_GUIDE.md` - 搜索功能实现
- `DROPDOWN_SELECTOR_UPDATE.md` - 下拉选择器更新

#### 后端修复
- `ERROR_HANDLING_FIX_COMPLETE.md` - 错误处理修复
- `MAIL_API_JWT_FIX.md` - 邮箱API JWT修复
- `FIX_DASHBOARD_API_ERRORS.md` - 仪表盘API错误修复

#### 用户管理
- `USER_LIST_ROLE_FIX.md` - 用户列表角色显示修复
- `PROJECT_MANAGEMENT_PAGES_SUMMARY.md` - 项目管理页面总结
- `SERVER_MAIL_MANAGEMENT_SUMMARY.md` - 服务器邮箱管理总结

#### 快速开始指南
- `QUICK_START.md` - 快速开始指南
- `QUICK_START_DASHBOARD.md` - 仪表盘快速开始
- `QUICK_START_USER_MANAGEMENT.md` - 用户管理快速开始
- `QUICK_START_ROLE_MANAGEMENT.md` - 角色管理快速开始
- `QUICK_START_API_TOKEN.md` - API Token快速开始

#### 其他
- `PROJECT_OVERVIEW.md` - 项目概览
- `CONSOLE_WARNINGS_EXPLAINED.md` - 控制台警告说明
- `需求文档.md` - 原始需求文档

## 如何使用这些文档

### 新手入门

1. 先阅读主目录的 `README.md`
2. 查看 `QUICK_START.md` 快速开始
3. 根据需要查看具体模块的快速开始指南

### 开发参考

1. 查看 `FRONTEND_COMPLETION_SUMMARY.md` 了解前端架构
2. 查看 `BACKEND_AUTH_AND_DOCS_SUMMARY.md` 了解后端架构
3. 参考具体功能的实现文档

### 问题排查

1. 查看 `ERROR_HANDLING_FIX_COMPLETE.md` 了解错误处理
2. 查看 `CONSOLE_WARNINGS_EXPLAINED.md` 了解常见警告
3. 查看具体模块的修复文档

## 文档命名规范

- `XXX_SUMMARY.md` - 功能总结文档
- `XXX_GUIDE.md` - 使用指南文档
- `XXX_FIX.md` - 问题修复文档
- `QUICK_START_XXX.md` - 快速开始文档

## 贡献文档

如果你修复了问题或添加了新功能，请：

1. 在 `fixes/` 目录创建新的Markdown文档
2. 使用清晰的文件名（遵循命名规范）
3. 包含以下内容：
   - 问题描述
   - 解决方案
   - 修改的文件
   - 测试方法
   - 相关截图（如有）

## 文档维护

- 定期整理和归档旧文档
- 更新过时的信息
- 合并重复的文档
- 保持文档结构清晰

## 相关链接

- [主README](../README.md)
- [后端README](../backend/README.md)
- [前端README](../frontend/README.md)
