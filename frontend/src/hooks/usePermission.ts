import { useEffect, useState } from 'react'
import { getUserRoutes } from '@/api/user'
import type { Route } from '@/types'

interface PermissionState {
  routes: Route[]
  permissions: Set<string>
  loading: boolean
}

/**
 * 权限管理 Hook
 * 用于检查用户是否有某个权限
 */
export const usePermission = () => {
  const [state, setState] = useState<PermissionState>({
    routes: [],
    permissions: new Set(),
    loading: true,
  })

  useEffect(() => {
    loadUserPermissions()
  }, [])

  const loadUserPermissions = async () => {
    try {
      const routes = await getUserRoutes()
      const permissions = new Set<string>()
      
      // 递归收集所有权限标识
      const collectPermissions = (routeList: Route[]) => {
        routeList.forEach(route => {
          if (route.permission) {
            permissions.add(route.permission)
          }
          if (route.children && route.children.length > 0) {
            collectPermissions(route.children)
          }
        })
      }
      
      collectPermissions(routes)
      
      setState({
        routes,
        permissions,
        loading: false,
      })
    } catch (error) {
      console.error('加载用户权限失败:', error)
      setState(prev => ({ ...prev, loading: false }))
    }
  }

  /**
   * 检查是否有某个权限
   * @param permission 权限标识，如 'user:create'
   */
  const hasPermission = (permission: string): boolean => {
    return state.permissions.has(permission)
  }

  /**
   * 检查是否有任意一个权限
   * @param permissions 权限标识数组
   */
  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(p => state.permissions.has(p))
  }

  /**
   * 检查是否有所有权限
   * @param permissions 权限标识数组
   */
  const hasAllPermissions = (permissions: string[]): boolean => {
    return permissions.every(p => state.permissions.has(p))
  }

  return {
    routes: state.routes,
    permissions: state.permissions,
    loading: state.loading,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    reload: loadUserPermissions,
  }
}
