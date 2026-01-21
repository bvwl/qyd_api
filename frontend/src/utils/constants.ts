import { UserStatus, ProjectStatus, AccountType, Status, EmailType, ActionType } from '@/types'

// 用户状态映射
export const USER_STATUS_MAP = {
  [UserStatus.NORMAL]: { text: '正常', color: 'success' },
  [UserStatus.DISABLED]: { text: '停用', color: 'default' },
  [UserStatus.LOCKED]: { text: '锁定', color: 'warning' },
  [UserStatus.BANNED]: { text: '封禁', color: 'error' },
}

// 项目状态映射
export const PROJECT_STATUS_MAP = {
  [ProjectStatus.NORMAL]: { text: '正常', color: 'success' },
  [ProjectStatus.NOT_WRITTEN]: { text: '未编写', color: 'default' },
  [ProjectStatus.WRITING]: { text: '编写中', color: 'processing' },
  [ProjectStatus.FINISHED]: { text: '项目结束', color: 'default' },
  [ProjectStatus.RUNAWAY]: { text: '项目跑路', color: 'error' },
  [ProjectStatus.MAINTENANCE]: { text: '项目维护', color: 'warning' },
  [ProjectStatus.UNASSIGNED]: { text: '未分配', color: 'default' },
  [ProjectStatus.ACCOUNT_UNSUPPORTED]: { text: '账号不支持', color: 'error' },
  [ProjectStatus.IP_UNSUPPORTED]: { text: 'IP不支持', color: 'error' },
}

// 账号类型映射
export const ACCOUNT_TYPE_MAP = {
  [AccountType.EMAIL]: { text: '邮箱', color: 'blue' },
  [AccountType.WALLET]: { text: '钱包', color: 'green' },
  [AccountType.X]: { text: 'X', color: 'purple' },
  [AccountType.OTHER1]: { text: '其他1', color: 'default' },
  [AccountType.OTHER2]: { text: '其他2', color: 'default' },
}

// 通用状态映射
export const STATUS_MAP = {
  [Status.NORMAL]: { text: '正常', color: 'success' },
  [Status.ABNORMAL]: { text: '异常', color: 'error' },
}

// 邮箱类型映射
export const EMAIL_TYPE_MAP = {
  [EmailType.IP_OK]: { text: 'IP正常', color: 'success' },
  [EmailType.IP_NOT]: { text: 'IP异常', color: 'error' },
  [EmailType.TOKEN_OK]: { text: 'Token正常', color: 'success' },
  [EmailType.TOKEN_NOT]: { text: 'Token异常', color: 'error' },
  [EmailType.IP_OK_TOKEN_OK]: { text: 'IP正常+Token正常', color: 'success' },
  [EmailType.IP_OK_TOKEN_NOT]: { text: 'IP正常+Token异常', color: 'warning' },
  [EmailType.IP_NOT_TOKEN_OK]: { text: 'IP异常+Token正常', color: 'warning' },
  [EmailType.IP_NOT_TOKEN_NOT]: { text: 'IP异常+Token异常', color: 'error' },
}

// 操作类型映射
export const ACTION_TYPE_MAP = {
  [ActionType.QUERY]: { text: '查询', color: 'default' },
  [ActionType.CREATE]: { text: '创建', color: 'success' },
  [ActionType.UPDATE]: { text: '修改', color: 'processing' },
  [ActionType.DELETE]: { text: '删除', color: 'error' },
  [ActionType.OTHER1]: { text: '其他1', color: 'default' },
  [ActionType.OTHER2]: { text: '其他2', color: 'default' },
}

// 是否销售映射
export const IS_SALE_MAP = {
  1: { text: '是', color: 'success' },
  2: { text: '否', color: 'default' },
}
