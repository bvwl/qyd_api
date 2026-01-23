import api from './index'
import type { User, Role, Route, UserToken, UserLog, ApiResponse, PaginationParams, LoginResponse } from '@/types'

// 用户认证
export const login = (data: { email: string; password: string }) => {
  return api.post<any, LoginResponse>('/v1/user/auth/login', data)
}

export const register = (data: { email: string; password: string; nickname: string }) => {
  return api.post<any, LoginResponse>('/v1/user/auth/register', data)
}

// 用户管理
export const getUserList = (params: PaginationParams & { 
  email?: string
  nickname?: string
  status?: number
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<User>>('/v1/user/user', { params })
}

export const getUserDetail = (id: string) => {
  return api.get<any, User>(`/v1/user/user/${id}`)
}

export const createUser = (data: Partial<User> & { role_ids?: string[] }) => {
  return api.post<any, User>('/v1/user/user', data)
}

export const updateUser = (id: string, data: Partial<User> & { role_ids?: string[] }) => {
  return api.put<any, User>(`/v1/user/user/${id}`, data)
}

export const deleteUser = (id: string) => {
  return api.delete(`/v1/user/user/${id}`)
}

// 用户角色管理
export const getUserRoles = (userId: string) => {
  return api.get<any, Role[]>(`/v1/user/${userId}/roles`)
}

export const assignUserRoles = (userId: string, roleCodes: string[]) => {
  return api.put<any, User>(`/v1/user/${userId}/roles`, { role_codes: roleCodes })
}

export const addUserRole = (userId: string, roleCode: string) => {
  return api.post<any, User>(`/v1/user/${userId}/roles/${roleCode}`)
}

export const removeUserRole = (userId: string, roleCode: string) => {
  return api.delete<any, User>(`/v1/user/${userId}/roles/${roleCode}`)
}

// 角色管理
export const getRoleList = (params?: PaginationParams & { 
  name?: string
  code?: string
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<Role>>('/v1/user/role', { params })
}

export const getRoleDetail = (id: string) => {
  return api.get<any, Role>(`/v1/user/role/${id}`)
}

export const createRole = (data: Partial<Role> & { route_ids?: string[] }) => {
  return api.post<any, Role>('/v1/user/role', data)
}

export const updateRole = (id: string, data: Partial<Role> & { route_ids?: string[] }) => {
  return api.put<any, Role>(`/v1/user/role/${id}`, data)
}

export const deleteRole = (id: string) => {
  return api.delete(`/v1/user/role/${id}`)
}

// 路由管理
export const getRouteList = (params?: PaginationParams & {
  name?: string
  path?: string
  status?: number
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<Route>>('/v1/user/route', { params })
}

export const getRouteDetail = (id: string) => {
  return api.get<any, Route>(`/v1/user/route/${id}`)
}

export const createRoute = (data: Partial<Route>) => {
  return api.post<any, Route>('/v1/user/route', data)
}

export const updateRoute = (id: string, data: Partial<Route>) => {
  return api.put<any, Route>(`/v1/user/route/${id}`, data)
}

export const deleteRoute = (id: string) => {
  return api.delete(`/v1/user/route/${id}`)
}

// 获取路由树
export const getRouteTree = (params?: { status?: number; route_type?: number }) => {
  return api.get<any, Route[]>('/v1/user/route/tree', { params })
}

// 获取当前用户的路由权限
export const getUserRoutes = () => {
  return api.get<any, Route[]>('/v1/user/route/user-routes')
}

// 获取角色的路由权限
export const getRoleRoutes = (roleId: string) => {
  return api.get<any, { tree: Route[]; checked_keys: string[] }>(`/v1/user/role/${roleId}/routes`)
}

// 设置角色的路由权限
export const setRoleRoutes = (roleId: string, routeIds: string[]) => {
  return api.post(`/v1/user/role/${roleId}/routes`, routeIds)
}

// Token 管理
export const getTokenList = (params?: PaginationParams & { 
  user_id?: string
  status?: number
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<UserToken>>('/v1/user/token', { params })
}

export const getTokenDetail = (id: string) => {
  return api.get<any, UserToken>(`/v1/user/token/${id}`)
}

export const createToken = (data: Partial<UserToken>) => {
  return api.post<any, UserToken>('/v1/user/token', data)
}

export const updateToken = (id: string, data: Partial<UserToken>) => {
  return api.put<any, UserToken>(`/v1/user/token/${id}`, data)
}

export const deleteToken = (id: string) => {
  return api.delete(`/v1/user/token/${id}`)
}

// 生成新Token
export const generateToken = () => {
  return api.post<any, UserToken>('/v1/user/token/generate')
}

// 日志管理
export const getLogList = (params?: PaginationParams & { 
  user_id?: string
  action?: number
  create_time_start?: string
  create_time_end?: string
}) => {
  return api.get<any, ApiResponse<UserLog>>('/v1/user/log', { params })
}

export const getLogDetail = (id: string) => {
  return api.get<any, UserLog>(`/v1/user/log/${id}`)
}
