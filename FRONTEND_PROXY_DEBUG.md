# 前端代理 URL 调试指南

## 问题描述

点击"复制代理"和"测试代理"时出现错误，可能是 `proxy_url` 字段为空或未定义。

## 已添加的调试功能

### 1. 控制台日志

在以下位置添加了调试日志：

- **获取服务器列表时**：
  ```javascript
  console.log('服务器列表数据:', res)
  console.log('第一条数据:', res.items?.[0])
  ```

- **点击复制代理时**：
  ```javascript
  console.log('复制代理 - proxyUrl:', proxyUrl, 'proxyType:', proxyType)
  ```

- **点击测试代理时**：
  ```javascript
  console.log('测试代理 - proxyUrl:', proxyUrl, 'serverId:', serverId)
  ```

### 2. 改进的错误提示

- 如果 `proxy_url` 为空，会显示："代理信息不可用，请检查服务器配置"
- 在控制台输出详细的错误信息

## 调试步骤

### 步骤 1: 更新前端代码

在服务器上执行：

```bash
cd /opt/zy/qyd_api
git pull

# 重新构建前端
docker compose -f docker-compose.frontend.yml build frontend

# 重启前端服务
docker compose -f docker-compose.frontend.yml restart frontend
```

### 步骤 2: 打开浏览器开发者工具

1. 在浏览器中打开前端页面
2. 按 `F12` 打开开发者工具
3. 切换到 "Console"（控制台）标签

### 步骤 3: 查看服务器列表数据

刷新页面，在控制台查看输出：

```
服务器列表数据: {message: "成功", count: 10, num: 10, items: Array(10)}
第一条数据: {
  id: "xxx",
  host: "192.168.13.6",
  port: 25000,
  proxy_url: "http://username:password@192.168.13.6:25000",  // 检查这个字段
  proxy_type: "http",  // 检查这个字段
  ...
}
```

**检查点**：
- ✅ `proxy_url` 有值：说明后端正常返回
- ❌ `proxy_url` 为空或 `undefined`：说明后端没有生成代理 URL

### 步骤 4: 点击"复制代理"按钮

在控制台查看输出：

```
复制代理 - proxyUrl: http://username:password@192.168.13.6:25000 proxyType: http
```

**检查点**：
- ✅ `proxyUrl` 有值：说明数据传递正常
- ❌ `proxyUrl` 为 `undefined`：说明前端数据绑定有问题

### 步骤 5: 查看网络请求

1. 切换到 "Network"（网络）标签
2. 刷新页面
3. 找到 `/v1/server/info` 请求
4. 点击查看响应数据

**检查响应数据**：

```json
{
  "message": "成功",
  "count": 10,
  "num": 10,
  "items": [
    {
      "id": "xxx",
      "host": "192.168.13.6",
      "port": 25000,
      "proxy_url": "http://username:password@192.168.13.6:25000",
      "proxy_type": "http",
      ...
    }
  ]
}
```

## 可能的问题和解决方案

### 问题 1: 后端返回的数据中没有 `proxy_url` 字段

**原因**：
- 后端 CRUD 层没有正确生成 `proxy_url`
- 后端 Schema 没有包含 `proxy_url` 字段

**解决方法**：
1. 检查后端日志（参考 `PROXY_URL_DEBUG_GUIDE.md`）
2. 确认用户有服务器账号
3. 重启后端服务应用最新代码

```bash
cd /opt/zy/qyd_api
docker compose -f docker-compose.backend.yml restart backend-api
```

### 问题 2: `proxy_url` 为 `""`（空字符串）

**原因**：
- 服务器的 `port` 字段为 `null`
- 端口不在有效范围内（HTTP: 22000-29999, SOCKS5: 32000-39999）

**解决方法**：
1. 检查数据库中服务器的 `port` 字段
2. 确保端口在有效范围内

```sql
SELECT id, host, port FROM server_info WHERE port IS NULL OR port < 22000;
```

### 问题 3: 前端数据绑定错误

**原因**：
- 前端组件没有正确接收 `proxy_url` 字段
- TypeScript 类型定义不匹配

**解决方法**：
查看控制台日志，确认数据结构是否正确。

### 问题 4: CORS 错误

**原因**：
- 后端 CORS 配置不包含前端地址

**解决方法**：
参考 `CORS_FIX_GUIDE.md` 修复 CORS 配置。

## 完整的调试流程

```bash
# 1. 更新代码
cd /opt/zy/qyd_api
git pull

# 2. 重启后端（应用调试日志）
docker compose -f docker-compose.backend.yml restart backend-api

# 3. 重新构建并重启前端
docker compose -f docker-compose.frontend.yml build frontend
docker compose -f docker-compose.frontend.yml restart frontend

# 4. 查看后端日志
docker compose -f docker-compose.backend.yml logs -f backend-api

# 5. 在浏览器中打开开发者工具，查看控制台输出
```

## 预期的正常输出

### 控制台输出

```
服务器列表数据: {message: "成功", count: 10, num: 10, items: Array(10)}
第一条数据: {
  id: "xxx",
  host: "192.168.13.6",
  port: 25000,
  proxy_url: "http://your_username:your_password@192.168.13.6:25000",
  proxy_type: "http",
  domain: null,
  status: 1,
  is_sale: 1,
  group: {...},
  create_time: "2024-01-27 10:00:00",
  update_time: "2024-01-27 10:00:00"
}

复制代理 - proxyUrl: http://your_username:your_password@192.168.13.6:25000 proxyType: http
```

### 后端日志输出

```
INFO: 生成代理URL - 用户ID: xxx, 用户信息: {...}
INFO: 找到服务器账号 - 用户名: your_username
INFO: 密码解密成功
```

## 下一步

1. 如果控制台显示 `proxy_url` 为空，说明是后端问题，参考 `PROXY_URL_DEBUG_GUIDE.md`
2. 如果控制台显示 `proxy_url` 有值但复制失败，说明是前端问题，检查浏览器权限
3. 如果网络请求失败，检查 CORS 配置

## 相关文档

- `PROXY_URL_DEBUG_GUIDE.md` - 后端调试指南
- `PROXY_URL_DEBUG_QUICK_REF.md` - 快速参考
- `NEXT_STEPS.md` - 下一步操作指南
- `CORS_FIX_GUIDE.md` - CORS 配置指南
