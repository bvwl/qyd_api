import { ReactNode } from 'react'
import { usePermission } from '@/hooks/usePermission'

interface PermissionProps {
  /**
   * 需要的权限标识
   */
  permission?: string
  
  /**
   * 需要的权限标识数组（满足任意一个即可）
   */
  anyPermissions?: string[]
  
  /**
   * 需要的权限标识数组（需要全部满足）
   */
  allPermissions?: string[]
  
  /**
   * 有权限时显示的内容
   */
  children: ReactNode
  
  /**
   * 无权限时显示的内容（可选）
   */
  fallback?: ReactNode
}

/**
 * 权限控制组件
 * 根据用户权限决定是否显示子组件
 * 
 * @example
 * // 单个权限
 * <Permission permission="user:create">
 *   <Button>创建用户</Button>
 * </Permission>
 * 
 * @example
 * // 任意权限
 * <Permission anyPermissions={["user:create", "user:edit"]}>
 *   <Button>操作</Button>
 * </Permission>
 * 
 * @example
 * // 所有权限
 * <Permission allPermissions={["user:view", "user:edit"]}>
 *   <Button>编辑</Button>
 * </Permission>
 */
export const Permission = ({
  permission,
  anyPermissions,
  allPermissions,
  children,
  fallback = null,
}: PermissionProps) => {
  const { hasPermission, hasAnyPermission, hasAllPermissions, loading } = usePermission()

  // 加载中不显示
  if (loading) {
    return null
  }

  // 检查权限
  let hasAccess = true

  if (permission) {
    hasAccess = hasPermission(permission)
  } else if (anyPermissions && anyPermissions.length > 0) {
    hasAccess = hasAnyPermission(anyPermissions)
  } else if (allPermissions && allPermissions.length > 0) {
    hasAccess = hasAllPermissions(allPermissions)
  }

  return hasAccess ? <>{children}</> : <>{fallback}</>
}

export default Permission
