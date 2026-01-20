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
  hasPermission: (permission: string) => boolean
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
        set({
          token: res.access_token,
          userInfo: res.user,
          isLoggedIn: true,
        })
        localStorage.setItem('access_token', res.access_token)
        
        // 获取用户权限
        if (res.user.roles) {
          const permissions: string[] = []
          res.user.roles.forEach(role => {
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
        set({
          token: '',
          userInfo: null,
          permissions: [],
          isLoggedIn: false,
        })
        localStorage.removeItem('access_token')
      },

      fetchUserInfo: async () => {
        const { userInfo } = get()
        if (userInfo) {
          const user = await getUserDetail(userInfo.id)
          set({ userInfo: user })
          
          // 更新权限
          if (user.roles) {
            const permissions: string[] = []
            user.roles.forEach(role => {
              if (role.routes) {
                role.routes.forEach(route => {
                  permissions.push(route.name)
                })
              }
            })
            set({ permissions })
          }
        }
      },

      hasPermission: (permission: string) => {
        const { permissions } = get()
        return permissions.includes(permission)
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
