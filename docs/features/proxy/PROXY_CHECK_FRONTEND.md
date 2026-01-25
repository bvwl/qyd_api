# 代理检测 - 前端直接检测

## 功能概述

代理检测功能已改为前端直接检测，不再通过后端 API。前端直接访问 IP 检测网站来验证代理是否可用。

## 技术方案

### 前端直接检测

前端使用 axios 直接访问 IP 检测网站，通过配置代理参数来测试代理可用性。

### 优势

1. **减少后端负载**：不需要后端处理代理检测请求
2. **更快响应**：直接从浏览器发起请求，减少中间环节
3. **实时反馈**：用户可以直接看到检测过程
4. **降低成本**：不占用服务器资源

### 限制

1. **SOCKS5 不支持**：浏览器环境不支持 SOCKS5 代理
2. **CORS 限制**：某些检测网站可能有 CORS 限制
3. **浏览器限制**：受浏览器安全策略限制

## 实现方式

### 1. 检测函数

```typescript
export const checkProxyDirect = async (proxyUrl: string): Promise<ProxyCheckResult> => {
  // 检测网站列表
  const checkUrls = [
    {
      url: 'https://api.ipify.org/?format=json',
      name: 'ipify',
      type: 'json' as const
    },
    {
      url: 'https://api.myip.com/',
      name: 'myip',
      type: 'json' as const
    },
    {
      url: 'https://api64.ipify.org/?format=json',
      name: 'ipify64',
      type: 'json' as const
    }
  ]

  // 解析代理 URL
  const proxyUrlObj = new URL(proxyUrl)
  const protocol = proxyUrlObj.protocol.replace(':', '')
  const host = proxyUrlObj.hostname
  const port = parseInt(proxyUrlObj.port)
  const username = proxyUrlObj.username
  const password = proxyUrlObj.password

  // 构建代理配置
  let proxyConfig: any = undefined
  
  if (protocol === 'http' || protocol === 'https') {
    proxyConfig = {
      host,
      port,
      protocol: 'http',
      ...(username && password ? { auth: { username, password } } : {})
    }
  } else if (protocol === 'socks5' || protocol === 'socks5h') {
    // 浏览器环境不支持 SOCKS5
    return {
      message: '浏览器环境不支持 SOCKS5 代理，请使用 HTTP 代理',
      status: 'failed',
      proxy_url: proxyUrl,
      ip: null,
      source: null,
      details: { error: 'SOCKS5 代理需要后端支持或浏览器扩展' }
    }
  }

  // 依次检测
  for (const checkSite of checkUrls) {
    try {
      const response = await axios.get(checkSite.url, {
        proxy: proxyConfig,
        timeout: 10000,
        headers: {
          'Accept': 'application/json'
        }
      })

      if (response.status === 200) {
        const data = response.data
        const ip = data.ip || data.IP || data.query

        return {
          message: '代理检测成功',
          status: 'success',
          proxy_url: proxyUrl,
          ip,
          source: checkSite.name,
          details: data
        }
      }
    } catch (error: any) {
      // 当前网站失败，继续下一个
      continue
    }
  }

  // 所有网站都失败
  return {
    message: '代理检测失败，所有检测网站均无法访问',
    status: 'failed',
    proxy_url: proxyUrl,
    ip: null,
    source: null,
    details: { error: '所有检测网站均返回非 200 状态码或请求超时' }
  }
}
```

### 2. 使用方式

```typescript
const handleTestProxy = async (proxyUrl?: string, serverId?: string) => {
  if (!proxyUrl) {
    message.warning('代理信息不可用')
    return
  }

  setTestingProxy(serverId || null)
  
  try {
    const result = await checkProxyDirect(proxyUrl)
    
    if (result.status === 'success') {
      Modal.success({
        title: '代理检测成功',
        content: (
          <div>
            <p><strong>代理地址：</strong>{proxyUrl}</p>
            <p><strong>检测IP：</strong>{result.ip}</p>
            <p><strong>检测来源：</strong>{result.source}</p>
            <p style={{ color: '#52c41a', marginTop: 8 }}>✅ 代理可用</p>
          </div>
        ),
      })
    } else {
      Modal.error({
        title: '代理检测失败',
        content: (
          <div>
            <p><strong>代理地址：</strong>{proxyUrl}</p>
            <p style={{ color: '#ff4d4f', marginTop: 8 }}>❌ 代理不可用</p>
            <p><strong>原因：</strong>{result.details?.error || result.message}</p>
          </div>
        ),
      })
    }
  } catch (error: any) {
    Modal.error({
      title: '代理检测失败',
      content: (
        <div>
          <p><strong>代理地址：</strong>{proxyUrl}</p>
          <p style={{ color: '#ff4d4f', marginTop: 8 }}>❌ 检测请求失败</p>
          <p><strong>错误：</strong>{error.message || '未知错误'}</p>
        </div>
      ),
    })
  } finally {
    setTestingProxy(null)
  }
}
```

## 检测网站

### 1. ipify (主要)
- **URL**: https://api.ipify.org/?format=json
- **格式**: JSON
- **响应**: `{"ip": "1.2.3.4"}`

### 2. myip (备用)
- **URL**: https://api.myip.com/
- **格式**: JSON
- **响应**: `{"ip": "1.2.3.4", "country": "US", ...}`

### 3. ipify64 (备用)
- **URL**: https://api64.ipify.org/?format=json
- **格式**: JSON
- **响应**: `{"ip": "1.2.3.4"}`

## 支持的代理类型

### ✅ HTTP 代理

**格式**：
```
http://ip:port
http://user:pass@ip:port
```

**示例**：
```
http://127.0.0.1:7890
http://user:pass@proxy.example.com:8080
```

### ❌ SOCKS5 代理

**限制**：浏览器环境不支持 SOCKS5 代理

**提示**：
```
浏览器环境不支持 SOCKS5 代理，请使用 HTTP 代理
```

**原因**：
- 浏览器的 axios 库不支持 SOCKS5 协议
- 需要通过后端或浏览器扩展来支持

**解决方案**：
1. 使用 HTTP 代理替代
2. 使用后端 API 检测（保留的备用方案）
3. 使用浏览器扩展（如 SwitchyOmega）

## 检测流程

```
开始检测
    ↓
解析代理地址
    ↓
检查代理类型
    ├─ HTTP → 继续
    └─ SOCKS5 → 返回不支持
         ↓
访问 ipify.org
    ↓
状态码 = 200？
    ├─ 是 → 返回成功结果
    └─ 否 → 访问 myip.com
              ↓
          状态码 = 200？
              ├─ 是 → 返回成功结果
              └─ 否 → 访问 ipify64.org
                        ↓
                    状态码 = 200？
                        ├─ 是 → 返回成功结果
                        └─ 否 → 返回失败结果
```

## 错误处理

### 1. 代理地址格式错误

```typescript
try {
  const proxyUrlObj = new URL(proxyUrl)
  // ...
} catch (error) {
  return {
    message: '代理地址格式错误',
    status: 'failed',
    proxy_url: proxyUrl,
    ip: null,
    source: null,
    details: { error: '无法解析代理地址' }
  }
}
```

### 2. SOCKS5 不支持

```typescript
if (protocol === 'socks5' || protocol === 'socks5h') {
  return {
    message: '浏览器环境不支持 SOCKS5 代理，请使用 HTTP 代理',
    status: 'failed',
    proxy_url: proxyUrl,
    ip: null,
    source: null,
    details: { error: 'SOCKS5 代理需要后端支持或浏览器扩展' }
  }
}
```

### 3. 所有网站都失败

```typescript
return {
  message: '代理检测失败，所有检测网站均无法访问',
  status: 'failed',
  proxy_url: proxyUrl,
  ip: null,
  source: null,
  details: { error: '所有检测网站均返回非 200 状态码或请求超时' }
}
```

## 注意事项

### 1. CORS 限制

某些检测网站可能有 CORS 限制，导致浏览器无法直接访问。

**解决方案**：
- 使用支持 CORS 的检测网站
- 使用后端 API 作为备用方案

### 2. 浏览器安全策略

浏览器可能会阻止某些代理请求。

**解决方案**：
- 使用 HTTPS 检测网站
- 确保代理服务器支持 HTTPS

### 3. 超时时间

每个检测请求的超时时间为 10 秒。

```typescript
const response = await axios.get(checkSite.url, {
  proxy: proxyConfig,
  timeout: 10000,  // 10 秒
  headers: {
    'Accept': 'application/json'
  }
})
```

### 4. SOCKS5 代理

如果需要检测 SOCKS5 代理，请使用后端 API：

```typescript
// 后端代理检测（保留作为备用）
export const checkProxy = (proxyUrl?: string) => {
  return api.get<any, ProxyCheckResult>('/v1/system/proxy/check', {
    params: { proxy_url: proxyUrl }
  })
}
```

## 使用场景

### 场景 1：检测 HTTP 代理

```typescript
const proxyUrl = 'http://127.0.0.1:7890'
const result = await checkProxyDirect(proxyUrl)

if (result.status === 'success') {
  console.log('代理可用，IP:', result.ip)
} else {
  console.log('代理不可用，原因:', result.details.error)
}
```

### 场景 2：检测带认证的 HTTP 代理

```typescript
const proxyUrl = 'http://user:pass@proxy.example.com:8080'
const result = await checkProxyDirect(proxyUrl)
```

### 场景 3：检测 SOCKS5 代理（不支持）

```typescript
const proxyUrl = 'socks5h://127.0.0.1:1080'
const result = await checkProxyDirect(proxyUrl)

// 返回：浏览器环境不支持 SOCKS5 代理，请使用 HTTP 代理
```

## 相关文件

### 前端
- `frontend/src/api/system.ts` - 系统 API（已更新）
- `frontend/src/views/Server/ServerList.tsx` - 服务器列表（已更新）

### 后端（备用）
- `backend/app/apis/v1/system/proxy.py` - 代理检测 API（保留）
- `backend/app/utils/req.py` - 网络请求工具（保留）

## 更新日志

### 2026-01-25
- ✅ 改为前端直接检测
- ✅ 支持 HTTP 代理
- ✅ 不支持 SOCKS5 代理（浏览器限制）
- ✅ 添加详细的错误提示
- ✅ 保留后端 API 作为备用

## 总结

代理检测功能已改为前端直接检测，减少了后端负载，提高了响应速度。但由于浏览器限制，目前只支持 HTTP 代理，不支持 SOCKS5 代理。如果需要检测 SOCKS5 代理，可以使用保留的后端 API。
