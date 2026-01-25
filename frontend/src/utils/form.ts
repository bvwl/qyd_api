/**
 * 表单工具函数
 */

/**
 * 过滤表单值中的空字符串
 * 将空字符串转换为 undefined（不传递该字段）
 * 
 * 用于 PUT/PATCH 请求，确保只更新用户实际填写的字段
 * 配合后端的 exclude_unset=True 使用
 * 
 * @param values 表单值对象
 * @returns 过滤后的对象（不包含空字符串字段）
 * 
 * @example
 * ```typescript
 * const values = await form.validateFields()
 * const filteredValues = filterEmptyStrings(values)
 * await updateUser(userId, filteredValues)
 * ```
 */
export function filterEmptyStrings<T extends Record<string, any>>(values: T): Partial<T> {
  return Object.entries(values).reduce((acc, [key, value]) => {
    // 如果值是空字符串，不包含该字段（相当于 undefined）
    if (value === '') {
      return acc
    }
    // 其他值正常包含
    acc[key] = value
    return acc
  }, {} as Partial<T>)
}

/**
 * 过滤对象中的 null 和 undefined 值
 * 
 * @param obj 对象
 * @returns 过滤后的对象
 */
export function filterNullish<T extends Record<string, any>>(obj: T): Partial<T> {
  return Object.entries(obj).reduce((acc, [key, value]) => {
    if (value !== null && value !== undefined) {
      acc[key] = value
    }
    return acc
  }, {} as Partial<T>)
}

/**
 * 过滤对象中的空字符串、null 和 undefined 值
 * 
 * @param obj 对象
 * @returns 过滤后的对象
 */
export function filterEmpty<T extends Record<string, any>>(obj: T): Partial<T> {
  return Object.entries(obj).reduce((acc, [key, value]) => {
    if (value !== '' && value !== null && value !== undefined) {
      acc[key] = value
    }
    return acc
  }, {} as Partial<T>)
}
