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
