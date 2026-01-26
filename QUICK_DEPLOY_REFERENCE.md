# 🚀 快速部署参考卡片

## 📦 一键部署（推荐）

```bash
# 1. 进入项目目录
cd /opt/zy/qyd_api

# 2. 拉取最新代码
git pull

# 3. 配置环境变量
cp .env.high_concurrency .env
vim .env  # 修改数据库和 Redis 配置

# 4. 运行部署脚本
chmod +x deploy-high-concurrency.sh
bash deploy-high-concurrency.sh
```

**部署时间**: 约 10-15 分钟  
**容器数量**: 5个后端 + 5个队列 + 1个前端 + 1个Redis  
**预期性能**: 20,000 - 50,000 QPS

---

## 🔧 常用命令

### 查看状态
```bash
# 查看所有容器
docker compose ps

# 查看资源使用
docker stats

# 查看日志
docker compose logs -f --tail=100
```

### 服务管理
```bash
# 重启服务
docker compose restart

# 停止服务
docker compose stop

# 启动服务
docker compose up -d --scale backend-api=5 --scale queue-worker=5

# 删除服务
docker compose down
```

### 扩展容器
```bash
# 扩展到 10 个容器
docker compose up -d --scale backend-api=10 --scale queue-worker=10

# 缩减到 3 个容器
docker compose up -d --scale backend-api=3 --scale queue-worker=3
```

---

## 📊 监控命令

### 数据库监控
```bash
# 查看 MySQL 连接数
mysql -h 192.168.13.6 -u root -p -e "SHOW PROCESSLIST;" | wc -l

# 查看慢查询
tail -f /var/log/mysql/slow.log
```

### Redis 监控
```bash
# 查看 Redis 连接数
docker compose exec redis redis-cli -a redis_fNmAxZ CLIENT LIST | wc -l

# 查看队列长度
docker compose exec redis redis-cli -a redis_fNmAxZ LLEN project_account_queue

# 查看 Redis 内存
docker compose exec redis redis-cli -a redis_fNmAxZ INFO memory
```

### 性能测试
```bash
# 基础压测（1000并发，10000请求）
ab -n 10000 -c 1000 -k http://192.168.13.6:6080/docs

# 持续压测（60秒）
wrk -t12 -c1000 -d60s http://192.168.13.6:6080/docs
```

---

## 🎯 性能指标

| 指标 | 目标值 | 检查命令 |
|------|--------|----------|
| HTTP QPS | > 20,000 | `ab -n 10000 -c 1000` |
| 队列处理 | > 50,000/秒 | 查看 Redis 队列 |
| 平均响应 | < 50ms | `wrk` 测试结果 |
| P99 响应 | < 200ms | `wrk` 测试结果 |
| CPU 使用 | < 80% | `docker stats` |
| 内存使用 | < 16GB | `free -h` |
| 数据库连接 | ~750 个 | MySQL PROCESSLIST |
| Redis 连接 | ~1000 个 | Redis CLIENT LIST |

---

## 🐛 快速故障排查

### 容器启动失败
```bash
# 查看日志
docker compose logs backend-api --tail=200

# 重启容器
docker compose restart backend-api
```

### 数据库连接失败
```bash
# 测试连接
mysql -h 192.168.13.6 -u root -p

# 检查配置
cat .env | grep DB_
```

### Redis 连接失败
```bash
# 查看 Redis 状态
docker compose ps redis

# 测试连接
docker compose exec redis redis-cli -a redis_fNmAxZ PING
```

### 性能不足
```bash
# 增加容器数量
docker compose up -d --scale backend-api=10 --scale queue-worker=10

# 查看资源使用
docker stats
top
```

---

## 📚 详细文档

- **完整部署指南**: [HIGH_CONCURRENCY_DEPLOYMENT.md](HIGH_CONCURRENCY_DEPLOYMENT.md)
- **检查清单**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **快速开始**: [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)

---

## 🔗 访问地址

- **前端**: http://192.168.13.6
- **后端**: http://192.168.13.6:6080
- **API 文档**: http://192.168.13.6:6080/docs

**默认账号**:
- 邮箱: `zhiyu`
- 密码: `2201101122@qq.com`

---

**最后更新**: 2026-01-26
