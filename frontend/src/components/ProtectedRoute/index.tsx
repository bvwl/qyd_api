import { Navigate } from 'react-router-dom'
import { useUserStore } from '@/store/useUserStore'
import { TokenManager } from '@/utils/token'
import { useEffect, useCallback } from 'react'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { token, isLoggedIn, logout } = useUserStore()
  
  // 使用 useCallback 避免函数重新创建导致的无限循环
  const checkToken = useCallback(() => {
    if (token && isLoggedIn) {
      // 检查token是否过期
      if (TokenManager.isTokenExpired(token)) {
        console.warn('Token已过期，请重新登录')
        logout()
        return false
      }
      
      // 检查token是否存在于localStorage
      const storedToken = localStorage.getItem('access_token')
      if (!storedToken || token !== storedToken) {
        console.warn('Token验证失败，请重新登录')
        logout()
        return false
      }
    }
    return true
  }, [token, isLoggedIn, logout])
  
  useEffect(() => {
    checkToken()
  }, [checkToken])
  
  // 检查是否已登录且token有效
  if (!token || !isLoggedIn || !TokenManager.hasToken()) {
    return <Navigate to="/login" replace />
  }
  
  // 检查token是否过期
  if (TokenManager.isTokenExpired(token)) {
    logout()
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}
