import api from './index'
import axios from 'axios'

// 代理检测响应类型
export interface ProxyCheckResult {
  message: string
  status: 'success' | 'failed'
  proxy_url: string | null
  ip: string | null
  source: string | null
  details: any
}

// 前端直接检测代理
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
  let proxyConfig: any = undefined
  
  try {
    const proxyUrlObj = new URL(proxyUrl)
    const protocol = proxyUrlObj.protocol.replace(':', '')
    const host = proxyUrlObj.hostname
    const port = parseInt(proxyUrlObj.port)
    const username = proxyUrlObj.username
    const password = proxyUrlObj.password

    // 构建代理配置
    if (protocol === 'http' || protocol === 'https') {
      proxyConfig = {
        host,
        port,
        protocol: 'http',
        ...(username && password ? { auth: { username, password } } : {})
      }
    } else if (protocol === 'socks5' || protocol === 'socks5h') {
      // 注意：浏览器环境不支持 SOCKS5 代理
      // 需要通过后端或浏览器扩展来支持
      return {
        message: '浏览器环境不支持 SOCKS5 代理，请使用 HTTP 代理',
        status: 'failed',
        proxy_url: proxyUrl,
        ip: null,
        source: null,
        details: { error: 'SOCKS5 代理需要后端支持或浏览器扩展' }
      }
    }
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
        let ip = null

        if (checkSite.type === 'json') {
          ip = data.ip || data.IP || data.query
        }

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
      console.log(`检测网站 ${checkSite.name} 失败:`, error.message)
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

// 后端代理检测（保留作为备用）
export const checkProxy = (proxyUrl?: string) => {
  return api.get<any, ProxyCheckResult>('/v1/system/proxy/check', {
    params: { proxy_url: proxyUrl }
  })
}
