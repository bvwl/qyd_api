/**
 * RBAC v2 API
 */
import api from './index'

// ==========================================
// 类型定义
// ==========================================

export interface Menu {
  id: string
  code: string
  title: string
  path: string
  component?: string
  icon?: string
  sort: number
  parent_id?: string
  is_hidden: boolean
  is_cache: boolean
  is_affix: boolean
  redirect?: string
  status: number
  create_time: string
  update_time: string
  children?: Menu[]
}

export interface Permission {
  id: string
  code: string
  name: string
  description?: string
  resource: string
  action: string
  permission_type: number
  api_method?: string
  api_path?: string
  group?: string
  status: number
  create_time: string
  update_time: string
}

export interface Role {
  id: string
  code: string
  name: string
  description?: string
  level: number
  data_scope: number
  is_system: boolean
  status: number
  create_time: string
  update_time: string
}

// ==========================================
// 用户权限 API
// ==========================================

/**
 * 获取当前用户的菜单树
 */
export const getUserMenus = () => {
  return api.get<any, { code: number; data: Menu[]; count: number }>('/v1/rbac/user/menus')
}

/**
 * 获取当前用户的权限列表
 */
export const getUserPermissions = () => {
  return api.get<any, { code: number; data: string[]; count: number }>('/v1/rbac/user/permissions')
}

/**
 * 检查当前用户是否有指定权限
 */
export const checkUserPermission = (code: string) => {
  return api.get<any, { code: number; data: { has_permission: boolean } }>(
    `/v1/rbac/user/has-permission?code=${code}`
  )
}

// ==========================================
// 菜单管理 API
// ==========================================

/**
 * 获取菜单树
 */
export const getMenuTree = (params?: { status?: number }) => {
  return api.get<any, { code: number; data: Menu[]; count: number }>('/v1/rbac/menu/tree', {
    params
  })
}

/**
 * 获取菜单列表（分页）
 */
export const getMenuList = (params?: {
  code?: string
  title?: string
  parent_id?: string
  status?: number
  page?: number
  limit?: number
}) => {
  return api.get<any, { code: number; data: { items: Menu[]; total: number } }>('/v1/rbac/menu', {
    params
  })
}

/**
 * 获取菜单详情
 */
export const getMenuDetail = (id: string) => {
  return api.get<any, { code: number; data: Menu }>(`/v1/rbac/menu/${id}`)
}

/**
 * 创建菜单
 */
export const createMenu = (data: {
  code: string
  title: string
  path: string
  component?: string
  icon?: string
  sort?: number
  parent_id?: string
  is_hidden?: boolean
  is_cache?: boolean
  is_affix?: boolean
  redirect?: string
}) => {
  return api.post<any, { code: number; message: string; data: { id: string } }>('/v1/rbac/menu', data)
}

/**
 * 更新菜单
 */
export const updateMenu = (id: string, data: Partial<Menu>) => {
  return api.put<any, { code: number; message: string }>(`/v1/rbac/menu/${id}`, data)
}

/**
 * 删除菜单
 */
export const deleteMenu = (id: string) => {
  return api.delete<any, { code: number; message: string }>(`/v1/rbac/menu/${id}`)
}

// ==========================================
// 角色管理 API
// ==========================================

/**
 * 获取角色列表
 */
export const getRoleList = (params?: {
  code?: string
  name?: string
  status?: number
  page?: number
  limit?: number
}) => {
  return api.get<any, { code: number; data: { items: Role[]; total: number } }>('/v1/rbac/role', {
    params
  })
}

/**
 * 获取角色详情
 */
export const getRoleDetail = (id: string) => {
  return api.get<any, { code: number; data: Role }>(`/v1/rbac/role/${id}`)
}

/**
 * 创建角色
 */
export const createRole = (data: {
  code: string
  name: string
  description?: string
  level?: number
  data_scope?: number
}) => {
  return api.post<any, { code: number; message: string; data: { id: string } }>('/v1/rbac/role', data)
}

/**
 * 更新角色
 */
export const updateRole = (id: string, data: Partial<Role>) => {
  return api.put<any, { code: number; message: string }>(`/v1/rbac/role/${id}`, data)
}

/**
 * 删除角色
 */
export const deleteRole = (id: string) => {
  return api.delete<any, { code: number; message: string }>(`/v1/rbac/role/${id}`)
}

/**
 * 获取角色的菜单
 */
export const getRoleMenus = (id: string) => {
  return api.get<any, { code: number; data: string[]; count: number }>(`/v1/rbac/role/${id}/menus`)
}

/**
 * 设置角色的菜单
 * 
 * 注意：menu_ids 应该包含所有选中的节点（包括半选的父节点）
 * 后端会自动补全所有父级菜单
 */
export const setRoleMenus = (id: string, menu_ids: string[]) => {
  return api.post<any, { code: number; message: string; count: number }>(`/v1/rbac/role/${id}/menus`, { menu_ids })
}
