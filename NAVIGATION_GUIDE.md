# QYD 项目导航指南

快速找到你需要的文档和资源。

## 🎯 我想...

### 快速开始

| 我想... | 推荐文档 | 时间 |
|---------|---------|------|
| 快速体验项目 | [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) | 5 分钟 |
| 本地开发调试 | [STARTUP_GUIDE.md](STARTUP_GUIDE.md) → 场景 1 | 10 分钟 |
| 部署到生产环境 | [QUICK_START.md](QUICK_START.md) | 15 分钟 |
| 部署高并发环境 | [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md) | 30 分钟 |

### 开发相关

| 我想... | 推荐文档 | 说明 |
|---------|---------|------|
| 了解项目结构 | [.kiro/steering/structure.md](.kiro/steering/structure.md) | 项目组织结构 |
| 学习开发规范 | [.kiro/steering/conventions.md](.kiro/steering/conventions.md) | 必读！⭐⭐⭐⭐⭐ |
| 开发后端功能 | [backend/README.md](backend/README.md) | 后端开发指南 |
| 开发前端功能 | [frontend/README.md](frontend/README.md) | 前端开发指南 |
| 了解技术栈 | [.kiro/steering/tech.md](.kiro/steering/tech.md) | 技术栈说明 |

### 运维相关

| 我想... | 推荐文档 | 说明 |
|---------|---------|------|
| 查找常用命令 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | 速查表⭐⭐⭐⭐⭐ |
| 管理服务 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 服务管理 | Systemd/Docker |
| 查看日志 | [docs/logs/LOG_QUICK_REFERENCE.md](docs/logs/LOG_QUICK_REFERENCE.md) | 日志管理 |
| 性能优化 | [docs/performance/PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md) | 性能配置 |
| 备份数据 | [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) → 工具脚本 | 备份脚本 |

### 故障排查

| 我想... | 推荐文档 | 说明 |
|---------|---------|------|
| 诊断问题 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 故障排查 | 常见问题 |
| 修复端口占用 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 快速修复 | 端口问题 |
| 修复数据库连接 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 快速修复 | 数据库问题 |
| 修复 Redis 连接 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 快速修复 | Redis 问题 |
| 查看详细故障排查 | [docs/fixes/TROUBLESHOOTING.md](docs/fixes/TROUBLESHOOTING.md) | 完整指南 |

### 功能相关

| 我想... | 推荐文档 | 说明 |
|---------|---------|------|
| 了解加密功能 | [docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md) | 加密快速参考 |
| 了解权限系统 | [docs/rbac/QUICK_START.md](docs/rbac/QUICK_START.md) | RBAC 快速开始 |
| 了解日志系统 | [docs/logs/LOG_QUICK_REFERENCE.md](docs/logs/LOG_QUICK_REFERENCE.md) | 日志快速参考 |
| 了解导出功能 | [docs/export/QUICK_REFERENCE_EXPORT.md](docs/export/QUICK_REFERENCE_EXPORT.md) | 导出快速参考 |
| 了解邮件功能 | [docs/guides/MAIL_VIEWER_QUICK_START.md](docs/guides/MAIL_VIEWER_QUICK_START.md) | 邮件查看器 |

### 测试相关

| 我想... | 推荐文档 | 说明 |
|---------|---------|------|
| 运行测试 | [backend/tests/README.md](backend/tests/README.md) | 测试说明 |
| 测试 API | [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) → 测试脚本 | API 测试 |
| 性能测试 | [backend/tests/performance/](backend/tests/performance/) | 性能测试 |
| 压力测试 | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 测试命令 | 压测命令 |

---

## 📚 按角色导航

### 新手用户

**第一步**: 了解项目
- [README.md](README.md) - 项目总览

**第二步**: 快速体验
- [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Docker 快速部署

**第三步**: 学习使用
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 常用命令
- [docs/DOCUMENTATION_COMPLETE_INDEX.md](docs/DOCUMENTATION_COMPLETE_INDEX.md) - 文档索引

### 后端开发者

**必读文档**:
1. [backend/README.md](backend/README.md) - 后端开发指南
2. [.kiro/steering/conventions.md](.kiro/steering/conventions.md) - 开发规范
3. [.kiro/steering/structure.md](.kiro/steering/structure.md) - 项目结构

**常用文档**:
- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) → 场景 5 - 仅启动后端
- [backend/tests/README.md](backend/tests/README.md) - 测试说明
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考

**深入学习**:
- [docs/rbac/PRACTICAL_RBAC_DESIGN.md](docs/rbac/PRACTICAL_RBAC_DESIGN.md) - RBAC 设计
- [docs/encryption/PROJECT_ACCOUNT_ENCRYPTION.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION.md) - 加密实现
- [docs/performance/SCALE_TO_10K_GUIDE.md](docs/performance/SCALE_TO_10K_GUIDE.md) - 性能优化

### 前端开发者

**必读文档**:
1. [frontend/README.md](frontend/README.md) - 前端开发指南
2. [.kiro/steering/conventions.md](.kiro/steering/conventions.md) - 开发规范
3. [.kiro/steering/structure.md](.kiro/steering/structure.md) - 项目结构

**常用文档**:
- [STARTUP_GUIDE.md](STARTUP_GUIDE.md) → 场景 6 - 仅启动前端
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考

**深入学习**:
- [docs/features/frontend/](docs/features/frontend/) - 前端功能文档
- [docs/rbac/QUICK_START.md](docs/rbac/QUICK_START.md) - 权限使用

### 运维工程师

**必读文档**:
1. [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 启动指南
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考
3. [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) - 脚本索引

**部署文档**:
- [QUICK_START.md](QUICK_START.md) - 本地快速部署
- [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Docker 快速部署
- [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md) - 高并发部署

**运维文档**:
- [docs/logs/LOG_QUICK_REFERENCE.md](docs/logs/LOG_QUICK_REFERENCE.md) - 日志管理
- [docs/performance/PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md) - 性能配置
- [docs/fixes/TROUBLESHOOTING.md](docs/fixes/TROUBLESHOOTING.md) - 故障排查

### 架构师

**必读文档**:
1. [README.md](README.md) - 项目总览
2. [.kiro/steering/structure.md](.kiro/steering/structure.md) - 项目结构
3. [docs/deployment/DEPLOYMENT_ARCHITECTURE.md](docs/deployment/DEPLOYMENT_ARCHITECTURE.md) - 部署架构

**设计文档**:
- [docs/rbac/ENTERPRISE_RBAC_DESIGN.md](docs/rbac/ENTERPRISE_RBAC_DESIGN.md) - 企业级 RBAC
- [docs/rbac/MODERN_RBAC_DESIGN.md](docs/rbac/MODERN_RBAC_DESIGN.md) - 现代 RBAC
- [docs/encryption/PROJECT_ACCOUNT_ENCRYPTION.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION.md) - 加密设计

**性能文档**:
- [docs/performance/SCALE_TO_10K_GUIDE.md](docs/performance/SCALE_TO_10K_GUIDE.md) - 扩展到 10000+ QPS
- [docs/performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md](docs/performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md) - 超高性能
- [docs/infrastructure/](docs/infrastructure/) - 基础设施文档

---

## 🔍 按主题导航

### 部署相关

**快速开始**:
- [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Docker 快速部署 ⭐⭐⭐⭐⭐
- [QUICK_START.md](QUICK_START.md) - 本地快速部署 ⭐⭐⭐⭐

**详细指南**:
- [NATIVE_DEPLOYMENT.md](NATIVE_DEPLOYMENT.md) - 本地详细部署
- [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md) - 高并发部署
- [docs/deployment/](docs/deployment/) - 部署文档目录

### 性能优化

**快速参考**:
- [docs/performance/PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md) ⭐⭐⭐⭐⭐

**详细指南**:
- [docs/performance/SCALE_TO_10K_GUIDE.md](docs/performance/SCALE_TO_10K_GUIDE.md) - 10000+ QPS
- [docs/performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md](docs/performance/ULTRA_HIGH_PERFORMANCE_GUIDE.md) - 超高性能
- [docs/performance/REDIS_QUEUE_SEPARATION_GUIDE.md](docs/performance/REDIS_QUEUE_SEPARATION_GUIDE.md) - 队列分离

### 安全与加密

**快速参考**:
- [docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_QUICK_REF.md) ⭐⭐⭐⭐⭐

**详细文档**:
- [docs/encryption/PROJECT_ACCOUNT_ENCRYPTION.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION.md) - 加密详细文档
- [docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_FLOW.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION_FLOW.md) - 加密流程
- [docs/fixes/SECURITY_FIX_PASSWORD_ENCRYPTION.md](docs/fixes/SECURITY_FIX_PASSWORD_ENCRYPTION.md) - 密码加密

### 权限系统

**快速开始**:
- [docs/rbac/QUICK_START.md](docs/rbac/QUICK_START.md) ⭐⭐⭐⭐⭐
- [docs/guides/PERMISSION_QUICK_START.md](docs/guides/PERMISSION_QUICK_START.md)

**设计文档**:
- [docs/rbac/PRACTICAL_RBAC_DESIGN.md](docs/rbac/PRACTICAL_RBAC_DESIGN.md) - 实用设计
- [docs/rbac/MODERN_RBAC_DESIGN.md](docs/rbac/MODERN_RBAC_DESIGN.md) - 现代设计
- [docs/rbac/ENTERPRISE_RBAC_DESIGN.md](docs/rbac/ENTERPRISE_RBAC_DESIGN.md) - 企业级设计

**使用指南**:
- [docs/guides/PERMISSION_MANAGE_GUIDE.md](docs/guides/PERMISSION_MANAGE_GUIDE.md) - 权限管理
- [docs/guides/MENU_BINDING_GUIDE.md](docs/guides/MENU_BINDING_GUIDE.md) - 菜单绑定

### 日志管理

**快速参考**:
- [docs/logs/LOG_QUICK_REFERENCE.md](docs/logs/LOG_QUICK_REFERENCE.md) ⭐⭐⭐⭐⭐

**详细文档**:
- [docs/logs/LOG_SYSTEM_COMPLETE.md](docs/logs/LOG_SYSTEM_COMPLETE.md) - 日志系统完整文档
- [docs/logs/LOG_MANAGEMENT_UPDATE.md](docs/logs/LOG_MANAGEMENT_UPDATE.md) - 日志管理更新

---

## 🛠️ 按任务导航

### 首次部署

1. 选择部署方式
   - Docker: [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)
   - 本地: [QUICK_START.md](QUICK_START.md)

2. 配置环境变量
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 环境变量

3. 初始化数据库
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 数据库操作

4. 启动服务
   - [STARTUP_GUIDE.md](STARTUP_GUIDE.md)

5. 验证部署
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 测试命令

### 代码更新

1. 拉取代码
   ```bash
   git pull
   ```

2. 更新依赖
   - 后端: [backend/README.md](backend/README.md)
   - 前端: [frontend/README.md](frontend/README.md)

3. 重启服务
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 服务管理

4. 验证更新
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 测试命令

### 性能调优

1. 了解当前性能
   - [docs/performance/PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md)

2. 选择配置方案
   - 标准: 2700 条/秒
   - 高性能: 6000 条/秒
   - 超高性能: 12000 条/秒

3. 应用配置
   - [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md)

4. 性能测试
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 测试命令

5. 监控和调整
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 资源监控

### 故障排查

1. 诊断问题
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 故障排查

2. 查看日志
   - [docs/logs/LOG_QUICK_REFERENCE.md](docs/logs/LOG_QUICK_REFERENCE.md)

3. 使用调试脚本
   - [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) → 调试脚本

4. 查找解决方案
   - [docs/fixes/TROUBLESHOOTING.md](docs/fixes/TROUBLESHOOTING.md)

5. 应用修复
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 快速修复

---

## 📖 文档类型说明

### 快速开始类

**特点**: 简洁明了，快速上手  
**适合**: 新手用户、快速体验

**示例**:
- [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)
- [QUICK_START.md](QUICK_START.md)

### 详细指南类

**特点**: 完整详细，深入讲解  
**适合**: 深入学习、生产部署

**示例**:
- [NATIVE_DEPLOYMENT.md](NATIVE_DEPLOYMENT.md)
- [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md)

### 快速参考类

**特点**: 速查表格，命令列表  
**适合**: 日常使用、快速查找

**示例**:
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- [docs/performance/PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md)

### 故障排查类

**特点**: 问题诊断，解决方案  
**适合**: 遇到问题、需要修复

**示例**:
- [docs/fixes/TROUBLESHOOTING.md](docs/fixes/TROUBLESHOOTING.md)
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) → 故障排查

---

## 🎯 推荐学习路径

### 路径 1: 快速上手（1 小时）

1. [README.md](README.md) - 了解项目（10 分钟）
2. [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - 快速部署（20 分钟）
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 学习常用命令（30 分钟）

### 路径 2: 开发入门（4 小时）

1. [README.md](README.md) - 了解项目（10 分钟）
2. [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 开发环境（30 分钟）
3. [.kiro/steering/conventions.md](.kiro/steering/conventions.md) - 开发规范（1 小时）
4. [backend/README.md](backend/README.md) - 后端开发（1 小时）
5. [frontend/README.md](frontend/README.md) - 前端开发（1 小时）
6. 实践开发（30 分钟）

### 路径 3: 运维精通（8 小时）

1. [README.md](README.md) - 了解项目（10 分钟）
2. [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 所有场景（1 小时）
3. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 常用命令（1 小时）
4. [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md) - 高并发部署（2 小时）
5. [docs/performance/SCALE_TO_10K_GUIDE.md](docs/performance/SCALE_TO_10K_GUIDE.md) - 性能优化（2 小时）
6. [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) - 脚本工具（1 小时）
7. 实践部署（1 小时）

### 路径 4: 架构深入（16 小时）

1. [README.md](README.md) - 了解项目（10 分钟）
2. [.kiro/steering/structure.md](.kiro/steering/structure.md) - 项目结构（1 小时）
3. [docs/deployment/DEPLOYMENT_ARCHITECTURE.md](docs/deployment/DEPLOYMENT_ARCHITECTURE.md) - 部署架构（2 小时）
4. [docs/rbac/ENTERPRISE_RBAC_DESIGN.md](docs/rbac/ENTERPRISE_RBAC_DESIGN.md) - RBAC 设计（3 小时）
5. [docs/encryption/PROJECT_ACCOUNT_ENCRYPTION.md](docs/encryption/PROJECT_ACCOUNT_ENCRYPTION.md) - 加密设计（2 小时）
6. [docs/performance/SCALE_TO_10K_GUIDE.md](docs/performance/SCALE_TO_10K_GUIDE.md) - 性能优化（3 小时）
7. [docs/DOCUMENTATION_COMPLETE_INDEX.md](docs/DOCUMENTATION_COMPLETE_INDEX.md) - 浏览所有文档（4 小时）
8. 实践和总结（1 小时）

---

## 🔗 快速链接

### 最常用文档（Top 10）

1. [STARTUP_GUIDE.md](STARTUP_GUIDE.md) - 启动指南
2. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考
3. [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) - Docker 快速部署
4. [.kiro/steering/conventions.md](.kiro/steering/conventions.md) - 开发规范
5. [backend/README.md](backend/README.md) - 后端开发
6. [frontend/README.md](frontend/README.md) - 前端开发
7. [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) - 脚本索引
8. [docs/performance/PERFORMANCE_QUICK_REFERENCE.md](docs/performance/PERFORMANCE_QUICK_REFERENCE.md) - 性能参考
9. [docs/logs/LOG_QUICK_REFERENCE.md](docs/logs/LOG_QUICK_REFERENCE.md) - 日志参考
10. [docs/DOCUMENTATION_COMPLETE_INDEX.md](docs/DOCUMENTATION_COMPLETE_INDEX.md) - 文档索引

### 索引文档

- [docs/DOCUMENTATION_COMPLETE_INDEX.md](docs/DOCUMENTATION_COMPLETE_INDEX.md) - 完整文档索引
- [scripts/SCRIPTS_INDEX.md](scripts/SCRIPTS_INDEX.md) - 脚本工具索引
- [backend/tests/README.md](backend/tests/README.md) - 测试文档索引
- [backend/scripts/README.md](backend/scripts/README.md) - 后端脚本索引

---

**最后更新**: 2026-01-26  
**版本**: v1.0.0
