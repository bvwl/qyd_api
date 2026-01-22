import axios, { AxiosError } from 'axios'
import { message } from 'antd'

// 配置message的全局配置，减少主题警告
message.config({
  top: 100,
  duration: 3,
  maxCount: 3,
})

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:6080/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      // 添加Bearer token到请求头
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error: AxiosError<{ detail: string }>) => {
    if (error.response) {
      const { status, data } = error.response
      const url = error.config?.url || ''
      const method = error.config?.method || ''
      
      // 特殊处理：以下接口返回404时不显示错误（表示没有数据）
      const isProjectAccountQuery = url.includes('/v1/project/account') && method === 'get'
      const isProjectWalletQuery = url.includes('/v1/project/wallet') && method === 'get'
      const isProjectInfoQuery = url.includes('/v1/project/info') && method === 'get'
      const isUserTokenQuery = url.includes('/v1/user/token') && method === 'get'
      const isUserQuery = url.includes('/v1/user/user') && method === 'get'
      const isMailQuery = url.includes('/v1/mail/info') && method === 'get'
      const isServerQuery = url.includes('/v1/server/info') && method === 'get'
      const isServerGroupQuery = url.includes('/v1/server/group') && method === 'get'
      const isServerAccountQuery = url.includes('/v1/server/account') && method === 'get'
      const isServerCountryQuery = url.includes('/v1/server/country') && method === 'get'
      const is404 = status === 404
      
      // 特殊处理：登录接口的错误由组件自己处理，不在这里显示
      const isLoginRequest = url.includes('/v1/user/auth/login')
      
      if (is404 && (
        isProjectAccountQuery || 
        isProjectWalletQuery || 
        isProjectInfoQuery ||
        isUserTokenQuery || 
        isUserQuery ||
        isMailQuery || 
        isServerQuery || 
        isServerGroupQuery ||
        isServerAccountQuery ||
        isServerCountryQuery
      )) {
        // 这些查询接口404不显示错误提示，静默处理
        return Promise.reject(error)
      }
      
      // 登录接口的错误不在这里显示，由登录组件处理
      if (isLoginRequest) {
        return Promise.reject(error)
      }
      
      switch (status) {
        case 401:
          // Token过期或无效
          message.error('登录已过期，请重新登录')
          // 清除token和用户信息
          localStorage.removeItem('access_token')
          localStorage.removeItem('user-storage')
          // 跳转到登录页
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          break
        case 403:
          message.error('没有权限访问')
          break
        case 404:
          // 显示后端返回的详细错误信息，或默认提示
          const detail404 = data?.detail || '请求的资源不存在'
          message.error(detail404)
          break
        case 500:
          // 显示后端返回的详细错误信息，或默认提示
          const detail500 = data?.detail || '服务器错误，请稍后重试'
          message.error(detail500)
          break
        default:
          // 其他错误显示通用提示
          const detailDefault = data?.detail || `请求失败 (${status})`
          message.error(detailDefault)
          break
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      message.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default api
