import axios, { AxiosError } from 'axios'
import { message } from 'antd'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:6080',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
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
          message.error('未授权，请重新登录')
          localStorage.removeItem('access_token')
          window.location.href = '/login'
          break
        case 403:
          message.error('没有权限访问')
          break
        case 404:
          // 404 通常表示无数据，不显示错误
          break
        case 500:
          message.error('服务器错误')
          break
        default:
          message.error(data?.detail || '请求失败')
      }
    } else {
      message.error('网络错误，请检查网络连接')
    }
    
    return Promise.reject(error)
  }
)

export default api
