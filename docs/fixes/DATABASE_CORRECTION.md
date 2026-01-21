# 数据库文档修正

## 修正时间
2026-01-21

## 问题描述
文档中错误地将数据库标注为PostgreSQL，实际项目使用的是MySQL。

## 修正内容

### 1. README.md
- ✅ 技术栈：PostgreSQL → MySQL
- ✅ 环境要求：PostgreSQL 14+ → MySQL 5.7+ / 8.0+

### 2. backend/README.md
- ✅ 技术栈：PostgreSQL → MySQL
- ✅ 数据库配置示例：
  - 端口：5432 → 3306
  - 用户：postgres → qyd
  - 数据库名：qyd_db → qyd
- ✅ 备份恢复命令：pg_dump/psql → mysqldump/mysql
- ✅ 常见问题：PostgreSQL服务 → MySQL服务

### 3. docs/PROJECT_STRUCTURE.md
- ✅ 开发环境数据流：PostgreSQL → MySQL
- ✅ 生产环境数据流：PostgreSQL → MySQL

## 实际配置

### 数据库引擎
```python
DB_ENGINE = "tortoise.backends.mysql"
```

### 连接配置
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=qyd
DB_PASSWORD=your_password_here
DB_NAME=qyd
```

### 字符集
```python
"charset": "utf8mb4"
```

## 验证
所有文档已修正完成，不再包含PostgreSQL相关引用（node_modules除外）。

## 相关文件
- README.md
- backend/README.md
- backend/.env.example
- backend/app/core/settings.py
- docs/PROJECT_STRUCTURE.md
