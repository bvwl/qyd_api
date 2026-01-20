import dayjs from 'dayjs'

/**
 * 格式化日期时间
 */
export const formatDateTime = (date: string | Date, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!date) return '-'
  return dayjs(date).format(format)
}

/**
 * 格式化日期
 */
export const formatDate = (date: string | Date) => {
  return formatDateTime(date, 'YYYY-MM-DD')
}

/**
 * 格式化时间
 */
export const formatTime = (date: string | Date) => {
  return formatDateTime(date, 'HH:mm:ss')
}

/**
 * 脱敏处理
 */
export const maskString = (str: string, start = 3, end = 3) => {
  if (!str || str.length <= start + end) return str
  return str.substring(0, start) + '***' + str.substring(str.length - end)
}

/**
 * 脱敏邮箱
 */
export const maskEmail = (email: string) => {
  if (!email) return ''
  const [name, domain] = email.split('@')
  if (!domain) return email
  return maskString(name, 2, 1) + '@' + domain
}

/**
 * 脱敏密码
 */
export const maskPassword = (password: string) => {
  if (!password) return ''
  return '******'
}

/**
 * 格式化文件大小
 */
export const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

/**
 * 格式化数字
 */
export const formatNumber = (num: number, decimals = 2) => {
  if (num === null || num === undefined) return '-'
  return num.toFixed(decimals)
}

/**
 * 复制到剪贴板
 */
export const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (err) {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    const success = document.execCommand('copy')
    document.body.removeChild(textarea)
    return success
  }
}
