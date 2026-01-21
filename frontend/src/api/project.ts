import api from './index'
import type { Project, ProjectAccount, ProjectWallet, ProjectBalance, ApiResponse, PaginationParams } from '@/types'

// 项目信息
export const getProjectList = (params?: PaginationParams & { name?: string; status?: number }) => {
  return api.get<any, ApiResponse<Project>>('/v1/project/info', { params })
}

export const getProjectDetail = (id: string) => {
  return api.get<any, Project>(`/v1/project/info/${id}`)
}

export const createProject = (data: Partial<Project> & { user_ids?: string[] }) => {
  return api.post<any, Project>('/v1/project/info', data)
}

export const updateProject = (id: string, data: Partial<Project> & { user_ids?: string[] }) => {
  return api.put<any, Project>(`/v1/project/info/${id}`, data)
}

export const deleteProject = (id: string) => {
  return api.delete(`/v1/project/info/${id}`)
}

// 项目账号
export const getProjectAccountList = (params?: PaginationParams & { 
  project_id?: string
  status?: number
  account_type?: number
  account?: string
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<ProjectAccount>>('/v1/project/account', { params })
}

export const getProjectAccountDetail = (id: string) => {
  return api.get<any, ProjectAccount>(`/v1/project/account/${id}`)
}

export const createProjectAccount = (data: Partial<ProjectAccount>) => {
  return api.post<any, ProjectAccount>('/v1/project/account', data)
}

export const updateProjectAccount = (id: string, data: Partial<ProjectAccount>) => {
  return api.put<any, ProjectAccount>(`/v1/project/account/${id}`, data)
}

export const deleteProjectAccount = (id: string) => {
  return api.delete(`/v1/project/account/${id}`)
}

// 项目钱包
export const getProjectWalletList = (params?: PaginationParams & { 
  chain?: string
  project_id?: string
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<ProjectWallet>>('/v1/project/wallet', { params })
}

export const getProjectWalletDetail = (id: string) => {
  return api.get<any, ProjectWallet>(`/v1/project/wallet/${id}`)
}

export const createProjectWallet = (data: Partial<ProjectWallet>) => {
  return api.post<any, ProjectWallet>('/v1/project/wallet', data)
}

export const updateProjectWallet = (id: string, data: Partial<ProjectWallet>) => {
  return api.put<any, ProjectWallet>(`/v1/project/wallet/${id}`, data)
}

export const deleteProjectWallet = (id: string) => {
  return api.delete(`/v1/project/wallet/${id}`)
}

// 项目余额
export const getProjectBalanceList = (params?: PaginationParams & { account_id?: string }) => {
  return api.get<any, ApiResponse<ProjectBalance>>('/v1/project/balance', { params })
}

export const getProjectBalanceDetail = (id: string) => {
  return api.get<any, ProjectBalance>(`/v1/project/balance/${id}`)
}

export const createProjectBalance = (data: Partial<ProjectBalance>) => {
  return api.post<any, ProjectBalance>('/v1/project/balance', data)
}

export const updateProjectBalance = (id: string, data: Partial<ProjectBalance>) => {
  return api.put<any, ProjectBalance>(`/v1/project/balance/${id}`, data)
}

export const deleteProjectBalance = (id: string) => {
  return api.delete(`/v1/project/balance/${id}`)
}
