import api from './index'
import type { EmailInfo, ApiResponse, PaginationParams, EmailType } from '@/types'

// 邮箱信息
export const getEmailList = (params?: PaginationParams & { 
  email?: string
  status?: number
  email_type?: EmailType
  server_id?: string
  create_time_start?: string
  create_time_end?: string
  update_time_start?: string
  update_time_end?: string
}) => {
  return api.get<any, ApiResponse<EmailInfo>>('/v1/mail/info', { params })
}

export const getEmailDetail = (id: string) => {
  return api.get<any, EmailInfo>(`/v1/mail/info/${id}`)
}

export const createEmail = (data: Partial<EmailInfo>) => {
  return api.post<any, EmailInfo>('/v1/mail/info', data)
}

export const updateEmail = (id: string, data: Partial<EmailInfo>) => {
  return api.put<any, EmailInfo>(`/v1/mail/info/${id}`, data)
}

export const deleteEmail = (id: string) => {
  return api.delete(`/v1/mail/info/${id}`)
}

// 批量更新邮箱状态
export const batchUpdateEmailStatus = (data: { from_status: number; to_status: number }) => {
  return api.post<any, ApiResponse>('/v1/mail/info/status/batch-update', data)
}

// Outlook 操作
export const getOutlookAuthUrl = (email: string) => {
  return api.get<any, { url: string; verifier: string }>('/v1/mail/outlook/auth/url', { params: { email } })
}

export const getOutlookToken = (data: { email: string; url: string; verifier: string }) => {
  return api.post<any, ApiResponse>('/v1/mail/outlook/auth/token', data)
}

export const sendOutlookEmail = (data: {
  email: string
  to_email: string
  subject: string
  content: string
  content_type?: 'Text' | 'HTML'
}) => {
  return api.post<any, ApiResponse>('/v1/mail/outlook/send', data)
}

export const getOutlookMessages = (data: {
  email: string
  from_email: string
  num?: number
  top?: number
}) => {
  return api.post<any, { code: number; message: string; data: any[] }>('/v1/mail/outlook/messages', data)
}

export const checkEmailStatus = (data: {
  update_time_start?: number
  update_time_end?: number
  status?: number
  email_type?: EmailType
}) => {
  return api.post<any, ApiResponse>('/v1/mail/outlook/check', data)
}

// 获取收件箱邮件列表（使用 messages 接口）
export const getInboxMessages = (params: {
  email: string
  top?: number
}) => {
  return api.post<any, {
    code: number
    message: string
    data: Array<{
      from_email: string
      title: string
      content: string
    }>
  }>('/v1/mail/outlook/messages', {
    email: params.email,
    from_email: '@',  // @ 表示查看所有邮件
    num: params.top || 10,  // 默认获取10条
    top: params.top || 10
  })
}

// 获取邮件详情
export const getMessageDetail = (messageId: string, email: string) => {
  return api.get<any, {
    code: number
    message: string
    data: {
      id: string
      subject: string
      from: string
      from_name: string
      to: string[]
      cc: string[]
      received_time: string
      body_type: string
      body_content: string
      has_attachments: boolean
      is_read: boolean
    }
  }>(`/v1/mail/outlook/message/${messageId}`, { params: { email } })
}
