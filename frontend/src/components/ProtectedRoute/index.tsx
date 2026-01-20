import { Navigate } from 'react-router-dom'
import { useUserStore } from '@/store/useUserStore'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const token = useUserStore((state) => state.token)
  
  if (!token) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}
