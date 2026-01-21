import { Navigate } from 'react-router-dom'
import { useUserStore } from '@/store/useUserStore'
import { TokenManager } from '@/utils/token'
import { useEffect } from 'react'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { token, isLoggedIn, checkTokenValid, logout } = useUserStore()
  
  useEffect(() => {
    // 检查token是否有效
    if (token && isLoggedIn) {
      // 检查token是否过期
      if (TokenManager.isTokenExpired(token)) {
        console.warn('Token已过期，请重新登录')
        logout()
      } else if (!checkTokenValid()) {
        console.warn('Token验证失败，请重新登录')
        logout()
      }
    }
  }, [token, isLoggedIn, checkTokenValid, logout])
  
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
