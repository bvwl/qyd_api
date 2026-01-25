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
