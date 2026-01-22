import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { login as loginApi, getUserDetail } from '@/api/user'

interface UserState {
  token: string
  userInfo: User | null
  permissions: string[]
  isLoggedIn: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchUserInfo: () => Promise<void>
  setUserInfo: (userInfo: User) => void
  hasPermission: (permission: string) => boolean
  checkTokenValid: () => boolean
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      token: '',
      userInfo: null,
      permissions: [],
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
        
        // 提取用户权限
        if (res.user.roles) {
          const permissions: string[] = []
          res.user.roles.forEach(role => {
            // 添加角色代码作为权限
            permissions.push(role.code)
            
            // 添加路由权限
            if (role.routes) {
              role.routes.forEach(route => {
                permissions.push(route.name)
              })
            }
          })
          set({ permissions })
        }
      },

      logout: () => {
        // 清除所有认证信息
        localStorage.removeItem('access_token')
        localStorage.removeItem('user-storage')
        
        set({
          token: '',
          userInfo: null,
          permissions: [],
          isLoggedIn: false,
        })
      },

      fetchUserInfo: async () => {
        const { userInfo } = get()
        if (userInfo) {
          try {
            const user = await getUserDetail(userInfo.id)
            set({ userInfo: user })
            
            // 更新权限
            if (user.roles) {
              const permissions: string[] = []
              user.roles.forEach(role => {
                permissions.push(role.code)
                if (role.routes) {
                  role.routes.forEach(route => {
                    permissions.push(route.name)
                  })
                }
              })
              set({ permissions })
            }
          } catch (error) {
            console.error('获取用户信息失败:', error)
            // 如果获取失败（可能token过期），清除登录状态
            get().logout()
          }
        }
      },

      setUserInfo: (userInfo: User) => {
        set({ userInfo })
      },

      hasPermission: (permission: string) => {
        const { permissions, userInfo } = get()
        
        // 管理员拥有所有权限
        if (userInfo?.roles?.some(role => role.code === 'ADMIN')) {
          return true
        }
        
        return permissions.includes(permission)
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
        isLoggedIn: state.isLoggedIn,
      }),
    }
  )
)
