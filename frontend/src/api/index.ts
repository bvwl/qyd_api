import axios, { AxiosError } from 'axios'
import { message } from 'antd'

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
