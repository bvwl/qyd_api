// 枚举类型
export enum UserStatus {
  NORMAL = 1,    // 正常
  DISABLED = 2,  // 停用
  LOCKED = 3,    // 锁定
  BANNED = 4     // 封禁
}

export enum ProjectStatus {
  NORMAL = 1,           // 正常
  NOT_WRITTEN = 2,      // 未编写
  WRITING = 3,          // 编写中
  FINISHED = 4,         // 项目结束
  RUNAWAY = 5,          // 项目跑路
  MAINTENANCE = 6,      // 项目维护
  UNASSIGNED = 7,       // 未分配
  ACCOUNT_UNSUPPORTED = 8,  // 账号不支持
  IP_UNSUPPORTED = 9    // IP不支持
}

export enum AccountType {
  EMAIL = 1,    // 邮箱
  WALLET = 2,   // 钱包
  X = 3,        // X
  OTHER1 = 4,   // 其他1
  OTHER2 = 5    // 其他2
}

export enum Status {
  NORMAL = 1,   // 正常
  ABNORMAL = 2  // 异常
}

export enum EmailType {
  IP_OK = 'IP_OK',
  IP_NOT = 'IP_NOT',
  TOKEN_OK = 'TOKEN_OK',
  TOKEN_NOT = 'TOKEN_NOT',
  IP_OK_TOKEN_OK = 'IP_OK_TOKEN_OK',
  IP_OK_TOKEN_NOT = 'IP_OK_TOKEN_NOT',
  IP_NOT_TOKEN_OK = 'IP_NOT_TOKEN_OK',
  IP_NOT_TOKEN_NOT = 'IP_NOT_TOKEN_NOT'
}

export enum ActionType {
  QUERY = 1,   // 查询
  CREATE = 2,  // 创建
  UPDATE = 3,  // 修改
  DELETE = 4,  // 删除
  OTHER1 = 5,  // 其他1
  OTHER2 = 6   // 其他2
}

// 用户相关
export interface User {
  id: string
  email: string
  nickname: string
  avatar?: string
  status: UserStatus
  create_time: string
  update_time: string
  roles?: Role[]
  projects?: Project[]
}

export interface Role {
  id: string
  name: string
  code: string
  description?: string
  create_time: string
  update_time: string
  routes?: Route[]
}

export interface Route {
  id: string
  name: string
  path: string
  component?: string
  title: string
  icon?: string
  sort: number
  redirect?: string
  is_hidden: boolean
  is_cache: boolean
  is_affix: boolean
  route_type: number  // 1:菜单, 2:按钮, 3:接口
  permission?: string  // 权限标识
  api_method?: string  // API方法
  api_path?: string    // API路径
  status: Status
  parent_id?: string
  parent?: Route
  children?: Route[]
}

export interface UserToken {
  id: string
  token: string
  status: Status
  user_id: string
  user?: User
  create_time: string
  update_time: string
}

export interface UserLog {
  id: string
  action: ActionType
  description?: string
  ip?: string
  user_agent?: string
  user_id: string
  user?: User
  create_time: string
  update_time: string
}

// 项目相关
export interface Project {
  id: string
  name: string
  status: ProjectStatus
  content?: string
  create_time: string
  update_time: string
  users?: User[]
}

export interface ProjectAccount {
  id: string
  account: string
  password?: string
  status: Status
  account_type: AccountType
  data?: Record<string, any>
  // 余额相关字段
  balance: number | string  // 后端返回字符串类型的 Decimal
  variable: number | string  // 后端返回字符串类型的 Decimal
  balance_history?: any
  project_id: string
  project?: Project
  server_id?: string
  server?: ServerInfo
  create_time: string
  update_time: string
}

export interface ProjectWallet {
  id: string
  private_key: string
  public_key: string
  mnemonic?: string  // 可选，私钥导入的钱包可能没有助记词
  chain: string
  remark?: string
  project_id?: string  // 可选，钱包可以独立存在
  project?: Project
  create_time: string
  update_time: string
}

// 服务器相关
export interface ServerCountry {
  id: string
  short_name: string
  name: string
  status: Status
  create_time: string
  update_time: string
}

export interface ServerGroup {
  id: string
  name: string
  status: Status
  country_id: string
  country?: ServerCountry
  create_time: string
  update_time: string
}

export interface ServerInfo {
  id: string
  host: string
  ssh_port?: number
  password?: string
  status: Status
  domain?: string
  is_sale: number
  port?: number
  proxy_url?: string  // SOCKS5代理URL
  group_id?: string
  group?: ServerGroup
  create_time: string
  update_time: string
}

export interface ServerAccount {
  id: string
  username: string
  password: string
  user_id: string
  user?: User
  create_time: string
  update_time: string
}

// 邮箱相关
export interface EmailInfo {
  id: string
  email: string
  password: string
  auxiliary_email: string
  auxiliary_email_password: string
  client_id?: string
  access_token?: string
  refresh_token?: string
  status: Status
  message?: string
  server_id?: string
  server_info?: ServerInfo
  proxy_type?: string
  proxy_url?: string
  create_time: string
  update_time: string
}

// API 响应
export interface ApiResponse<T = any> {
  message: string
  count?: number
  num?: number
  items?: T[]
  data?: T
}

// 分页参数
export interface PaginationParams {
  page?: number
  limit?: number
  res_count?: boolean
  order_by?: string
}

// 登录响应
export interface LoginResponse {
  message: string
  access_token: string
  user: User
}
