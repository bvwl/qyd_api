# 项目脚本使用说明

本目录包含项目的各类脚本工具，按功能分类组织。

## 📁 目录结构

```
scripts/
├── mysql/         # MySQL相关脚本
├── test/          # 测试脚本
├── debug/         # 调试脚本
├── utils/         # 工具脚本
└── SCRIPTS_README.md  # 本文档
```

## 🗂️ 脚本分类

### MySQL脚本 (`mysql/`)

MySQL数据库管理和主从复制相关脚本。

#### 部署脚本
- `deploy_mysql_final.sh` - 完整部署MySQL主从复制
- `deploy_mysql_6cpu.sh` - 部署MySQL (6核配置)
- `deploy_mysql_shared_cpu.sh` - 部署MySQL (共享CPU)
- `deploy_mysql_single_server.sh` - 部署MySQL (单服务器)
- `deploy_mysql_step_by_step.sh` - 分步部署MySQL

#### 管理脚本
- `check_mysql_status.sh` - 检查MySQL主从状态
- `connect_mysql.sh` - 快速连接MySQL (主库/从库)
- `restart_mysql.sh` - 重启MySQL容器
- `fix_replication.sh` - 修复主从复制问题
- `cleanup_mysql.sh` - 清理MySQL环境

#### 工具脚本
- `get_master_ip.sh` - 获取主库IP地址
- `test_mysql_sync.sh` - 测试主从数据同步

**使用示例：**
```bash
# 检查MySQL状态
bash scripts/mysql/check_mysql_status.sh

# 连接主库
bash scripts/mysql/connect_mysql.sh master

# 测试主从同步
bash scripts/mysql/test_mysql_sync.sh
```

### 测试脚本 (`test/`)

API接口和功能测试脚本。

#### API测试
- `test_api_endpoints.sh` - 测试所有API接口
- `test_batch_upsert.py` - 测试批量操作接口

#### 权限测试
- `test_crud_permission.sh` - 测试CRUD权限
- `test_crud_permission_simple.sh` - 测试CRUD权限(简化版)
- `test_data_permission.sh` - 测试数据权限
- `test_data_permission_full.sh` - 测试数据权限(完整版)
- `test_delete_permission.sh` - 测试删除权限
- `test_permission_apis.sh` - 测试权限API

#### 其他测试
- `test_admin_menu.md` - 管理员菜单测试文档
- `test_frontend.html` - 前端功能测试页面

**使用示例：**
```bash
# 测试API接口
bash scripts/test/test_api_endpoints.sh

# 测试权限
bash scripts/test/test_crud_permission.sh

# 测试批量操作
python scripts/test/test_batch_upsert.py
```

### 调试脚本 (`debug/`)

问题诊断和调试工具。

- `check_api_auth.py` - 检查API认证状态
- `check_delete_permissions.py` - 检查删除权限配置
- `debug_account.py` - 调试账号问题
- `debug_check.py` - 通用调试检查

**使用示例：**
```bash
# 检查API认证
python scripts/debug/check_api_auth.py

# 检查删除权限
python scripts/debug/check_delete_permissions.py

# 调试账号
python scripts/debug/debug_account.py
```

### 工具脚本 (`utils/`)

各类辅助工具和修复脚本。

#### 认证相关
- `add_auth_ast.py` - 使用AST方式添加认证
- `add_auth_to_apis.py` - 批量添加API认证
- `batch_add_auth.py` - 批量添加认证
- `fix_auth_manual.py` - 手动修复认证

#### 权限相关
- `fix_delete_permissions.py` - 修复删除权限

#### 代码修复
- `fix_remaining_files.py` - 修复剩余文件
- `fix_role_py.py` - 修复role.py
- `fix_single_line_functions.py` - 修复单行函数

#### 功能相关
- `fix_mail_viewer_complete.sh` - 修复邮件查看器
- `install_mail_viewer_deps.sh` - 安装邮件查看器依赖

#### 服务管理
- `frontend_restart.sh` - 重启前端服务

**使用示例：**
```bash
# 批量添加API认证
python scripts/utils/add_auth_to_apis.py

# 修复删除权限
python scripts/utils/fix_delete_permissions.py

# 重启前端
bash scripts/utils/frontend_restart.sh
```

## 🚀 常用操作

### MySQL管理

```bash
# 1. 检查MySQL状态
bash scripts/mysql/check_mysql_status.sh

# 2. 连接数据库
bash scripts/mysql/connect_mysql.sh master   # 主库
bash scripts/mysql/connect_mysql.sh slave1   # 从库1
bash scripts/mysql/connect_mysql.sh slave2   # 从库2

# 3. 测试主从同步
bash scripts/mysql/test_mysql_sync.sh

# 4. 修复主从复制
bash scripts/mysql/fix_replication.sh
```

### API测试

```bash
# 1. 测试所有API接口
bash scripts/test/test_api_endpoints.sh

# 2. 测试权限功能
bash scripts/test/test_crud_permission.sh
bash scripts/test/test_delete_permission.sh

# 3. 测试批量操作
python scripts/test/test_batch_upsert.py
```

### 问题诊断

```bash
# 1. 检查API认证状态
python scripts/debug/check_api_auth.py

# 2. 检查删除权限
python scripts/debug/check_delete_permissions.py

# 3. 调试账号问题
python scripts/debug/debug_account.py
```

### 代码维护

```bash
# 1. 批量添加API认证
python scripts/utils/add_auth_to_apis.py

# 2. 修复权限配置
python scripts/utils/fix_delete_permissions.py

# 3. 重启服务
bash scripts/utils/frontend_restart.sh
```

## 📝 脚本使用规范

### Python脚本

```bash
# 进入backend目录
cd backend

# 运行脚本
python ../scripts/debug/check_api_auth.py
```

### Shell脚本

```bash
# 添加执行权限
chmod +x scripts/mysql/check_mysql_status.sh

# 运行脚本
bash scripts/mysql/check_mysql_status.sh
```

## ⚠️ 注意事项

### 权限要求
- MySQL脚本需要root权限或sudo权限
- Python脚本需要在backend目录运行
- Shell脚本需要执行权限

### 环境要求
- Python脚本需要安装项目依赖
- MySQL脚本需要Docker环境
- 确保.env配置正确

### 安全提示
- 清理脚本会删除数据，请谨慎使用
- 修复脚本会修改代码，建议先备份
- 测试脚本可能会创建测试数据

## 🔗 相关文档

### MySQL相关
- [MySQL主从复制完整文档](../docs/mysql主从.md)
- [单服务器分步部署教程](../docs/mysql主从-单服务器分步部署教程.md)
- [单服务器快速部署指南](../docs/mysql主从-单服务器快速部署.md)
- [问题总结与解决方案](../docs/mysql主从复制问题总结.md)

### 功能相关
- [Redis队列使用指南](../docs/guides/REDIS_QUEUE_GUIDE.md)
- [RBAC使用指南](../docs/guides/RBAC_README.md)
- [权限管理快速开始](../docs/guides/PERMISSION_QUICK_START.md)
- [邮件查看器快速开始](../docs/guides/MAIL_VIEWER_QUICK_START.md)

### 开发相关
- [后端开发指南](../backend/README.md)
- [前端开发指南](../frontend/README.md)
- [数据库初始化指南](../backend/db/README.md)

## 📞 问题反馈

如果遇到问题：
1. 查看脚本输出的错误信息
2. 检查环境配置是否正确
3. 查看相关文档
4. 运行调试脚本诊断问题

## 🔄 脚本维护

### 添加新脚本
1. 根据功能放到对应目录
2. 添加脚本说明注释
3. 更新本文档
4. 添加使用示例

### 脚本命名规范
- MySQL脚本：`*_mysql_*.sh`
- 测试脚本：`test_*.sh` 或 `test_*.py`
- 调试脚本：`debug_*.py` 或 `check_*.py`
- 修复脚本：`fix_*.py` 或 `fix_*.sh`
- 工具脚本：功能描述命名

### 脚本编写规范
- 添加脚本说明注释
- 添加使用示例
- 添加错误处理
- 添加参数验证
- 输出友好的提示信息

