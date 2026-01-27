# Docker Host 网络模式代理配置说明

## 修改内容

已将 `docker-compose.backend.yml` 修改为使用 **host 网络模式**，这样容器可以直接访问宿主机的代理服务。

## 主要变更

### 1. 网络模式
```yaml
# 之前：使用 bridge 网络 + extra_hosts
ports:
  - "6080:6080"
extra_hosts:
  - "host.docker.internal:host-gateway"
networks:
  - qyd-network

# 现在：使用 host 网络模式
network_mode: "host"
```

### 2. 代理配置
```yaml
# 之前：通过 host.docker.internal 或 172.17.0.1 访问
- HTTP_PROXY=http://host.docker.internal:7890

# 现在：直接使用 127.0.0.1
- HTTP_PROXY=http://127.0.0.1:7890
- HTTPS_PROXY=http://127.0.0.1:7890
- ALL_PROXY=socks5h://127.0.0.1:7891
```

## Host 网络模式的优势

1. **直接访问宿主机服务**：容器和宿主机共享网络栈，可以直接使用 `127.0.0.1` 访问宿主机服务
2. **无需端口映射**：容器内的端口直接暴露在宿主机上
3. **性能更好**：减少了网络层的转发开销
4. **配置简单**：不需要配置 `extra_hosts` 或查找网关 IP

## Host 网络模式的注意事项

1. **端口冲突**：容器使用的端口（如 6080）不能被宿主机其他服务占用
2. **安全性**：容器可以访问宿主机的所有网络接口
3. **仅限 Linux**：host 网络模式在 macOS 和 Windows 上的 Docker Desktop 中行为不同

## 使用方法

### 1. 重启服务
```bash
# 停止现有容器
docker-compose -f docker-compose.backend.yml down

# 启动新配置
docker-compose -f docker-compose.backend.yml up -d

# 查看日志
docker-compose -f docker-compose.backend.yml logs -f
```

### 2. 测试代理
```bash
# 进入容器测试
docker exec -it qyd-backend-api bash

# 在容器内测试代理
curl https://iprust.io/ip.json

# 应该显示代理的 IP 地址
```

### 3. 验证环境变量
```bash
# 查看容器的代理环境变量
docker exec qyd-backend-api env | grep -i proxy
```

## 常见问题

### Q1: apt update 仍然失败？
**原因**：Debian 镜像的 apt 可能不会自动使用 HTTP_PROXY 环境变量。

**解决方案**：在 Dockerfile 中配置 apt 代理
```dockerfile
# 在 apt 命令前添加代理配置
RUN echo 'Acquire::http::Proxy "http://127.0.0.1:7890";' > /etc/apt/apt.conf.d/proxy && \
    apt-get update && \
    apt-get install -y curl && \
    rm /etc/apt/apt.conf.d/proxy
```

### Q2: 代理仍然无法连接？
**检查清单**：
1. 确认宿主机代理正在运行：`curl -x http://127.0.0.1:7890 https://iprust.io/ip.json`
2. 确认代理监听在 `0.0.0.0` 而不是 `127.0.0.1`
3. 检查防火墙规则：`iptables -L -n`
4. 查看容器日志：`docker logs qyd-backend-api`

### Q3: 端口 6080 被占用？
```bash
# 查看端口占用
lsof -i :6080
netstat -tlnp | grep 6080

# 停止占用端口的服务
kill <PID>
```

## 如果需要切换回 Bridge 网络

如果 host 网络模式不适合你的场景，可以使用以下配置：

```yaml
services:
  backend-api:
    ports:
      - "6080:6080"
    environment:
      - HTTP_PROXY=http://172.17.0.1:7890
      - HTTPS_PROXY=http://172.17.0.1:7890
    networks:
      - qyd-network

networks:
  qyd-network:
    driver: bridge
```

**注意**：需要确保代理软件允许来自 Docker 网桥（172.17.0.0/16）的连接。

## 测试脚本

运行测试脚本验证配置：
```bash
./test-docker-proxy.sh
```

## 参考资料

- [Docker 网络模式文档](https://docs.docker.com/network/)
- [Docker Compose 网络配置](https://docs.docker.com/compose/networking/)
- [容器代理配置最佳实践](https://docs.docker.com/network/proxy/)
