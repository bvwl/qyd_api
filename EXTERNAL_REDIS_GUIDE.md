# 使用外部 Redis 服务器部署指南

本指南说明如何使用已部署的外部 Redis 服务器进行前后端分离部署。

## 📋 架构说明

### 使用外部 Redis 的架构

```
前端服务器 (192.168.1.10)     后端服务器 (192.168.1.20)
┌─────────────────┐           ┌─────────────────┐
│   Frontend      │           │  Backend API    │
│   (Nginx)       │◄──────────┤  (FastAPI)      │
│   Port: 80      │   CORS    │  Port: 6080     │
└─────────────────┘           │                 │
                              │  Queue Worker   │
                              │  (Python)       │
                              └────────┬────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        │                             │
                 ┌──────▼──────┐             ┌───────▼────────┐
                 │    MySQL    │             │     Redis      │
                 │ (外部服务)   │             │  (外部服务)     │
                 └─────────────┘             │ 192.168.1.20   │
                                             │   Port: 6379   │
                                             └────────────────┘
```

### 优势

- ✅ **复用现有资源**: 使用已部署的 Redis 服务器
- ✅ **统一管理**: Redis 可以被多个应用共享
- ✅ **减少容器数量**: 不需要在 Docker 中启动 Redis
- ✅ **灵活配置**: 可以使用专门优化的 Redis 配置

## 🔧 配置说明

### 1. Redis 服务器要求

确保你的 Redis 服务器满足以下要求：

```bash
# 检查 Redis 是否运行
redis-cli -h 192.168.1.20 -p 6379 -a your_password ping

# 应该返回: PONG
```

**必需配置**:
- Redis 版本: 6.0 或更高
- 绑定地址: 允许后端服务器访问
- 密码保护: 建议启用
- 持久化: 建议启用 AOF 或 RDB

### 2. Redis 配置文件

编辑 Redis 配置文件 `/etc/redis/redis.conf`:

```conf
# 绑定地址（允许后端服务器访问）
bind 0.0.0.0

# 或只允许特定 IP
# bind 127.0.0.1 192.168.1.20

# 设置密码
requirepass redis_fNmAxZ

# 最大内存（根据实际情况调整）
maxmemory 2gb
maxmemory-policy allkeys-lru

# 持久化配置
appendonly yes
appendfsync everysec

# 日志级别
loglevel notice
logfile /var/log/redis/redis-server.log
```

重启 Redis:

```bash
sudo systemctl restart redis
sudo systemctl enable redis
```

### 3. 防火墙配置

允许后端服务器访问 Redis:

```bash
# 如果 Redis 和后端在同一服务器，无需配置

# 如果 Redis 在不同服务器，允许后端服务器访问
sudo ufw allow from 192.168.1.20 to any port 6379

# 查看防火墙状态
sudo ufw status
```

## 🚀 部署步骤

### Docker 部署

#### 1. 配置环境变量

编辑 `.env.backend` 文件:

```env
# ==========================================
# Redis 配置（外部 Redis 服务器）
# ==========================================
REDIS_ENABLED=1
# Redis 服务器地址（修改为你的 Redis 服务器地址）
REDIS_HOST=192.168.1.20
REDIS_PORT=6379
REDIS_PASSWORD=redis_fNmAxZ
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
```

#### 2. 部署后端

```bash
# 复制配置文件
cp .env.backend .env

# 编辑配置（修改 REDIS_HOST 和 REDIS_PASSWORD）
vim .env

# 一键部署
bash deploy-backend.sh
```

#### 3. 验证连接

```bash
# 查看后端日志
docker-compose -f docker-compose.backend.yml logs -f backend-api

# 应该看到类似的日志：
# INFO: Redis connected successfully
# INFO: Redis version: 7.0.x
```

### 原生部署

#### 1. 配置环境变量

编辑 `backend/.env` 文件:

```env
# Redis 配置
REDIS_ENABLED=1
REDIS_HOST=192.168.1.20
REDIS_PORT=6379
REDIS_PASSWORD=redis_fNmAxZ
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
```

#### 2. 部署后端

```bash
# 运行部署脚本
bash deploy-backend-native.sh

# 脚本会自动跳过 Redis 安装步骤
```

#### 3. 验证连接

```bash
# 查看 API 日志
sudo journalctl -u qyd-api -f

# 查看 Worker 日志
sudo journalctl -u qyd-worker -f
```

## 🧪 测试 Redis 连接

### 方法 1: 使用 redis-cli

```bash
# 测试连接
redis-cli -h 192.168.1.20 -p 6379 -a redis_fNmAxZ ping

# 查看 Redis 信息
redis-cli -h 192.168.1.20 -p 6379 -a redis_fNmAxZ info

# 查看键数量
redis-cli -h 192.168.1.20 -p 6379 -a redis_fNmAxZ dbsize
```

### 方法 2: 使用 Python 脚本

创建测试脚本 `test_redis.py`:

```python
import redis
import os

# 从环境变量读取配置
redis_host = os.getenv('REDIS_HOST', '192.168.1.20')
redis_port = int(os.getenv('REDIS_PORT', '6379'))
redis_password = os.getenv('REDIS_PASSWORD', 'redis_fNmAxZ')

try:
    # 连接 Redis
    r = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        decode_responses=True
    )
    
    # 测试连接
    if r.ping():
        print(f"✓ Redis 连接成功: {redis_host}:{redis_port}")
        
        # 获取 Redis 信息
        info = r.info()
        print(f"✓ Redis 版本: {info['redis_version']}")
        print(f"✓ 已使用内存: {info['used_memory_human']}")
        print(f"✓ 键数量: {r.dbsize()}")
    else:
        print("✗ Redis 连接失败")
        
except redis.ConnectionError as e:
    print(f"✗ Redis 连接错误: {e}")
except Exception as e:
    print(f"✗ 错误: {e}")
```

运行测试:

```bash
# Docker 部署
docker-compose -f docker-compose.backend.yml exec backend-api python test_redis.py

# 原生部署
cd /opt/qyd/backend
source venv/bin/activate
python test_redis.py
```

## 🐛 故障排查

### 1. 无法连接 Redis

**问题**: 后端日志显示 "Error connecting to Redis"

**排查步骤**:

```bash
# 1. 检查 Redis 是否运行
sudo systemctl status redis

# 2. 测试 Redis 连接
redis-cli -h 192.168.1.20 -p 6379 -a redis_fNmAxZ ping

# 3. 检查防火墙
sudo ufw status

# 4. 检查 Redis 绑定地址
grep "^bind" /etc/redis/redis.conf

# 5. 查看 Redis 日志
sudo tail -f /var/log/redis/redis-server.log
```

**解决方案**:

1. 确保 Redis 正在运行:
```bash
sudo systemctl start redis
sudo systemctl enable redis
```

2. 修改 Redis 绑定地址:
```bash
# 编辑配置文件
sudo vim /etc/redis/redis.conf

# 修改绑定地址
bind 0.0.0.0

# 重启 Redis
sudo systemctl restart redis
```

3. 开放防火墙:
```bash
sudo ufw allow from 192.168.1.20 to any port 6379
```

### 2. Redis 密码错误

**问题**: "NOAUTH Authentication required"

**解决方案**:

检查密码配置:

```bash
# 查看 Redis 配置
grep "^requirepass" /etc/redis/redis.conf

# 确保 .env 文件中的密码一致
grep "REDIS_PASSWORD" .env
```

### 3. Redis 连接超时

**问题**: "Connection timeout"

**解决方案**:

1. 检查网络连接:
```bash
# 测试网络连通性
ping 192.168.1.20

# 测试端口连通性
telnet 192.168.1.20 6379
```

2. 增加超时时间:
```env
# .env 文件
REDIS_TIMEOUT=10
```

### 4. Redis 内存不足

**问题**: "OOM command not allowed when used memory > 'maxmemory'"

**解决方案**:

1. 增加最大内存:
```bash
# 编辑 Redis 配置
sudo vim /etc/redis/redis.conf

# 修改最大内存
maxmemory 4gb

# 重启 Redis
sudo systemctl restart redis
```

2. 配置内存淘汰策略:
```conf
maxmemory-policy allkeys-lru
```

## 📊 性能优化

### 1. Redis 连接池配置

根据并发量调整连接池大小:

```env
# 低并发（< 1000 请求/秒）
REDIS_MAX_CONNECTIONS=50

# 中等并发（1000-5000 请求/秒）
REDIS_MAX_CONNECTIONS=100

# 高并发（> 5000 请求/秒）
REDIS_MAX_CONNECTIONS=200
```

### 2. Redis 持久化优化

根据数据重要性选择持久化策略:

```conf
# 方案 1: 只使用 AOF（数据安全性高）
appendonly yes
appendfsync everysec

# 方案 2: 只使用 RDB（性能高）
save 900 1
save 300 10
save 60 10000

# 方案 3: 同时使用 AOF 和 RDB（推荐）
appendonly yes
appendfsync everysec
save 900 1
```

### 3. Redis 内存优化

```conf
# 启用内存压缩
hash-max-ziplist-entries 512
hash-max-ziplist-value 64

# 启用 LZF 压缩
rdbcompression yes

# 启用键过期
maxmemory-policy allkeys-lru
```

## 🔒 安全建议

1. ✅ **启用密码保护**: 设置强密码
2. ✅ **限制访问**: 只允许必要的 IP 访问
3. ✅ **禁用危险命令**: 重命名或禁用 FLUSHALL、FLUSHDB 等命令
4. ✅ **使用 TLS**: 在生产环境启用 TLS 加密
5. ✅ **定期备份**: 配置自动备份策略
6. ✅ **监控日志**: 定期检查 Redis 日志
7. ✅ **限制内存**: 设置合理的 maxmemory
8. ✅ **更新版本**: 保持 Redis 版本最新

### 禁用危险命令

编辑 `/etc/redis/redis.conf`:

```conf
# 重命名危险命令
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command SHUTDOWN ""
```

## 📚 相关文档

- [前后端分离部署指南](SEPARATE_DEPLOYMENT_GUIDE.md)
- [快速参考](SEPARATE_DEPLOYMENT_QUICK_REF.md)
- [原生部署指南](SEPARATE_DEPLOYMENT_NATIVE.md)
- [部署文档索引](DEPLOYMENT_README.md)

## 🆘 获取帮助

如遇到问题：

1. 查看 Redis 日志: `sudo tail -f /var/log/redis/redis-server.log`
2. 查看后端日志: `docker-compose -f docker-compose.backend.yml logs -f`
3. 测试 Redis 连接: `redis-cli -h <host> -p <port> -a <password> ping`
4. 查看本文档的故障排查章节

---

**最后更新**: 2026-01-27  
**版本**: v1.0.0
