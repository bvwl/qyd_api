import api from './index'
import type { ApiResponse, PaginationParams } from '@/types'

// XUI 服务器接口
export interface XuiServer {
  id: string
  name: string
  host: string
  domain?: string
  port: number
  username: string
  password?: string
  is_ssl: boolean
  web_path: string
  status: number
  cert_file?: string
  key_file?: string
  remark?: string
  create_time: string
  update_time: string
}

// XUI 入站接口
export interface XuiInbound {
  id: string
  server_id: string
  inbound_id: number
  listen_host: string
  listen_port: number
  protocol: number
  remark?: string
  status: number
  default_username: string
  default_password?: string
  create_time: string
  update_time: string
}

// XUI 账号接口
export interface XuiAccount {
  id: string
  email: string
  uuid: string
  enable: boolean
  flow: string
  limit_ip: number
  total_gb: number
  expire_time: number
  up: number
  down: number
  inbound_ids: number[]
}

// ==================== XUI 服务器 API ====================

export const getXuiServerList = (params?: PaginationParams & { 
  name?: string
  host?: string
  domain?: string
  status?: number
  create_time_start?: string
  create_time_end?: string
}) => {
  return api.get<any, ApiResponse<XuiServer>>('/v1/xui/server', { params })
}

export const getXuiServerDetail = (id: string) => {
  return api.get<any, XuiServer>(`/v1/xui/server/${id}`)
}

export const createXuiServer = (data: Partial<XuiServer>) => {
  return api.post<any, XuiServer>('/v1/xui/server', data)
}

export const updateXuiServer = (id: string, data: Partial<XuiServer>) => {
  return api.put<any, XuiServer>(`/v1/xui/server/${id}`, data)
}

export const deleteXuiServer = (id: string) => {
  return api.delete(`/v1/xui/server/${id}`)
}

// ==================== XUI 入站 API ====================

export const getXuiInboundList = (params?: PaginationParams & { 
  server_id?: string
  listen_port?: number
  protocol?: number
  status?: number
  create_time_start?: string
  create_time_end?: string
}) => {
  return api.get<any, ApiResponse<XuiInbound>>('/v1/xui/inbound', { params })
}

export const getXuiInboundDetail = (id: string) => {
  return api.get<any, XuiInbound>(`/v1/xui/inbound/${id}`)
}

export const createXuiInbound = (data: Partial<XuiInbound>) => {
  return api.post<any, XuiInbound>('/v1/xui/inbound', data)
}

export const updateXuiInbound = (id: string, data: Partial<XuiInbound>) => {
  return api.put<any, XuiInbound>(`/v1/xui/inbound/${id}`, data)
}

export const deleteXuiInbound = (id: string) => {
  return api.delete(`/v1/xui/inbound/${id}`)
}

// ==================== XUI 账号管理 API ====================

export const getXuiAccountsByInbound = (inboundId: string) => {
  return api.get<any, { items: XuiAccount[] }>(`/v1/xui/account/inbound/${inboundId}`)
}

export const addAccountToInbound = (inboundId: string, accountId: string) => {
  return api.post(`/v1/xui/account/inbound/${inboundId}/account/${accountId}`)
}

export const removeAccountFromInbound = (inboundId: string, accountId: string) => {
  return api.delete(`/v1/xui/account/inbound/${inboundId}/account/${accountId}`)
}

// ==================== XUI 操作 API ====================

// 同步入站配置
export const syncXuiInbounds = (serverId: string) => {
  return api.post<any, {
    code: number
    message: string
    data: {
      server_id: string
      server_name: string
      inbound_count: number
      server_info_count: number
      created: number
      updated: number
      skipped: number
    }
  }>(`/v1/xui/operation/sync-inbounds/${serverId}`)
}

// 测试服务器连接
export const testXuiConnection = (serverId: string) => {
  return api.post<any, {
    code: number
    message: string
    data: {
      success: boolean
      message: string
    }
  }>(`/v1/xui/operation/test-connection/${serverId}`)
}


// ==================== XUI 操作日志 API ====================

export interface XuiOperationLog {
  id: string
  inbound_id: string
  inbound_info: string
  account_id: string
  account_username: string
  error_message: string
  retry_count: number
  is_resolved: boolean
  create_time: string
}

// 获取失败的操作日志
export const getFailedLogs = (params?: PaginationParams & {
  inbound_id?: string
}) => {
  return api.get<any, ApiResponse<XuiOperationLog>>('/v1/xui/account/failed-logs', { params })
}

// 重试失败的操作
export const retryFailedLog = (logId: string) => {
  return api.post<any, {
    code: number
    message: string
    data: {
      success: boolean
      message: string
      result?: any
    }
  }>(`/v1/xui/account/retry-failed/${logId}`)
}

// 批量重试失败的操作
export const batchRetryFailedLogs = (inboundId?: string) => {
  return api.post<any, {
    code: number
    message: string
    data: {
      total: number
      success: number
      failed: number
    }
  }>('/v1/xui/account/batch-retry-failed', null, {
    params: inboundId ? { inbound_id: inboundId } : undefined
  })
}

// 批量添加账号到入站
export const batchAddAccountsToInbound = (inboundId: string, accountIds: string[]) => {
  return api.post<any, {
    code: number
    message: string
    data: {
      total: number
      success: number
      failed: number
      success_list: Array<{ account_id: string; username: string }>
      failed_list: Array<{ account_id: string; username: string; error: string }>
    }
  }>('/v1/xui/account/batch-add', {
    inbound_id: inboundId,
    account_ids: accountIds
  })
}

// 将账号添加到所有入站
export const addAccountToAllInbounds = (accountId: string) => {
  return api.post<any, {
    code: number
    message: string
    data: {
      total: number
      success: number
      failed: number
      failed_list: Array<{ inbound_id: string; inbound_info: string; error: string }>
      is_all_added: boolean
    }
  }>(`/v1/xui/account/add-to-all-inbounds/${accountId}`)
}

// 从所有入站删除账号
export const removeAccountFromAllInbounds = (accountId: string) => {
  return api.delete<any, {
    code: number
    message: string
    data: {
      total: number
      success: number
      failed: number
      failed_list: Array<{ inbound_id: string; inbound_info: string; error: string }>
      is_all_removed: boolean
    }
  }>(`/v1/xui/account/remove-from-all-inbounds/${accountId}`)
}
