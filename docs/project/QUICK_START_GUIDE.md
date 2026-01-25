# 快速开始指南

## 📋 目录

1. [项目账号加密](#项目账号加密)
2. [日志管理](#日志管理)
3. [常用命令](#常用命令)
4. [API 测试](#api-测试)
5. [故障排查](#故障排查)

---

## 🔐 项目账号加密

### 加密规则
- **加密字段**：`private_key`、`mnemonic`
- **加密方式**：AES-CBC
- **密钥**：MD5(项目名称 + "9527")
- **权限**：只有项目所属人和 ADMIN 可以解密

### 快速测试
```bash
# 测试加密功能
cd backend
python test_project_account_encryption.py

# 测试队列加密
python test_queue_encryption.py
```

### API 使用
```bash
# 创建账号（自动加密）
curl -X POST http://localhost:6080/v1/project/account \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "account": "test@example.com",
    "project_id": "uuid",
    "data": {
      "private_key": "0xabcdef...",
      "mnemonic": "word1 word2 ..."
    }
  }'

# 查询账号（根据权限自动解密）
curl -X GET http://localhost:6080/v1/project/account/{id} \
  -H "Authorization: Bearer {token}"
```

### 权限说明
| 用户类型 | 解密权限 |
|---------|---------|
| ADMIN | ✅ 所有项目 |
| 项目所属人 | ✅ 自己的项目 |
| 其他用户 | ❌ 看到密文 |

### ⚠️ 重要提醒
- **项目名称不能修改**，否则无法解密旧数据
- 现有数据不会自动加密，需要手动迁移

### 📖 详细文档
- [完整文档](PROJECT_ACCOUNT_ENCRYPTION.md)
- [快速参考](PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md)
- [流程图](PROJECT_ACCOUNT_ENCRYPTION_FLOW.md)
- [功能总结](PROJECT_ACCOUNT_FEATURES_SUMMARY.md)

---

## 📝 日志管理

### 日志配置
- **保留期限**：90天（3个月）
- **目录结构**：`名称/年/月/日`
- **自动压缩**：旧日志自动压缩为 .gz
- **自动清理**：超过90天自动删除

### 日志位置
```
backend/logs/
├── api/2026/01/25/api.log.2026-01-25_14.gz
├── app/2026/01/25/app.log.2026-01-25_14.gz
├── database/2026/01/25/database.log.2026-01-25_14.gz
└── scheduler/2026/01/25/scheduler.log.2026-01-25_14.gz
```

### 日志管理命令
```bash
# 查看日志结构
cd backend
python test_log_structure.py

# 整理旧日志（迁移到新结构）
python scripts/organize_logs.py

# 手动清理日志
python scripts/cleanup_logs.py

# 分析日志
python scripts/analyze_logs.py
```

### 📖 详细文档
- [日志系统完整文档](LOG_SYSTEM_COMPLETE.md)
- [日志快速参考](LOG_QUICK_REFERENCE.md)
- [日志管理更新](LOG_MANAGEMENT_UPDATE.md)

---

## 🚀 常用命令

### 后端服务

#### 启动服务
```bash
cd backend

# 启动主服务
python start.py

# 启动队列处理器
python start_queue_worker.py
```

#### 数据库管理
```bash
# 初始化数据库
python db/init_roles_and_admin.py

# 初始化路由权限
python db/init_routes.py

# 检查数据库表
python scripts/check_db_tables.py

# 测试数据库连接
python scripts/test_db_connection.py
```

#### 测试脚本
```bash
# 测试加密功能
python test_project_account_encryption.py

# 测试队列加密
python test_queue_encryption.py

# 测试日志结构
python test_log_structure.py

# 测试余额计算
python test_balance_calculation.py
```

### 前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

---

## 🧪 API 测试

### 获取 Token
```bash
# 登录获取 Token
curl -X POST http://localhost:6080/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "zhiyu",
    "password": "2201101122@qq.com"
  }'

# 响应
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 测试项目账号 API
```bash
# 设置 Token
TOKEN="your_token_here"

# 创建项目账号
curl -X POST http://localhost:6080/v1/project/account \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account": "test@example.com",
    "project_id": "project-uuid",
    "account_type": 2,
    "status": 1,
    "balance": 100.5,
    "data": {
      "private_key": "0xabcdef...",
      "mnemonic": "word1 word2 ..."
    }
  }'

# 查询项目账号
curl -X GET "http://localhost:6080/v1/project/account/{id}" \
  -H "Authorization: Bearer $TOKEN"

# 批量创建/更新（Redis 队列）
curl -X POST http://localhost:6080/v1/project/account/batch-upsert \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "account": "test1@example.com",
      "project_id": "project-uuid",
      "data": { ... }
    },
    {
      "account": "test2@example.com",
      "project_id": "project-uuid",
      "data": { ... }
    }
  ]'

# 统计项目账号
curl -X GET "http://localhost:6080/v1/project/account/stats?project_id=project-uuid" \
  -H "Authorization: Bearer $TOKEN"
```

### 访问 API 文档
- Swagger UI: http://localhost:6080/docs
- ReDoc: http://localhost:6080/redoc

---

## 🔧 故障排查

### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :6080

# 杀死进程
kill -9 <PID>

# 或使用脚本
cd backend/scripts
./restart_server.sh
```

### 2. 数据库连接失败
```bash
# 检查数据库配置
cat backend/.env | grep DB_

# 测试数据库连接
cd backend
python scripts/test_db_connection.py

# 检查数据库表
python scripts/check_db_tables.py
```

### 3. Redis 连接失败
```bash
# 检查 Redis 配置
cat backend/.env | grep REDIS_

# 测试 Redis 连接
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ ping

# 查看队列大小
redis-cli -h 127.0.0.1 -p 6378 -a redis_fNmAxZ llen project_account
```

### 4. 加密/解密失败
```bash
# 检查项目名称是否正确
# 项目名称不能修改，否则无法解密

# 运行测试脚本
cd backend
python test_project_account_encryption.py

# 查看错误日志
tail -f logs/app.log
```

### 5. 队列处理失败
```bash
# 检查队列处理器是否运行
ps aux | grep start_queue_worker

# 启动队列处理器
cd backend
python start_queue_worker.py

# 查看队列日志
tail -f logs/app.log | grep queue
```

### 6. 前端无法访问 API
```bash
# 检查 CORS 配置
cat backend/.env | grep CORS_ORIGINS

# 应该包含前端地址
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 重启后端服务
cd backend
python start.py
```

---

## 📚 完整文档索引

### 项目账号加密
- [PROJECT_ACCOUNT_ENCRYPTION.md](PROJECT_ACCOUNT_ENCRYPTION.md) - 详细文档
- [PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md](PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md) - 快速参考
- [PROJECT_ACCOUNT_ENCRYPTION_FLOW.md](PROJECT_ACCOUNT_ENCRYPTION_FLOW.md) - 流程图
- [PROJECT_ACCOUNT_FEATURES_SUMMARY.md](PROJECT_ACCOUNT_FEATURES_SUMMARY.md) - 功能总结

### 日志管理
- [LOG_SYSTEM_COMPLETE.md](LOG_SYSTEM_COMPLETE.md) - 完整文档
- [LOG_QUICK_REFERENCE.md](LOG_QUICK_REFERENCE.md) - 快速参考
- [LOG_MANAGEMENT_UPDATE.md](LOG_MANAGEMENT_UPDATE.md) - 更新说明
- [LOG_MANAGEMENT_SUMMARY.md](LOG_MANAGEMENT_SUMMARY.md) - 功能总结

### 项目总结
- [PROJECT_ORGANIZATION_SUMMARY.md](PROJECT_ORGANIZATION_SUMMARY.md) - 项目整理总结
- [PROJECT_ACCOUNT_STATS_FEATURE.md](PROJECT_ACCOUNT_STATS_FEATURE.md) - 统计功能
- [PROJECT_STATS_EXPORT_FEATURE.md](PROJECT_STATS_EXPORT_FEATURE.md) - 导出功能

### 其他功能
- [MAIL_SEND_MENU_FIX.md](MAIL_SEND_MENU_FIX.md) - 发送邮件菜单修复
- [MAIL_VIEWER_RENAME.md](MAIL_VIEWER_RENAME.md) - 邮件查看器重命名
- [EXPORT_FEATURE_COMPLETE.md](EXPORT_FEATURE_COMPLETE.md) - 导出功能完整文档

---

## 🎯 默认账号

### 管理员账号
- **邮箱**：`zhiyu`
- **密码**：`2201101122@qq.com`
- **角色**：ADMIN
- **权限**：全部权限

---

## 🌐 服务地址

### 开发环境
- **后端 API**：http://localhost:6080
- **前端应用**：http://localhost:5173
- **API 文档**：http://localhost:6080/docs
- **ReDoc**：http://localhost:6080/redoc

### 数据库
- **MySQL 主库**：127.0.0.1:3307
- **MySQL 从库**：127.0.0.1:3308, 127.0.0.1:3309
- **Redis**：127.0.0.1:6378

---

## ✅ 功能清单

### 已完成功能
- ✅ 项目账号敏感数据加密
- ✅ 基于权限的自动解密
- ✅ Redis 队列异步处理
- ✅ 余额自动计算
- ✅ 日志管理系统优化
- ✅ 菜单修复和优化
- ✅ 数据权限控制
- ✅ 批量操作支持
- ✅ 统计和导出功能

### 核心特性
- 🔐 AES-CBC 加密
- 🔑 每个项目独立密钥
- 👥 基于角色的权限控制
- 📊 实时统计和导出
- 📝 自动日志管理
- ⚡ Redis 队列异步处理
- 🔄 自动余额计算

---

## 📞 技术支持

如有问题，请查看：
1. 相关文档（见上方文档索引）
2. 日志文件（`backend/logs/`）
3. API 文档（http://localhost:6080/docs）

---

**最后更新**：2026-01-25
**版本**：v1.0
**状态**：✅ 完成
