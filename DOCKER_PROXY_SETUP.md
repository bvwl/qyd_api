# Docker 容器代理配置指南

## 配置说明

已为后端 Docker 容器配置系统代理，使其可以通过宿主机的代理访问外部网络。

## 配置内容

### 1. 代理环境变量

容器内已配置以下代理环境变量：

```bash
# HTTP/HTTPS 代理
HTTP_PROXY=http://host.docker.internal:7890
HTTPS_PROXY=http://host.docker.internal:7890
http_proxy=http://host.docker.internal:7890
https_proxy=http://host.docker.internal:7890

# SOCKS5 代理
ALL_PROXY=socks5h://host.docker.internal:7891
all_proxy=socks5h://host.docker.internal:7891

# 不走代理的地址
NO_PROXY=localhost,127.0.0.1,::1,host.docker.internal
no_proxy=localhost,127.0.0.1,::1,host.docker.internal
```

### 2. 日志映射

日志已映射到项目根目录的 `logs` 文件夹：

```yaml
volumes:
  - ./logs:/app/logs  # 日志映射到宿主机
```

**日志目录结构**：
```
logs/
├── api/          # API 请求日志（按小时分割）
├── app/          # 应用日志（按小时分割）
├── database/     # 数据库日志（按小时分割）
├── scheduler/    # 定时任务日志（按小时分割）
├── api.log       # 当前 API 日志
├── app.log       # 当前应用日志
├── database.log  # 当前数据库日志
└── scheduler.log # 当前定时任务日志
```

### 3. 宿主机访问配置

使用 `extra_hosts` 允许容器访问宿主机：

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## 使用方法

### 1. 确保宿主机代理正在运行

```bash
# 检查代理状态
clashproxy

# 应该看到：
# 系统代理：开启
# HTTP_PROXY=http://127.0.0.1:7890
# ALL_PROXY=socks5h://127.0.0.1:7891
```

### 2. 重启后端服务

```bash
# 停止服务
docker compose -f docker-compose.backend.yml stop

# 重新构建（如果需要）
docker compose -f docker-compose.backend.yml build

# 启动服务
docker compose -f docker-compose.backend.yml up -d

# 查看日志
docker compose -f docker-compose.backend.yml logs -f backend-api
```

### 3. 验证代理是否生效

```bash
# 进入容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 检查环境变量
env | grep -i proxy

# 测试代理连接
curl -I https://www.google.com

# 退出容器
exit
```

## 代理工作原理

### Docker 网络架构

```
┌─────────────────────────────────────────┐
│          宿主机 (192.168.13.6)           │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   Clash 代理                     │   │
│  │   - HTTP: 127.0.0.1:7890        │   │
│  │   - SOCKS5: 127.0.0.1:7891      │   │
│  └─────────────────────────────────┘   │
│              ↑                          │
│              │ host.docker.internal     │
│              │                          │
│  ┌─────────────────────────────────┐   │
│  │   Docker 容器                    │   │
│  │   - backend-api                 │   │
│  │   - queue-worker                │   │
│  │                                 │   │
│  │   环境变量:                      │   │
│  │   HTTP_PROXY=http://            │   │
│  │     host.docker.internal:7890   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 请求流程

1. **容器内应用发起外部请求**
   - 例如：访问 GitHub API、下载文件等

2. **检查代理环境变量**
   - Python 的 `requests`、`httpx` 等库会自动读取 `HTTP_PROXY` 环境变量

3. **通过 host.docker.internal 访问宿主机**
   - Docker 将 `host.docker.internal` 解析为宿主机 IP

4. **宿主机代理转发请求**
   - Clash 代理接收请求并转发到外部网络

5. **返回响应**
   - 响应原路返回到容器内应用

## 查看日志

### 方式 1: 直接查看宿主机文件

```bash
# 查看当前日志
tail -f logs/app.log
tail -f logs/api.log
tail -f logs/database.log

# 查看历史日志（压缩文件）
ls -lh logs/app/
zcat logs/app/app.log.2026-01-27_10.gz | less
```

### 方式 2: 使用 Docker 命令

```bash
# 查看容器日志
docker compose -f docker-compose.backend.yml logs -f backend-api
docker compose -f docker-compose.backend.yml logs -f queue-worker

# 查看最近 100 行
docker compose -f docker-compose.backend.yml logs --tail=100 backend-api
```

### 方式 3: 进入容器查看

```bash
# 进入容器
docker compose -f docker-compose.backend.yml exec backend-api bash

# 查看日志
tail -f /app/logs/app.log

# 退出
exit
```

## 代理配置选项

### 仅使用 HTTP 代理

如果只想使用 HTTP 代理，可以移除 SOCKS5 配置：

```yaml
environment:
  - HTTP_PROXY=http://host.docker.internal:7890
  - HTTPS_PROXY=http://host.docker.internal:7890
  - NO_PROXY=localhost,127.0.0.1,::1
```

### 仅使用 SOCKS5 代理

如果只想使用 SOCKS5 代理：

```yaml
environment:
  - ALL_PROXY=socks5h://host.docker.internal:7891
  - NO_PROXY=localhost,127.0.0.1,::1
```

### 禁用代理

如果需要临时禁用代理，注释掉代理环境变量：

```yaml
environment:
  # - HTTP_PROXY=http://host.docker.internal:7890
  # - HTTPS_PROXY=http://host.docker.internal:7890
  # - ALL_PROXY=socks5h://host.docker.internal:7891
```

## 常见问题

### Q1: 容器无法访问外部网络

**检查步骤**：

1. 确认宿主机代理正在运行：
   ```bash
   clashproxy
   curl -x http://127.0.0.1:7890 https://www.google.com
   ```

2. 检查容器内代理环境变量：
   ```bash
   docker compose -f docker-compose.backend.yml exec backend-api env | grep -i proxy
   ```

3. 测试容器到宿主机的连接：
   ```bash
   docker compose -f docker-compose.backend.yml exec backend-api ping host.docker.internal
   ```

### Q2: 日志文件权限问题

如果日志文件无法写入，检查权限：

```bash
# 修改日志目录权限
chmod -R 755 logs/
chown -R $USER:$USER logs/
```

### Q3: 代理导致内网访问变慢

将内网地址添加到 `NO_PROXY`：

```yaml
environment:
  - NO_PROXY=localhost,127.0.0.1,::1,host.docker.internal,192.168.0.0/16,10.0.0.0/8
```

### Q4: 日志文件太大

日志会自动按小时分割并压缩，旧日志会自动清理（默认保留 90 天）。

手动清理：
```bash
# 删除 30 天前的日志
find logs/ -name "*.gz" -mtime +30 -delete
```

## 性能影响

### 代理对性能的影响

- **HTTP 代理**：增加约 10-50ms 延迟
- **SOCKS5 代理**：增加约 5-30ms 延迟
- **内网访问**：不走代理，无影响（通过 NO_PROXY 配置）

### 优化建议

1. **内网地址不走代理**：
   - 数据库、Redis 等内网服务添加到 `NO_PROXY`

2. **选择合适的代理类型**：
   - HTTP/HTTPS 请求：使用 HTTP 代理
   - 其他协议：使用 SOCKS5 代理

3. **代理服务器优化**：
   - 使用本地代理（127.0.0.1）而不是远程代理
   - 确保代理服务器性能良好

## 相关文档

- [Docker 部署指南](./DEPLOYMENT_README.md)
- [Docker 代码更新指南](./DOCKER_CODE_UPDATE_GUIDE.md)
- [后端重启指南](./RESTART_BACKEND_GUIDE.md)
