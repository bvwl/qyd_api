# 脚本工具索引

项目提供的所有脚本工具说明和使用指南。

## 📋 目录

- [部署脚本](#部署脚本)
- [服务管理脚本](#服务管理脚本)
- [数据库脚本](#数据库脚本)
- [测试脚本](#测试脚本)
- [调试脚本](#调试脚本)
- [工具脚本](#工具脚本)

---

## 部署脚本

### 根目录部署脚本

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `setup_environment.sh` | 环境安装脚本 | 首次部署，安装 Python、Node.js、Redis 等 |
| `deploy_native.sh` | 本地部署脚本 | 生产环境本地部署 |
| `docker-deploy.sh` | Docker 标准部署 | Docker 容器化部署 |
| `docker-deploy-fast.sh` | Docker 快速部署 | Docker 快速部署（国内镜像加速） |
| `deploy-high-concurrency.sh` | 高并发部署 | 高并发生产环境部署 |

### 使用示例

```bash
# 环境安装
sudo bash setup_environment.sh

# 本地部署
bash deploy_native.sh

# Docker 快速部署
bash docker-deploy-fast.sh

# 高并发部署
bash deploy-high-concurrency.sh
```

---

## 服务管理脚本

### 根目录服务脚本

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `start_all_services.sh` | 启动所有服务 | 启动后端、前端、队列 Worker |
| `restart_all_services.sh` | 重启所有服务 | 更新代码后重启 |
| `restart-backend.sh` | 重启后端服务 | 后端代码更新 |
| `rebuild-backend.sh` | 重新构建后端 | 后端依赖更新 |
| `rebuild_frontend.sh` | 重新构建前端 | 前端代码更新 |
| `restart_nginx.sh` | 重启 Nginx | Nginx 配置更新 |
| `update-and-restart.sh` | 更新并重启 | 拉取代码并重启服务 |

### 使用示例

```bash
# 启动所有服务
bash start_all_services.sh

# 重启所有服务
bash restart_all_services.sh

# 重启后端
bash restart-backend.sh

# 重新构建前端
bash rebuild_frontend.sh

# 更新代码并重启
bash update-and-restart.sh
```

---

## 数据库脚本

### MySQL 管理脚本 (`scripts/mysql/`)

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `check_mysql_status.sh` | 检查 MySQL 状态 | 检查主从复制状态 |
| `connect_mysql.sh` | 连接 MySQL | 快速连接数据库 |
| `restart_mysql.sh` | 重启 MySQL | MySQL 配置更新 |
| `fix_replication.sh` | 修复主从复制 | 主从复制出错 |
| `deploy_mysql_master.sh` | 部署 MySQL 主库 | 部署主库 |
| `deploy_mysql_slave.sh` | 部署 MySQL 从库 | 部署从库 |
| `setup_replication.sh` | 配置主从复制 | 配置主从关系 |

### 后端数据库脚本 (`backend/db/`)

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `init_roles_and_admin.py` | 初始化角色和管理员 | 首次部署 |
| `init_routes.py` | 初始化路由权限 | 首次部署 |
| `init_rbac_v2.py` | 初始化 RBAC v2 | RBAC 升级 |
| `apply_*.py` | 数据库迁移脚本 | 数据库结构更新 |
| `check_*.py` | 数据检查脚本 | 数据验证 |

### 使用示例

```bash
# 检查 MySQL 状态
bash scripts/mysql/check_mysql_status.sh

# 连接 MySQL
bash scripts/mysql/connect_mysql.sh

# 修复主从复制
bash scripts/mysql/fix_replication.sh

# 初始化数据库
cd backend
python db/init_roles_and_admin.py
python db/init_routes.py
```

---

## 测试脚本

### 根目录测试脚本

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `check_database.py` | 检查数据库连接 | 验证数据库配置 |
| `diagnose_services.sh` | 诊断服务状态 | 故障排查 |
| `diagnose_frontend.sh` | 诊断前端问题 | 前端故障排查 |
| `check_and_start_frontend.sh` | 检查并启动前端 | 前端启动检查 |

### 测试脚本 (`scripts/test/`)

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `test_api_endpoints.sh` | 测试 API 接口 | API 功能测试 |
| `test_user_permission.sh` | 测试用户权限 | 权限功能测试 |
| `test_project_permission.sh` | 测试项目权限 | 项目权限测试 |
| `test_server_permission.sh` | 测试服务器权限 | 服务器权限测试 |
| `test_batch_upsert.py` | 测试批量操作 | 批量操作测试 |

### 后端测试脚本 (`backend/tests/`)

| 目录 | 说明 | 使用场景 |
|------|------|---------|
| `api/` | API 测试 | 接口功能测试 |
| `integration/` | 集成测试 | 系统集成测试 |
| `performance/` | 性能测试 | 性能压测 |
| `unit/` | 单元测试 | 单元功能测试 |

### 使用示例

```bash
# 检查数据库
python check_database.py

# 诊断服务
bash diagnose_services.sh

# 测试 API
bash scripts/test/test_api_endpoints.sh

# 测试权限
bash scripts/test/test_user_permission.sh

# 运行后端测试
cd backend
pytest
pytest tests/api/
pytest tests/performance/
```

---

## 调试脚本

### 调试脚本 (`scripts/debug/`)

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `check_api_auth.py` | 检查 API 认证 | 认证问题调试 |
| `check_delete_permissions.py` | 检查删除权限 | 权限问题调试 |
| `debug_account.py` | 调试账号问题 | 账号相关问题 |
| `debug_redis.py` | 调试 Redis 连接 | Redis 问题调试 |
| `debug_database.py` | 调试数据库连接 | 数据库问题调试 |

### 使用示例

```bash
# 检查 API 认证
python scripts/debug/check_api_auth.py

# 检查删除权限
python scripts/debug/check_delete_permissions.py

# 调试账号
python scripts/debug/debug_account.py --user-id <user_id>

# 调试 Redis
python scripts/debug/debug_redis.py

# 调试数据库
python scripts/debug/debug_database.py
```

---

## 工具脚本

### 根目录工具脚本

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `organize_all_files.sh` | 整理项目文件 | 项目文件整理 |
| `init_routes_manual.sh` | 手动初始化路由 | 路由初始化 |
| `reset_routes.sh` | 重置路由权限 | 路由权限重置 |
| `check_routes.sh` | 检查路由配置 | 路由配置检查 |
| `fix_502_error.sh` | 修复 502 错误 | Nginx 502 错误 |
| `fix_nginx_config.sh` | 修复 Nginx 配置 | Nginx 配置问题 |
| `fix_production.sh` | 修复生产环境 | 生产环境问题 |

### 工具脚本 (`scripts/utils/`)

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `backup_database.sh` | 备份数据库 | 定期备份 |
| `restore_database.sh` | 恢复数据库 | 数据恢复 |
| `cleanup_logs.sh` | 清理日志文件 | 日志清理 |
| `monitor_services.sh` | 监控服务状态 | 服务监控 |
| `generate_ssl_cert.sh` | 生成 SSL 证书 | HTTPS 配置 |

### 后端工具脚本 (`backend/scripts/`)

| 脚本 | 说明 | 使用场景 |
|------|------|---------|
| `cleanup_logs.py` | 清理日志 | 日志管理 |
| `analyze_logs.py` | 分析日志 | 日志分析 |
| `log_manager.sh` | 日志管理器 | 日志管理 |
| `organize_logs.py` | 整理日志 | 日志整理 |
| `verify_setup.py` | 验证部署 | 部署验证 |

### 使用示例

```bash
# 整理项目文件
bash organize_all_files.sh

# 重置路由
bash reset_routes.sh

# 修复 502 错误
bash fix_502_error.sh

# 备份数据库
bash scripts/utils/backup_database.sh

# 清理日志
bash scripts/utils/cleanup_logs.sh
python backend/scripts/cleanup_logs.py

# 分析日志
python backend/scripts/analyze_logs.py

# 验证部署
python backend/scripts/verify_setup.py
```

---

## 脚本开发规范

### 1. 脚本命名

- 使用小写字母和下划线
- 描述性命名，清晰表达功能
- 示例: `deploy_native.sh`, `check_database.py`

### 2. 脚本结构

```bash
#!/bin/bash

# 脚本说明
# 作者: xxx
# 日期: 2026-01-26
# 用途: xxx

# 设置错误时退出
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函数定义
function print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

function print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

function print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 主逻辑
main() {
    print_info "开始执行..."
    
    # 脚本逻辑
    
    print_info "执行完成"
}

# 执行主函数
main "$@"
```

### 3. Python 脚本结构

```python
#!/usr/bin/env python3
"""
脚本说明
作者: xxx
日期: 2026-01-26
用途: xxx
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """主函数"""
    print("开始执行...")
    
    # 脚本逻辑
    
    print("执行完成")

if __name__ == "__main__":
    main()
```

### 4. 错误处理

```bash
# Bash 脚本
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 未安装"
    exit 1
fi

# Python 脚本
try:
    # 操作
    pass
except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)
```

### 5. 日志记录

```bash
# 记录到文件
LOG_FILE="/var/log/qyd/script.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 执行操作" >> "$LOG_FILE"

# Python 日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/var/log/qyd/script.log'
)
logging.info("执行操作")
```

---

## 常用脚本组合

### 首次部署

```bash
# 1. 安装环境
sudo bash setup_environment.sh

# 2. 部署项目
bash deploy_native.sh

# 3. 初始化数据库
cd backend
python db/init_roles_and_admin.py
python db/init_routes.py

# 4. 启动服务
bash ../start_all_services.sh
```

### 代码更新

```bash
# 1. 拉取代码
git pull

# 2. 更新依赖
cd backend
source venv/bin/activate
pip install -r requirements.txt

cd ../frontend
npm install

# 3. 重新构建
npm run build

# 4. 重启服务
cd ..
bash restart_all_services.sh
```

### 故障排查

```bash
# 1. 诊断服务
bash diagnose_services.sh

# 2. 检查数据库
python check_database.py

# 3. 检查日志
tail -f backend/logs/api.log
tail -f backend/logs/app.log

# 4. 测试 API
bash scripts/test/test_api_endpoints.sh
```

### 性能测试

```bash
# 1. 运行性能测试
cd backend
pytest tests/performance/

# 2. 分析日志
python scripts/analyze_logs.py

# 3. 监控服务
bash scripts/utils/monitor_services.sh
```

---

## 相关文档

- [STARTUP_GUIDE.md](../STARTUP_GUIDE.md) - 启动指南
- [backend/scripts/README.md](../backend/scripts/README.md) - 后端脚本说明
- [backend/tests/README.md](../backend/tests/README.md) - 测试说明

---

**最后更新**: 2026-01-26  
**版本**: v1.0.0
