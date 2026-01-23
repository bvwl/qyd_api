import { useUserStore } from '@/store/useUserStore'

/**
 * 权限管理 Hook (RBAC v2)
 * 用于检查用户是否有某个权限
 */
export const usePermission = () => {
  const { permissions, userInfo, hasPermission, hasAnyPermission, hasAllPermissions } = useUserStore()

  /**
   * 检查是否是管理员
   */
  const isAdmin = (): boolean => {
    return userInfo?.roles?.some(role => role.code === 'ADMIN') || false
  }

  /**
   * 检查是否有某个权限
   * @param permission 权限标识，如 'user:create' 或权限数组
   */
  const checkPermission = (permission: string | string[]): boolean => {
    // 管理员拥有所有权限
    if (isAdmin()) {
      return true
    }

    return hasPermission(permission)
  }

  /**
   * 检查是否有任意一个权限
   * @param permissionList 权限标识数组
   */
  const checkAnyPermission = (permissionList: string[]): boolean => {
    // 管理员拥有所有权限
    if (isAdmin()) {
      return true
    }

    return hasAnyPermission(permissionList)
  }

  /**
   * 检查是否有所有权限
   * @param permissionList 权限标识数组
   */
  const checkAllPermissions = (permissionList: string[]): boolean => {
    // 管理员拥有所有权限
    if (isAdmin()) {
      return true
    }

    return hasAllPermissions(permissionList)
  }

  return {
    permissions,
    isAdmin,
    hasPermission: checkPermission,
    hasAnyPermission: checkAnyPermission,
    hasAllPermissions: checkAllPermissions,
  }
}
