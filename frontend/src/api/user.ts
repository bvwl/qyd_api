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
export const getUserList = (params: PaginationParams & { email?: string; nickname?: string; status?: number }) => {
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

// 角色管理
export const getRoleList = (params?: PaginationParams) => {
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
export const getRouteList = (params?: PaginationParams) => {
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

// Token 管理
export const getTokenList = (params?: PaginationParams & { user_id?: string; status?: number }) => {
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

// 日志管理
export const getLogList = (params?: PaginationParams & { user_id?: string; action?: number }) => {
  return api.get<any, ApiResponse<UserLog>>('/v1/user/log', { params })
}

export const getLogDetail = (id: string) => {
  return api.get<any, UserLog>(`/v1/user/log/${id}`)
}
