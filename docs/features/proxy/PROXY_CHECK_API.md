# 代理检测 API

## 功能概述

代理检测 API 用于检测代理服务器是否可用，通过访问多个 IP 检测网站来验证代理的连通性。

## API 端点

```
GET /v1/system/proxy/check
```

## 功能特性

### ✅ 已实现

1. **多网站检测**：依次访问 3 个 IP 检测网站
2. **智能切换**：如果第一个网站失败，自动尝试下一个
3. **代理支持**：支持 HTTP 和 SOCKS5 代理
4. **本机检测**：不提供代理时检测本机网络
5. **详细信息**：返回检测到的 IP 和详细信息

### 检测网站列表

1. **https://api.ipify.org/**
   - 返回格式：纯文本
   - 返回内容：IP 地址

2. **https://api.myip.com/**
   - 返回格式：JSON
   - 返回内容：IP 地址和其他信息

3. **https://iprust.io/ip.json**
   - 返回格式：JSON
   - 返回内容：IP 地址和其他信息

## 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| proxy_url | string | 否 | 代理地址 | http://127.0.0.1:7890 |

### 代理地址格式

#### HTTP 代理
```
http://ip:port
http://user:pass@ip:port
```

#### SOCKS5 代理
```
socks5h://ip:port
socks5h://user:pass@ip:port
```

## 响应格式

```json
{
  "message": "代理检测成功",
  "status": "success",
  "proxy_url": "http://127.0.0.1:7890",
  "ip": "1.2.3.4",
  "source": "ipify",
  "details": {
    "raw": "1.2.3.4"
  }
}
```

### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| message | string | 提示信息 |
| status | string | 代理状态：success（可用）/ failed（不可用） |
| proxy_url | string | 代理地址（如果提供） |
| ip | string | 检测到的 IP 地址 |
| source | string | 检测来源网站（ipify/myip/iprust） |
| details | object | 详细信息（包含原始响应内容） |

## 使用示例

### 示例 1：检测本机网络

**请求**：
```bash
curl -X GET 'http://127.0.0.1:6080/v1/system/proxy/check' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**响应**：
```json
{
  "message": "网络连接正常",
  "status": "success",
  "proxy_url": null,
  "ip": "151.241.129.29",
  "source": "ipify",
  "details": {
    "raw": "151.241.129.29"
  }
}
```

### 示例 2：检测 HTTP 代理

**请求**：
```bash
curl -X GET 'http://127.0.0.1:6080/v1/system/proxy/check?proxy_url=http://127.0.0.1:7890' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**响应（代理可用）**：
```json
{
  "message": "代理检测成功",
  "status": "success",
  "proxy_url": "http://127.0.0.1:7890",
  "ip": "5.6.7.8",
  "source": "ipify",
  "details": {
    "raw": "5.6.7.8"
  }
}
```

**响应（代理不可用）**：
```json
{
  "message": "代理检测失败，所有检测网站均无法访问",
  "status": "failed",
  "proxy_url": "http://127.0.0.1:7890",
  "ip": null,
  "source": null,
  "details": {
    "error": "所有检测网站均返回非 200 状态码或请求超时"
  }
}
```

### 示例 3：检测 SOCKS5 代理

**请求**：
```bash
curl -X GET 'http://127.0.0.1:6080/v1/system/proxy/check?proxy_url=socks5h://127.0.0.1:1080' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**响应**：
```json
{
  "message": "代理检测成功",
  "status": "success",
  "proxy_url": "socks5h://127.0.0.1:1080",
  "ip": "9.10.11.12",
  "source": "myip",
  "details": {
    "ip": "9.10.11.12",
    "country": "United States",
    "cc": "US"
  }
}
```

### 示例 4：检测带认证的代理

**请求**：
```bash
curl -X GET 'http://127.0.0.1:6080/v1/system/proxy/check?proxy_url=http://user:pass@127.0.0.1:7890' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

## 技术实现

### 1. 使用 Req._req2 方法

```python
result = await Req._req2(
    method="GET",
    url=check_site["url"],
    proxy_url=proxy_url,
    ran_env="chrome124"
)
```

### 2. 依次检测多个网站

```python
check_urls = [
    {"url": "https://api.ipify.org/", "name": "ipify", "type": "text"},
    {"url": "https://api.myip.com/", "name": "myip", "type": "json"},
    {"url": "https://iprust.io/ip.json", "name": "iprust", "type": "json"}
]

for check_site in check_urls:
    result = await Req._req2(...)
    if result["code"] == 200:
        # 检测成功，返回结果
        return ProxyCheckOut(...)
```

### 3. 解析不同格式的响应

```python
if check_site["type"] == "text":
    # 纯文本格式
    ip = content.strip()
elif check_site["type"] == "json":
    # JSON 格式
    ip = content.get("ip") or content.get("IP") or content.get("query")
```

### 4. 错误处理

```python
try:
    result = await Req._req2(...)
    if result["code"] == 200:
        return success_response
except Exception as e:
    # 当前网站失败，继续下一个
    continue

# 所有网站都失败
return failed_response
```

## 检测逻辑

```
开始检测
    ↓
访问 ipify.org
    ↓
状态码 = 200？
    ├─ 是 → 返回成功结果
    └─ 否 → 访问 myip.com
              ↓
          状态码 = 200？
              ├─ 是 → 返回成功结果
              └─ 否 → 访问 iprust.io
                        ↓
                    状态码 = 200？
                        ├─ 是 → 返回成功结果
                        └─ 否 → 返回失败结果
```

## 使用场景

### 场景 1：检测本机网络

```bash
# 不提供 proxy_url 参数
curl -X GET 'http://127.0.0.1:6080/v1/system/proxy/check' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**用途**：
- 检查服务器网络连接
- 获取服务器公网 IP
- 验证网络配置

### 场景 2：验证代理可用性

```bash
# 提供 proxy_url 参数
curl -X GET 'http://127.0.0.1:6080/v1/system/proxy/check?proxy_url=http://proxy.example.com:8080' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

**用途**：
- 验证代理服务器是否在线
- 检查代理配置是否正确
- 获取代理出口 IP

### 场景 3：批量检测代理池

```python
import requests

proxies = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "socks5h://proxy3.example.com:1080"
]

for proxy in proxies:
    response = requests.get(
        "http://127.0.0.1:6080/v1/system/proxy/check",
        params={"proxy_url": proxy},
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )
    result = response.json()
    
    if result["status"] == "success":
        print(f"✅ {proxy} - 可用 - IP: {result['ip']}")
    else:
        print(f"❌ {proxy} - 不可用")
```

## 权限要求

- 需要登录认证（JWT Token）
- 所有登录用户都可以使用此 API

## 注意事项

1. **超时时间**：每个网站的请求超时时间为 30 秒
2. **顺序检测**：按照 ipify → myip → iprust 的顺序检测
3. **首个成功**：只要有一个网站返回 200，就认为代理可用
4. **全部失败**：只有 3 个网站都失败，才认为代理不可用
5. **代理格式**：确保代理地址格式正确（http:// 或 socks5h://）
6. **网络环境**：使用 chrome124 浏览器环境模拟

## 错误处理

### 1. 代理地址格式错误

如果代理地址格式不正确，请求可能会失败。

**正确格式**：
- `http://127.0.0.1:7890`
- `socks5h://127.0.0.1:1080`
- `http://user:pass@proxy.com:8080`

**错误格式**：
- `127.0.0.1:7890`（缺少协议）
- `http//127.0.0.1:7890`（协议格式错误）

### 2. 代理服务未启动

如果代理服务未启动或地址错误，所有检测网站都会失败。

**响应**：
```json
{
  "message": "代理检测失败，所有检测网站均无法访问",
  "status": "failed",
  "proxy_url": "http://127.0.0.1:7890",
  "ip": null,
  "source": null,
  "details": {
    "error": "所有检测网站均返回非 200 状态码或请求超时"
  }
}
```

### 3. 网络连接问题

如果服务器本身无法访问外网，即使不使用代理也会失败。

## 测试

### 运行测试脚本

```bash
cd backend
python test_proxy_check.py
```

### 测试内容

1. ✅ 测试本机网络（不使用代理）
2. ✅ 测试 HTTP 代理
3. ✅ 测试 SOCKS5 代理
4. ✅ 测试无效代理

## 相关文件

### 后端
- `backend/app/apis/v1/system/proxy.py` - 代理检测 API
- `backend/app/apis/v1/system/__init__.py` - 路由注册
- `backend/app/utils/req.py` - 网络请求工具
- `backend/test_proxy_check.py` - 测试脚本

## API 文档

访问 Swagger 文档查看详细的 API 说明：

```
http://127.0.0.1:6080/docs
```

在 "系统-代理检测" 标签下可以找到此 API。

## 更新日志

### 2026-01-25
- ✅ 创建代理检测 API
- ✅ 支持 HTTP 和 SOCKS5 代理
- ✅ 依次检测 3 个 IP 检测网站
- ✅ 返回详细的检测结果
- ✅ 添加测试脚本
- ✅ 创建完整文档

## 总结

代理检测 API 提供了一个简单可靠的方式来验证代理服务器的可用性。通过依次访问多个 IP 检测网站，确保检测结果的准确性。支持 HTTP 和 SOCKS5 代理，可以用于代理池管理、网络诊断等场景。
