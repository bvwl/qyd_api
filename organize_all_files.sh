#!/bin/bash

# 项目文件整理脚本
# 将散落的测试文件、文档、脚本整理到对应目录

set -e

echo "=========================================="
echo "开始整理项目文件..."
echo "=========================================="

# 创建必要的目录
echo ""
echo "1. 创建目录结构..."

# Backend 测试目录
mkdir -p backend/tests/integration
mkdir -p backend/tests/unit
mkdir -p backend/tests/performance
mkdir -p backend/tests/api

# Backend 文档目录
mkdir -p backend/docs/deployment
mkdir -p backend/docs/migration
mkdir -p backend/docs/features

# Backend 脚本目录
mkdir -p backend/scripts/database
mkdir -p backend/scripts/xui
mkdir -p backend/scripts/test

# 根目录文档整理
mkdir -p docs/project
mkdir -p docs/archived

echo "✓ 目录结构创建完成"

# ==========================================
# 整理 Backend 测试文件
# ==========================================
echo ""
echo "2. 整理 Backend 测试文件..."

# 性能测试
if [ -f "backend/test_queue_performance.py" ]; then
  mv backend/test_queue_performance.py backend/tests/performance/
  echo "  ✓ 移动 test_queue_performance.py"
fi

if [ -f "backend/test_ultra_performance.py" ]; then
  mv backend/test_ultra_performance.py backend/tests/performance/
  echo "  ✓ 移动 test_ultra_performance.py"
fi

if [ -f "backend/test_redis_separation.py" ]; then
  mv backend/test_redis_separation.py backend/tests/performance/
  echo "  ✓ 移动 test_redis_separation.py"
fi

# API 测试
if [ -f "backend/test_permission_api.py" ]; then
  mv backend/test_permission_api.py backend/tests/api/
  echo "  ✓ 移动 test_permission_api.py"
fi

if [ -f "backend/test_account_api.sh" ]; then
  mv backend/test_account_api.sh backend/tests/api/
  echo "  ✓ 移动 test_account_api.sh"
fi

if [ -f "backend/test_api_time_query.sh" ]; then
  mv backend/test_api_time_query.sh backend/tests/api/
  echo "  ✓ 移动 test_api_time_query.sh"
fi

if [ -f "backend/test_stats_api.sh" ]; then
  mv backend/test_stats_api.sh backend/tests/api/
  echo "  ✓ 移动 test_stats_api.sh"
fi

if [ -f "backend/test_withdrawal_api.sh" ]; then
  mv backend/test_withdrawal_api.sh backend/tests/api/
  echo "  ✓ 移动 test_withdrawal_api.sh"
fi

if [ -f "backend/test_withdrawal_complete.sh" ]; then
  mv backend/test_withdrawal_complete.sh backend/tests/api/
  echo "  ✓ 移动 test_withdrawal_complete.sh"
fi

# 集成测试
if [ -f "backend/test_account_encryption_update.py" ]; then
  mv backend/test_account_encryption_update.py backend/tests/integration/
  echo "  ✓ 移动 test_account_encryption_update.py"
fi

if [ -f "backend/test_aes_encryption.py" ]; then
  mv backend/test_aes_encryption.py backend/tests/integration/
  echo "  ✓ 移动 test_aes_encryption.py"
fi

if [ -f "backend/test_balance_calculation.py" ]; then
  mv backend/test_balance_calculation.py backend/tests/integration/
  echo "  ✓ 移动 test_balance_calculation.py"
fi

if [ -f "backend/test_batch_wallet_creation.py" ]; then
  mv backend/test_batch_wallet_creation.py backend/tests/integration/
  echo "  ✓ 移动 test_batch_wallet_creation.py"
fi

if [ -f "backend/test_batch_wallet_fix.py" ]; then
  mv backend/test_batch_wallet_fix.py backend/tests/integration/
  echo "  ✓ 移动 test_batch_wallet_fix.py"
fi

if [ -f "backend/test_db_read.py" ]; then
  mv backend/test_db_read.py backend/tests/integration/
  echo "  ✓ 移动 test_db_read.py"
fi

if [ -f "backend/test_encryption_simple.py" ]; then
  mv backend/test_encryption_simple.py backend/tests/integration/
  echo "  ✓ 移动 test_encryption_simple.py"
fi

if [ -f "backend/test_export_users.py" ]; then
  mv backend/test_export_users.py backend/tests/integration/
  echo "  ✓ 移动 test_export_users.py"
fi

if [ -f "backend/test_host_binding.py" ]; then
  mv backend/test_host_binding.py backend/tests/integration/
  echo "  ✓ 移动 test_host_binding.py"
fi

if [ -f "backend/test_log_structure.py" ]; then
  mv backend/test_log_structure.py backend/tests/integration/
  echo "  ✓ 移动 test_log_structure.py"
fi

if [ -f "backend/test_project_account_encryption.py" ]; then
  mv backend/test_project_account_encryption.py backend/tests/integration/
  echo "  ✓ 移动 test_project_account_encryption.py"
fi

if [ -f "backend/test_project_stats.py" ]; then
  mv backend/test_project_stats.py backend/tests/integration/
  echo "  ✓ 移动 test_project_stats.py"
fi

if [ -f "backend/test_project_withdrawal.py" ]; then
  mv backend/test_project_withdrawal.py backend/tests/integration/
  echo "  ✓ 移动 test_project_withdrawal.py"
fi

if [ -f "backend/test_proxy_check.py" ]; then
  mv backend/test_proxy_check.py backend/tests/integration/
  echo "  ✓ 移动 test_proxy_check.py"
fi

if [ -f "backend/test_proxy_type_fix.py" ]; then
  mv backend/test_proxy_type_fix.py backend/tests/integration/
  echo "  ✓ 移动 test_proxy_type_fix.py"
fi

if [ -f "backend/test_queue_encryption.py" ]; then
  mv backend/test_queue_encryption.py backend/tests/integration/
  echo "  ✓ 移动 test_queue_encryption.py"
fi

if [ -f "backend/test_security_log.py" ]; then
  mv backend/test_security_log.py backend/tests/integration/
  echo "  ✓ 移动 test_security_log.py"
fi

if [ -f "backend/test_time_parameter_fix.py" ]; then
  mv backend/test_time_parameter_fix.py backend/tests/integration/
  echo "  ✓ 移动 test_time_parameter_fix.py"
fi

if [ -f "backend/test_token_invalidation.py" ]; then
  mv backend/test_token_invalidation.py backend/tests/integration/
  echo "  ✓ 移动 test_token_invalidation.py"
fi

if [ -f "backend/test_upsert_fix.py" ]; then
  mv backend/test_upsert_fix.py backend/tests/integration/
  echo "  ✓ 移动 test_upsert_fix.py"
fi

if [ -f "backend/test_wallet_encryption.py" ]; then
  mv backend/test_wallet_encryption.py backend/tests/integration/
  echo "  ✓ 移动 test_wallet_encryption.py"
fi

# XUI 测试
if [ -f "backend/test_xui_account_404.py" ]; then
  mv backend/test_xui_account_404.py backend/tests/integration/
  echo "  ✓ 移动 test_xui_account_404.py"
fi

if [ -f "backend/test_xui_migration.py" ]; then
  mv backend/test_xui_migration.py backend/tests/integration/
  echo "  ✓ 移动 test_xui_migration.py"
fi

if [ -f "backend/test_xui_operation_log.py" ]; then
  mv backend/test_xui_operation_log.py backend/tests/integration/
  echo "  ✓ 移动 test_xui_operation_log.py"
fi

if [ -f "backend/test_xui_routes.py" ]; then
  mv backend/test_xui_routes.py backend/tests/integration/
  echo "  ✓ 移动 test_xui_routes.py"
fi

if [ -f "backend/test_xui_status_fix.py" ]; then
  mv backend/test_xui_status_fix.py backend/tests/integration/
  echo "  ✓ 移动 test_xui_status_fix.py"
fi

if [ -f "backend/test_xui_status_update.py" ]; then
  mv backend/test_xui_status_update.py backend/tests/integration/
  echo "  ✓ 移动 test_xui_status_update.py"
fi

if [ -f "backend/test_xui_sync.py" ]; then
  mv backend/test_xui_sync.py backend/tests/integration/
  echo "  ✓ 移动 test_xui_sync.py"
fi

echo "✓ Backend 测试文件整理完成"

# ==========================================
# 整理 Backend 文档
# ==========================================
echo ""
echo "3. 整理 Backend 文档..."

if [ -f "backend/API_TOKEN_INVALIDATION.md" ]; then
  mv backend/API_TOKEN_INVALIDATION.md backend/docs/features/
  echo "  ✓ 移动 API_TOKEN_INVALIDATION.md"
fi

if [ -f "backend/RBAC_IMPLEMENTATION_SUMMARY.md" ]; then
  mv backend/RBAC_IMPLEMENTATION_SUMMARY.md backend/docs/features/
  echo "  ✓ 移动 RBAC_IMPLEMENTATION_SUMMARY.md"
fi

if [ -f "backend/TIME_PARAMETER_QUICK_FIX.md" ]; then
  mv backend/TIME_PARAMETER_QUICK_FIX.md backend/docs/features/
  echo "  ✓ 移动 TIME_PARAMETER_QUICK_FIX.md"
fi

if [ -f "backend/DEPLOY_READ_WRITE_SPLIT.md" ]; then
  mv backend/DEPLOY_READ_WRITE_SPLIT.md backend/docs/deployment/
  echo "  ✓ 移动 DEPLOY_READ_WRITE_SPLIT.md"
fi

if [ -f "backend/READ_WRITE_SPLIT_GUIDE.md" ]; then
  mv backend/READ_WRITE_SPLIT_GUIDE.md backend/docs/deployment/
  echo "  ✓ 移动 READ_WRITE_SPLIT_GUIDE.md"
fi

if [ -f "backend/CREATE_XUI_TABLES.md" ]; then
  mv backend/CREATE_XUI_TABLES.md backend/docs/migration/
  echo "  ✓ 移动 CREATE_XUI_TABLES.md"
fi

if [ -f "backend/XUI_CREATE_TABLES_FINAL.md" ]; then
  mv backend/XUI_CREATE_TABLES_FINAL.md backend/docs/migration/
  echo "  ✓ 移动 XUI_CREATE_TABLES_FINAL.md"
fi

if [ -f "backend/XUI_MANUAL_MIGRATION.md" ]; then
  mv backend/XUI_MANUAL_MIGRATION.md backend/docs/migration/
  echo "  ✓ 移动 XUI_MANUAL_MIGRATION.md"
fi

if [ -f "backend/XUI_MIGRATION_GUIDE.md" ]; then
  mv backend/XUI_MIGRATION_GUIDE.md backend/docs/migration/
  echo "  ✓ 移动 XUI_MIGRATION_GUIDE.md"
fi

if [ -f "backend/XUI_MIGRATION_QUICK_START.md" ]; then
  mv backend/XUI_MIGRATION_QUICK_START.md backend/docs/migration/
  echo "  ✓ 移动 XUI_MIGRATION_QUICK_START.md"
fi

echo "✓ Backend 文档整理完成"

# ==========================================
# 整理 Backend 脚本
# ==========================================
echo ""
echo "4. 整理 Backend 脚本..."

# 数据库脚本
if [ -f "backend/check_password_encryption.py" ]; then
  mv backend/check_password_encryption.py backend/scripts/database/
  echo "  ✓ 移动 check_password_encryption.py"
fi

if [ -f "backend/check_password_in_db.py" ]; then
  mv backend/check_password_in_db.py backend/scripts/database/
  echo "  ✓ 移动 check_password_in_db.py"
fi

if [ -f "backend/check_users_table.py" ]; then
  mv backend/check_users_table.py backend/scripts/database/
  echo "  ✓ 移动 check_users_table.py"
fi

if [ -f "backend/create_stats_table.py" ]; then
  mv backend/create_stats_table.py backend/scripts/database/
  echo "  ✓ 移动 create_stats_table.py"
fi

if [ -f "backend/init_project_stats.py" ]; then
  mv backend/init_project_stats.py backend/scripts/database/
  echo "  ✓ 移动 init_project_stats.py"
fi

if [ -f "backend/fix_time_parameter_issue.py" ]; then
  mv backend/fix_time_parameter_issue.py backend/scripts/database/
  echo "  ✓ 移动 fix_time_parameter_issue.py"
fi

if [ -f "backend/verify_route.sql" ]; then
  mv backend/verify_route.sql backend/scripts/database/
  echo "  ✓ 移动 verify_route.sql"
fi

if [ -f "backend/verify_wallet_batch_route.py" ]; then
  mv backend/verify_wallet_batch_route.py backend/scripts/database/
  echo "  ✓ 移动 verify_wallet_batch_route.py"
fi

# XUI 脚本
if [ -f "backend/add_xui_log_route.sh" ]; then
  mv backend/add_xui_log_route.sh backend/scripts/xui/
  echo "  ✓ 移动 add_xui_log_route.sh"
fi

if [ -f "backend/add_xui_routes.sh" ]; then
  mv backend/add_xui_routes.sh backend/scripts/xui/
  echo "  ✓ 移动 add_xui_routes.sh"
fi

if [ -f "backend/check_xui_log_table.py" ]; then
  mv backend/check_xui_log_table.py backend/scripts/xui/
  echo "  ✓ 移动 check_xui_log_table.py"
fi

if [ -f "backend/check_xui_log_table_simple.py" ]; then
  mv backend/check_xui_log_table_simple.py backend/scripts/xui/
  echo "  ✓ 移动 check_xui_log_table_simple.py"
fi

if [ -f "backend/check_xui_tables.py" ]; then
  mv backend/check_xui_tables.py backend/scripts/xui/
  echo "  ✓ 移动 check_xui_tables.py"
fi

if [ -f "backend/create_xui_tables.sh" ]; then
  mv backend/create_xui_tables.sh backend/scripts/xui/
  echo "  ✓ 移动 create_xui_tables.sh"
fi

if [ -f "backend/create_xui_tables_simple.sh" ]; then
  mv backend/create_xui_tables_simple.sh backend/scripts/xui/
  echo "  ✓ 移动 create_xui_tables_simple.sh"
fi

if [ -f "backend/migrate_xui.sh" ]; then
  mv backend/migrate_xui.sh backend/scripts/xui/
  echo "  ✓ 移动 migrate_xui.sh"
fi

# 示例文件
if [ -f "backend/example_batch_wallet_api.py" ]; then
  mv backend/example_batch_wallet_api.py backend/examples/
  echo "  ✓ 移动 example_batch_wallet_api.py"
fi

echo "✓ Backend 脚本整理完成"

# ==========================================
# 整理根目录文档
# ==========================================
echo ""
echo "5. 整理根目录文档..."

if [ -f "CLIENTS_FOLDER_CLEANUP.md" ]; then
  mv CLIENTS_FOLDER_CLEANUP.md docs/archived/
  echo "  ✓ 移动 CLIENTS_FOLDER_CLEANUP.md"
fi

if [ -f "COMPLETE_CLEANUP_SUMMARY.md" ]; then
  mv COMPLETE_CLEANUP_SUMMARY.md docs/archived/
  echo "  ✓ 移动 COMPLETE_CLEANUP_SUMMARY.md"
fi

if [ -f "FILE_ORGANIZATION_SUMMARY.md" ]; then
  mv FILE_ORGANIZATION_SUMMARY.md docs/archived/
  echo "  ✓ 移动 FILE_ORGANIZATION_SUMMARY.md"
fi

if [ -f "QUICK_START_GUIDE.md" ]; then
  mv QUICK_START_GUIDE.md docs/project/
  echo "  ✓ 移动 QUICK_START_GUIDE.md"
fi

# 整理脚本
if [ -f "organize_backend_docs.sh" ]; then
  mv organize_backend_docs.sh scripts/utils/
  echo "  ✓ 移动 organize_backend_docs.sh"
fi

if [ -f "organize_clients_folder.sh" ]; then
  mv organize_clients_folder.sh scripts/utils/
  echo "  ✓ 移动 organize_clients_folder.sh"
fi

if [ -f "organize_project_files.sh" ]; then
  mv organize_project_files.sh scripts/utils/
  echo "  ✓ 移动 organize_project_files.sh"
fi

echo "✓ 根目录文档整理完成"

# ==========================================
# 创建测试索引文件
# ==========================================
echo ""
echo "6. 创建索引文件..."

cat > backend/tests/README.md << 'EOF'
# 测试文件说明

## 目录结构

```
tests/
├── api/              # API 接口测试
├── integration/      # 集成测试
├── performance/      # 性能测试
├── unit/            # 单元测试（原有）
└── README.md        # 本文件
```

## API 测试 (api/)

测试各个 API 端点的功能：
- `test_account_api.sh` - 账户 API 测试
- `test_api_time_query.sh` - 时间查询 API 测试
- `test_permission_api.py` - 权限 API 测试
- `test_stats_api.sh` - 统计 API 测试
- `test_withdrawal_api.sh` - 提现 API 测试
- `test_withdrawal_complete.sh` - 完整提现流程测试

## 集成测试 (integration/)

测试多个模块协同工作：

### 加密相关
- `test_aes_encryption.py` - AES 加密测试
- `test_encryption_simple.py` - 简单加密测试
- `test_account_encryption_update.py` - 账户加密更新测试
- `test_project_account_encryption.py` - 项目账户加密测试
- `test_wallet_encryption.py` - 钱包加密测试
- `test_queue_encryption.py` - 队列加密测试

### 业务功能
- `test_balance_calculation.py` - 余额计算测试
- `test_batch_wallet_creation.py` - 批量创建钱包测试
- `test_batch_wallet_fix.py` - 批量钱包修复测试
- `test_project_stats.py` - 项目统计测试
- `test_project_withdrawal.py` - 项目提现测试
- `test_export_users.py` - 用户导出测试

### 系统功能
- `test_db_read.py` - 数据库读取测试
- `test_host_binding.py` - 主机绑定测试
- `test_log_structure.py` - 日志结构测试
- `test_security_log.py` - 安全日志测试
- `test_token_invalidation.py` - Token 失效测试
- `test_time_parameter_fix.py` - 时间参数修复测试
- `test_upsert_fix.py` - Upsert 修复测试

### 代理相关
- `test_proxy_check.py` - 代理检查测试
- `test_proxy_type_fix.py` - 代理类型修复测试

### XUI 相关
- `test_xui_account_404.py` - XUI 账户 404 测试
- `test_xui_migration.py` - XUI 迁移测试
- `test_xui_operation_log.py` - XUI 操作日志测试
- `test_xui_routes.py` - XUI 路由测试
- `test_xui_status_fix.py` - XUI 状态修复测试
- `test_xui_status_update.py` - XUI 状态更新测试
- `test_xui_sync.py` - XUI 同步测试

## 性能测试 (performance/)

测试系统性能和负载：
- `test_queue_performance.py` - 队列性能测试
- `test_ultra_performance.py` - 超高性能测试
- `test_redis_separation.py` - Redis 分离性能测试

## 单元测试 (unit/)

原有的单元测试文件。

## 运行测试

### 运行所有测试
```bash
cd backend
pytest
```

### 运行特定类型的测试
```bash
# API 测试
pytest tests/api/

# 集成测试
pytest tests/integration/

# 性能测试
pytest tests/performance/

# 单元测试
pytest tests/unit/
```

### 运行单个测试文件
```bash
pytest tests/integration/test_wallet_encryption.py
```

### 运行 Shell 脚本测试
```bash
bash tests/api/test_account_api.sh
```

## 注意事项

1. 运行测试前确保已安装依赖：`pip install -r requirements.txt`
2. 确保测试数据库已配置
3. 某些测试需要 Redis 服务运行
4. 性能测试可能需要较长时间
EOF

echo "  ✓ 创建 backend/tests/README.md"

cat > backend/scripts/README.md << 'EOF'
# 脚本文件说明

## 目录结构

```
scripts/
├── database/        # 数据库相关脚本
├── xui/            # XUI 相关脚本
├── test/           # 测试脚本（原有）
├── debug/          # 调试脚本（原有）
├── utils/          # 工具脚本（原有）
└── README.md       # 本文件
```

## 数据库脚本 (database/)

### 检查脚本
- `check_password_encryption.py` - 检查密码加密
- `check_password_in_db.py` - 检查数据库中的密码
- `check_users_table.py` - 检查用户表

### 初始化脚本
- `create_stats_table.py` - 创建统计表
- `init_project_stats.py` - 初始化项目统计

### 修复脚本
- `fix_time_parameter_issue.py` - 修复时间参数问题

### 验证脚本
- `verify_route.sql` - 验证路由 SQL
- `verify_wallet_batch_route.py` - 验证钱包批量路由

## XUI 脚本 (xui/)

### 路由管理
- `add_xui_log_route.sh` - 添加 XUI 日志路由
- `add_xui_routes.sh` - 添加 XUI 路由

### 表管理
- `check_xui_log_table.py` - 检查 XUI 日志表
- `check_xui_log_table_simple.py` - 简单检查 XUI 日志表
- `check_xui_tables.py` - 检查 XUI 表
- `create_xui_tables.sh` - 创建 XUI 表
- `create_xui_tables_simple.sh` - 简单创建 XUI 表

### 迁移
- `migrate_xui.sh` - XUI 迁移脚本

## 使用说明

### 数据库脚本

```bash
# 检查密码加密
python backend/scripts/database/check_password_encryption.py

# 初始化项目统计
python backend/scripts/database/init_project_stats.py

# 修复时间参数问题
python backend/scripts/database/fix_time_parameter_issue.py
```

### XUI 脚本

```bash
# 创建 XUI 表
bash backend/scripts/xui/create_xui_tables.sh

# 添加 XUI 路由
bash backend/scripts/xui/add_xui_routes.sh

# XUI 迁移
bash backend/scripts/xui/migrate_xui.sh
```

## 注意事项

1. 运行脚本前请备份数据库
2. 确保已配置正确的数据库连接
3. 某些脚本需要管理员权限
4. 建议先在测试环境运行
EOF

echo "  ✓ 创建 backend/scripts/README.md"

cat > backend/docs/README.md << 'EOF'
# Backend 文档

## 目录结构

```
docs/
├── deployment/      # 部署相关文档
├── migration/       # 数据迁移文档
├── features/        # 功能特性文档
└── README.md       # 本文件
```

## 部署文档 (deployment/)

- `DEPLOY_READ_WRITE_SPLIT.md` - 读写分离部署指南
- `READ_WRITE_SPLIT_GUIDE.md` - 读写分离使用指南

## 迁移文档 (migration/)

### XUI 迁移
- `CREATE_XUI_TABLES.md` - 创建 XUI 表
- `XUI_CREATE_TABLES_FINAL.md` - XUI 表创建最终版
- `XUI_MANUAL_MIGRATION.md` - XUI 手动迁移
- `XUI_MIGRATION_GUIDE.md` - XUI 迁移指南
- `XUI_MIGRATION_QUICK_START.md` - XUI 迁移快速开始

## 功能文档 (features/)

- `API_TOKEN_INVALIDATION.md` - API Token 失效机制
- `RBAC_IMPLEMENTATION_SUMMARY.md` - RBAC 实现总结
- `TIME_PARAMETER_QUICK_FIX.md` - 时间参数快速修复

## 相关文档

更多文档请查看项目根目录的 `docs/` 文件夹。
EOF

echo "  ✓ 创建 backend/docs/README.md"

# ==========================================
# 完成
# ==========================================
echo ""
echo "=========================================="
echo "文件整理完成！"
echo "=========================================="
echo ""
echo "整理后的目录结构："
echo ""
echo "backend/"
echo "├── tests/"
echo "│   ├── api/              # API 测试"
echo "│   ├── integration/      # 集成测试"
echo "│   ├── performance/      # 性能测试"
echo "│   └── unit/            # 单元测试"
echo "├── scripts/"
echo "│   ├── database/        # 数据库脚本"
echo "│   ├── xui/            # XUI 脚本"
echo "│   └── test/           # 测试脚本"
echo "├── docs/"
echo "│   ├── deployment/      # 部署文档"
echo "│   ├── migration/       # 迁移文档"
echo "│   └── features/        # 功能文档"
echo "└── examples/           # 示例代码"
echo ""
echo "docs/"
echo "├── project/            # 项目文档"
echo "└── archived/           # 归档文档"
echo ""
echo "scripts/"
echo "└── utils/              # 工具脚本"
echo ""
echo "请查看各目录下的 README.md 了解详细信息"
