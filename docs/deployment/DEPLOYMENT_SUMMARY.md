# 部署文件完善总结

## 📅 更新日期
2026-01-26

## 📦 新增文件

### 1. 依赖管理

#### `backend/requirements.txt` (已完善)
- ✅ 添加版本号，确保依赖稳定性
- ✅ 按功能分类组织（核心框架、数据库、认证、工具等）
- ✅ 添加详细注释说明每个依赖的用途
- ✅ 标记可选依赖

**主要依赖**:
- FastAPI 0.109.0 - Web 框架
- Tortoise ORM 0.20.0 - 异步 ORM
- Aerich 0.7.2 - 数据库迁移工具
- Redis 5.0.1 - 缓存和队列
- python-jose 3.3.0 - JWT 认证

### 2. 部署初始化脚本

#### `backend/deploy_init.py` ✨ 新增
**功能**:
- ✅ 自动检查环境配置
- ✅ 初始化数据库连接
- ✅ 创建所有表结构
- ✅ 导入角色数据（ADMIN, GM, IT, MANUAL）
- ✅ 导入路由数据（菜单和权限）
- ✅ 创建管理员用户
- ✅ 绑定管理员和 GM 权限
- ✅ 验证初始化结果

**使用方法**:
```bash
python backend/deploy_init.py
```

**特点**:
- 🔒 幂等性：可重复运行，不会重复创建数据
- 📊 详细输出：显示每一步的执行结果
- ⚠️ 错误处理：遇到错误会显示详细信息
- ✅ 自动验证：完成后验证数据完整性

### 3. 快速部署脚本

#### `backend/quick_deploy.sh` ✨ 新增
**功能**:
- ✅ 自动检查环境（Python, MySQL, Redis）
- ✅ 创建虚拟环境
- ✅ 安装依赖包
- ✅ 配置环境变量
- ✅ 初始化 Aerich
- ✅ 初始化数据库
- ✅ 导入初始数据
- ✅ 测试服务启动

**使用方法**:
```bash
cd backend
bash quick_deploy.sh
```

**特点**:
- 🎨 彩色输出：清晰的状态提示
- 🔍 环境检查：自动检测必需软件
- 🤝 交互式：可选择是否编辑配置
- 📝 详细日志：每一步都有清晰说明

### 4. 部署检查脚本

#### `backend/check_deployment.py` ✨ 新增
**功能**:
- ✅ 检查 Python 版本
- ✅ 检查依赖包安装
- ✅ 检查环境变量配置
- ✅ 检查数据库连接
- ✅ 检查 Redis 连接
- ✅ 检查目录结构
- ✅ 检查必需文件
- ✅ 检查初始数据

**使用方法**:
```bash
python backend/check_deployment.py
```

**特点**:
- 📊 全面检查：覆盖所有关键配置
- 🎯 精准定位：明确指出问题所在
- 💡 解决建议：提供修复方法
- 📈 统计摘要：显示检查结果统计

### 5. 部署指南文档

#### `backend/DEPLOYMENT_GUIDE.md` ✨ 新增
**内容**:
- 📋 环境要求
- 🚀 快速部署步骤
- 📝 详细部署说明
- ⚙️ 配置说明（性能、读写分离）
- 🔄 数据库迁移指南
- 🐛 常见问题解决
- 📊 监控和维护
- 🔒 安全建议

**特点**:
- 📖 详细完整：覆盖所有部署场景
- 🎯 实用性强：提供可直接使用的命令
- 🔧 问题解决：包含常见问题和解决方案
- 🔐 安全提示：强调安全最佳实践

## 📚 Aerich 数据库迁移

### 配置文件

#### `backend/pyproject.toml` (已存在)
```toml
[tool.aerich]
tortoise_orm = "app.core.settings.TORTOISE_ORM"
location = "./migrations"
src_folder = "./."
```

### 使用流程

#### 1. 初始化 Aerich
```bash
aerich init -t app.core.settings.TORTOISE_ORM
```

#### 2. 初始化数据库
```bash
aerich init-db
```

#### 3. 创建迁移
```bash
# 修改模型后创建迁移
aerich migrate --name "describe_your_changes"

# 应用迁移
aerich upgrade
```

#### 4. 查看迁移历史
```bash
aerich history
aerich heads
```

#### 5. 回滚迁移
```bash
# 回滚到上一个版本
aerich downgrade

# 回滚到指定版本
aerich downgrade -v <version>
```

## 🚀 部署流程

### 方法一：使用快速部署脚本（推荐）

```bash
cd backend
bash quick_deploy.sh
```

脚本会自动完成所有步骤，包括：
1. 检查环境
2. 创建虚拟环境
3. 安装依赖
4. 配置环境变量
5. 初始化数据库
6. 导入初始数据

### 方法二：手动部署

```bash
cd backend

# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
vim .env  # 编辑配置

# 4. 初始化 Aerich
aerich init -t app.core.settings.TORTOISE_ORM

# 5. 初始化数据库
aerich init-db

# 6. 导入初始数据
python deploy_init.py

# 7. 检查部署
python check_deployment.py

# 8. 启动服务
python start.py
```

## ✅ 部署检查清单

使用 `check_deployment.py` 脚本可以自动检查以下项目：

- [ ] Python 版本 >= 3.11
- [ ] 所有依赖包已安装
- [ ] .env 文件已配置
- [ ] 必需环境变量已设置
- [ ] JWT_SECRET_KEY 长度 >= 32
- [ ] 数据库连接正常
- [ ] 数据库表已创建
- [ ] Redis 连接正常（如果启用）
- [ ] 目录结构完整
- [ ] 必需文件存在
- [ ] 角色数据已导入
- [ ] 路由数据已导入
- [ ] 管理员用户已创建

## 📊 初始数据说明

### 角色数据

| 角色代码 | 角色名称 | 说明 | 默认角色 |
|---------|---------|------|---------|
| ADMIN | 管理员 | 系统管理员，拥有所有权限 | 否 |
| GM | 项目管理员 | 可以管理项目和用户 | 否 |
| IT | 技术人员 | 技术支持人员 | 否 |
| MANUAL | 手动操作员 | 手动操作人员 | 是 |

### 路由数据

系统会自动导入以下菜单和路由：

- 仪表盘
- 用户管理（用户列表、角色管理、路由管理、权限管理、API Token、操作日志）
- 项目管理（项目列表、项目账号、项目钱包、批量创建钱包）
- 服务器管理（服务器列表、国家管理、分组管理、服务器账号）
- 邮箱管理（邮箱列表、发送邮件、邮件查看器）
- XUI 管理（XUI服务器、XUI入站、XUI账号、XUI日志）

### 管理员用户

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com
- **角色**: ADMIN
- **权限**: 所有路由

⚠️ **首次登录后请立即修改密码！**

## 🔧 配置文件说明

### `.env` 环境变量

必需配置：
```env
# 数据库
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_password
DB_NAME=qyd

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
```

可选配置：
```env
# Redis
REDIS_ENABLED=1
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# 读写分离
DB_READ_WRITE_SPLIT=0

# 性能配置
REDIS_QUEUE_BATCH_SIZE=200
REDIS_QUEUE_NUM_WORKERS=4
```

详细配置说明请查看 `backend/DEPLOYMENT_GUIDE.md`

## 🎯 性能配置

### 标准性能（2000条/秒）
```bash
cp backend/.env.high_performance backend/.env
# 编辑 .env 配置数据库和 Redis
```

### 超高性能（10000+条/秒）
```bash
cp backend/.env.ultra_high_performance backend/.env
# 编辑 .env 配置数据库和 Redis
```

详细性能配置请查看 `docs/performance/SCALE_TO_10K_GUIDE.md`

## 🐛 常见问题

### 1. 数据库连接失败
```bash
# 检查 MySQL 服务
sudo systemctl status mysql

# 检查配置
python check_deployment.py
```

### 2. Redis 连接失败
```bash
# 检查 Redis 服务
sudo systemctl status redis

# 或禁用 Redis
echo "REDIS_ENABLED=0" >> .env
```

### 3. Aerich 迁移失败
```bash
# 删除 migrations 目录重新初始化
rm -rf backend/migrations
cd backend
aerich init -t app.core.settings.TORTOISE_ORM
aerich init-db
```

### 4. 导入初始数据失败
```bash
# 确保数据库表已创建
cd backend
aerich init-db

# 重新导入
python deploy_init.py
```

更多问题请查看 `backend/DEPLOYMENT_GUIDE.md`

## 📖 相关文档

- [后端部署指南](backend/DEPLOYMENT_GUIDE.md) - 详细部署说明
- [项目结构说明](.kiro/steering/structure.md) - 项目目录结构
- [开发规范](.kiro/steering/conventions.md) - 开发规范和最佳实践
- [技术栈说明](.kiro/steering/tech.md) - 技术栈详细说明
- [性能优化指南](docs/performance/SCALE_TO_10K_GUIDE.md) - 性能优化
- [读写分离部署](docs/mysql主从-单服务器快速部署.md) - MySQL 主从配置

## 🎉 总结

本次更新完善了后端部署相关的所有文件和文档，包括：

✅ **依赖管理**: 完善 requirements.txt，添加版本号和分类
✅ **自动化脚本**: 提供快速部署和检查脚本
✅ **初始化工具**: Python 脚本导入初始数据
✅ **数据库迁移**: 使用 Aerich 管理数据库版本
✅ **详细文档**: 完整的部署指南和问题解决方案

现在可以在新服务器上快速部署后端服务，只需运行：

```bash
cd backend
bash quick_deploy.sh
```

或者按照 `DEPLOYMENT_GUIDE.md` 中的详细步骤手动部署。

---

**更新时间**: 2026-01-26  
**版本**: v1.2.0
