import api from './index'
import type { Project, ProjectAccount, ProjectWallet, ApiResponse, PaginationParams } from '@/types'

// 项目信息
export const getProjectList = (params?: PaginationParams & { 
  name?: string
  status?: number
  user_id?: string
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
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

// 项目账号（包含余额字段）
export const getProjectAccountList = (params?: PaginationParams & { 
  project_id?: string
  status?: number
  account_type?: number
  account?: string
  order_by?: string
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
  public_key?: string
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

export const upsertProjectWallet = (data: Partial<ProjectWallet>) => {
  return api.post<any, ProjectWallet>('/v1/project/wallet/upsert', data)
}

// 批量创建钱包
export const batchCreateWallet = (data: {
  project_name: string
  chain: string
  count: number
  remark?: string
}) => {
  return api.post<any, {
    message: string
    count: number
    items: ProjectWallet[]
  }>('/v1/project/wallet/batch', data)
}

// 项目账号统计
export const getProjectAccountStats = (params: {
  project_id: string
  account?: string
  status?: number
  account_type?: number
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, {
    code: number
    message: string
    data: {
      total_count: number
      balance: {
        max: number
        min: number
        avg: number
        sum: number
      }
      variable: {
        max: number
        min: number
        avg: number
        sum: number
      }
    }
  }>('/v1/project/account/stats', { params })
}

// 导出所有项目统计数据
export const exportAllProjectStats = () => {
  return api.get('/v1/project/account/export-all-stats', {
    responseType: 'blob'
  })
}

// 导出当天所有项目统计数据
export const exportTodayProjectStats = () => {
  return api.get('/v1/project/account/export-today-stats', {
    responseType: 'blob'
  })
}

// 项目统计 - 仪表盘数据
export const getProjectStatsForDashboard = (params: { 
  days: number
  project_ids?: string  // 逗号分隔的项目ID列表，不传则返回总和
}) => {
  return api.get<any, {
    code: number
    message: string
    data: Array<{
      project_id: string
      project_name: string
      dates: string[]
      counts: number[]
    }>
  }>('/v1/project/stats/dashboard', { params })
}

// 获取可用项目列表（用于统计图表）
export const getAvailableProjectsForStats = () => {
  return api.get<any, {
    code: number
    message: string
    data: Array<{
      id: string
      name: string
    }>
  }>('/v1/project/stats/projects')
}

// 获取项目今天的更新数量
export const getProjectTodayCount = (projectId: string) => {
  return api.get<any, {
    code: number
    message: string
    data: {
      project_id: string
      today_count: number
    }
  }>(`/v1/project/stats/project/${projectId}/today`)
}

// 清除统计缓存（仅管理员）
export const clearStatsCache = (projectId?: string) => {
  return api.post<any, {
    code: number
    message: string
  }>('/v1/project/stats/cache/clear', null, {
    params: projectId ? { project_id: projectId } : undefined
  })
}

// 手动同步统计数据（仅管理员）
export const syncStatsData = (days: number = 1) => {
  return api.post<any, {
    code: number
    message: string
    data: {
      days: number
      synced_count: number
    }
  }>('/v1/project/stats/sync', null, {
    params: { days }
  })
}

// 项目文件管理
export const uploadProjectFile = (projectId: string, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/v1/project/file/${projectId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export const getProjectFiles = (projectId: string) => {
  return api.get<any, { message: string; project_name: string; files: Array<{ name: string; size: number; modified_time: number }>; count: number }>(`/v1/project/file/${projectId}/files`)
}

export const downloadProjectFile = (projectId: string, filename: string) => {
  return api.get(`/v1/project/file/${projectId}/download/${filename}`, {
    responseType: 'blob',
  })
}

export const deleteProjectFile = (projectId: string, filename: string) => {
  return api.delete(`/v1/project/file/${projectId}/delete/${filename}`)
}
