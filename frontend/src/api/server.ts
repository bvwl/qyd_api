import api from './index'
import type { ServerCountry, ServerGroup, ServerInfo, ServerAccount, ApiResponse, PaginationParams } from '@/types'

// 国家信息
export const getCountryList = (params?: PaginationParams & { 
  name?: string
  short_name?: string
  status?: number
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<ServerCountry>>('/v1/server/country', { params })
}

export const getCountryDetail = (id: string) => {
  return api.get<any, ServerCountry>(`/v1/server/country/${id}`)
}

export const createCountry = (data: Partial<ServerCountry>) => {
  return api.post<any, ServerCountry>('/v1/server/country', data)
}

export const updateCountry = (id: string, data: Partial<ServerCountry>) => {
  return api.put<any, ServerCountry>(`/v1/server/country/${id}`, data)
}

export const deleteCountry = (id: string) => {
  return api.delete(`/v1/server/country/${id}`)
}

// 分组信息
export const getGroupList = (params?: PaginationParams & { 
  country_id?: string
  status?: number
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<ServerGroup>>('/v1/server/group', { params })
}

export const getGroupDetail = (id: string) => {
  return api.get<any, ServerGroup>(`/v1/server/group/${id}`)
}

export const createGroup = (data: Partial<ServerGroup>) => {
  return api.post<any, ServerGroup>('/v1/server/group', data)
}

export const updateGroup = (id: string, data: Partial<ServerGroup>) => {
  return api.put<any, ServerGroup>(`/v1/server/group/${id}`, data)
}

export const deleteGroup = (id: string) => {
  return api.delete(`/v1/server/group/${id}`)
}

// 服务器信息
export const getServerList = (params?: PaginationParams & { 
  host?: string
  group_id?: string
  status?: number
  is_sale?: number
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<ServerInfo>>('/v1/server/info', { params })
}

export const getServerDetail = (id: string) => {
  return api.get<any, ServerInfo>(`/v1/server/info/${id}`)
}

export const createServer = (data: Partial<ServerInfo>) => {
  return api.post<any, ServerInfo>('/v1/server/info', data)
}

export const updateServer = (id: string, data: Partial<ServerInfo>) => {
  return api.put<any, ServerInfo>(`/v1/server/info/${id}`, data)
}

export const deleteServer = (id: string) => {
  return api.delete(`/v1/server/info/${id}`)
}

// 服务器账号
export const getServerAccountList = (params?: PaginationParams & { 
  user_id?: string
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<ServerAccount>>('/v1/server/account', { params })
}

export const getServerAccountDetail = (id: string) => {
  return api.get<any, ServerAccount>(`/v1/server/account/${id}`)
}

export const createServerAccount = (data: Partial<ServerAccount>) => {
  return api.post<any, ServerAccount>('/v1/server/account', data)
}

export const updateServerAccount = (id: string, data: Partial<ServerAccount>) => {
  return api.put<any, ServerAccount>(`/v1/server/account/${id}`, data)
}

export const deleteServerAccount = (id: string) => {
  return api.delete(`/v1/server/account/${id}`)
}
