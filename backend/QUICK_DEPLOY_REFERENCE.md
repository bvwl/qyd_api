# 快速部署参考卡片

## 🚀 一键部署

```bash
cd backend
bash quick_deploy.sh
```

## 📋 手动部署步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境
```bash
cp .env.example .env
vim .env  # 配置数据库和 Redis
```

### 3. 初始化数据库
```bash
aerich init -t app.core.settings.TORTOISE_ORM
aerich init-db
python deploy_init.py
```

### 4. 检查部署
```bash
python check_deployment.py
```

### 5. 启动服务
```bash
python start.py
```

## 🔑 默认管理员

- **邮箱**: zhiyu
- **密码**: 2201101122@qq.com
- ⚠️ 首次登录后请立即修改密码！

## 📊 必需环境变量

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_password
DB_NAME=qyd
JWT_SECRET_KEY=your-secret-key-min-32-chars
```

## 🔄 数据库迁移

```bash
# 创建迁移
aerich migrate --name "description"

# 应用迁移
aerich upgrade

# 回滚迁移
aerich downgrade
```

## 🐛 常见问题

### 数据库连接失败
```bash
sudo systemctl status mysql
python check_deployment.py
```

### Redis 连接失败
```bash
sudo systemctl status redis
# 或禁用: echo "REDIS_ENABLED=0" >> .env
```

### 重新初始化
```bash
rm -rf migrations
aerich init -t app.core.settings.TORTOISE_ORM
aerich init-db
python deploy_init.py
```

## 📚 详细文档

- [完整部署指南](DEPLOYMENT_GUIDE.md)
- [部署总结](../DEPLOYMENT_SUMMARY.md)
- [项目结构](../.kiro/steering/structure.md)

## 🔗 快速链接

- API 文档: http://localhost:6080/docs
- ReDoc: http://localhost:6080/redoc
- 前端应用: http://localhost:3000

---

**提示**: 遇到问题先运行 `python check_deployment.py` 检查配置
