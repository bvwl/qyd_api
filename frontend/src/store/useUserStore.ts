import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { login as loginApi, getUserDetail } from '@/api/user'
import { getUserMenus, getUserPermissions } from '@/api/rbac'
import type { Menu } from '@/api/rbac'

interface UserState {
  token: string
  userInfo: User | null
  permissions: string[]
  menus: Menu[]
  isLoggedIn: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchUserInfo: () => Promise<void>
  fetchUserPermissions: () => Promise<void>
  fetchUserMenus: () => Promise<void>
  setUserInfo: (userInfo: User) => void
  hasPermission: (permission: string | string[]) => boolean
  hasAnyPermission: (permissions: string[]) => boolean
  hasAllPermissions: (permissions: string[]) => boolean
  checkTokenValid: () => boolean
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      token: '',
      userInfo: null,
      permissions: [],
      menus: [],
      isLoggedIn: false,

      login: async (email: string, password: string) => {
        const res = await loginApi({ email, password })
        
        // 保存token到localStorage和store
        const token = res.access_token
        localStorage.setItem('access_token', token)
        
        set({
          token,
          userInfo: res.user,
          isLoggedIn: true,
        })
        
        // 获取用户权限和菜单
        await get().fetchUserPermissions()
        await get().fetchUserMenus()
      },

      logout: () => {
        // 清除所有认证信息
        localStorage.removeItem('access_token')
        localStorage.removeItem('user-storage')
        
        set({
          token: '',
          userInfo: null,
          permissions: [],
          menus: [],
          isLoggedIn: false,
        })
      },

      fetchUserInfo: async () => {
        const { userInfo } = get()
        if (userInfo) {
          try {
            const user = await getUserDetail(userInfo.id)
            set({ userInfo: user })
          } catch (error) {
            console.error('获取用户信息失败:', error)
            // 如果获取失败（可能token过期），清除登录状态
            get().logout()
          }
        }
      },

      fetchUserPermissions: async () => {
        try {
          const res = await getUserPermissions()
          set({ permissions: res.data })
        } catch (error) {
          console.error('获取用户权限失败:', error)
        }
      },

      fetchUserMenus: async () => {
        try {
          const res = await getUserMenus()
          set({ menus: res.data })
        } catch (error) {
          console.error('获取用户菜单失败:', error)
        }
      },

      setUserInfo: (userInfo: User) => {
        set({ userInfo })
      },

      hasPermission: (permission: string | string[]) => {
        const { permissions, userInfo } = get()
        
        // 管理员拥有所有权限
        if (userInfo?.roles?.some(role => role.code === 'ADMIN')) {
          return true
        }
        
        // 如果 permissions 未初始化，返回 false
        if (!permissions || !Array.isArray(permissions)) {
          return false
        }
        
        // 支持单个权限或权限数组
        if (Array.isArray(permission)) {
          // 检查是否有任何一个权限或角色匹配
          return permission.some(p => {
            // 先检查是否是角色代码
            if (userInfo?.roles?.some(role => role.code === p)) {
              return true
            }
            // 再检查是否是权限字符串
            return permissions.includes(p)
          })
        }
        
        // 单个权限：先检查角色，再检查权限
        if (userInfo?.roles?.some(role => role.code === permission)) {
          return true
        }
        
        return permissions.includes(permission)
      },

      hasAnyPermission: (permissionList: string[]) => {
        const { permissions, userInfo } = get()
        
        // 管理员拥有所有权限
        if (userInfo?.roles?.some(role => role.code === 'ADMIN')) {
          return true
        }
        
        // 如果 permissions 未初始化，返回 false
        if (!permissions || !Array.isArray(permissions)) {
          return false
        }
        
        return permissionList.some(p => permissions.includes(p))
      },

      hasAllPermissions: (permissionList: string[]) => {
        const { permissions, userInfo } = get()
        
        // 管理员拥有所有权限
        if (userInfo?.roles?.some(role => role.code === 'ADMIN')) {
          return true
        }
        
        // 如果 permissions 未初始化，返回 false
        if (!permissions || !Array.isArray(permissions)) {
          return false
        }
        
        return permissionList.every(p => permissions.includes(p))
      },

      checkTokenValid: () => {
        const { token, isLoggedIn } = get()
        const storedToken = localStorage.getItem('access_token')
        
        // 检查token是否存在且一致
        if (!token || !storedToken || token !== storedToken || !isLoggedIn) {
          return false
        }
        
        return true
      },
    }),
    {
      name: 'user-storage',
      partialize: (state) => ({
        token: state.token,
        userInfo: state.userInfo,
        permissions: state.permissions,
        menus: state.menus,
        isLoggedIn: state.isLoggedIn,
      }),
    }
  )
)
