/**
 * JWT Token 工具类
 * 用于管理JWT token的存储、获取和验证
 */

const TOKEN_KEY = 'access_token'

export class TokenManager {
  /**
   * 保存token到localStorage
   */
  static setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token)
  }

  /**
   * 从localStorage获取token
   */
  static getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  }

  /**
   * 删除token
   */
  static removeToken(): void {
    localStorage.removeItem(TOKEN_KEY)
  }

  /**
   * 检查token是否存在
   */
  static hasToken(): boolean {
    return !!this.getToken()
  }

  /**
   * 解析JWT token（不验证签名）
   * 注意：这只是解析payload，不验证token的有效性
   */
  static parseToken(token: string): any {
    try {
      const parts = token.split('.')
      if (parts.length !== 3) {
        return null
      }
      
      // 解码payload部分
      const payload = parts[1]
      const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
      return JSON.parse(decoded)
    } catch (error) {
      console.error('解析token失败:', error)
      return null
    }
  }

  /**
   * 检查token是否过期
   */
  static isTokenExpired(token?: string): boolean {
    const tokenToCheck = token || this.getToken()
    if (!tokenToCheck) {
      return true
    }

    try {
      const payload = this.parseToken(tokenToCheck)
      if (!payload || !payload.exp) {
        return true
      }

      // exp是Unix时间戳（秒），需要转换为毫秒
      const expirationTime = payload.exp * 1000
      const currentTime = Date.now()

      return currentTime >= expirationTime
    } catch (error) {
      console.error('检查token过期失败:', error)
      return true
    }
  }

  /**
   * 获取token的剩余有效时间（秒）
   */
  static getTokenRemainingTime(token?: string): number {
    const tokenToCheck = token || this.getToken()
    if (!tokenToCheck) {
      return 0
    }

    try {
      const payload = this.parseToken(tokenToCheck)
      if (!payload || !payload.exp) {
        return 0
      }

      const expirationTime = payload.exp * 1000
      const currentTime = Date.now()
      const remainingTime = Math.floor((expirationTime - currentTime) / 1000)

      return remainingTime > 0 ? remainingTime : 0
    } catch (error) {
      console.error('获取token剩余时间失败:', error)
      return 0
    }
  }

  /**
   * 从token中获取用户信息
   */
  static getUserInfoFromToken(token?: string): any {
    const tokenToCheck = token || this.getToken()
    if (!tokenToCheck) {
      return null
    }

    try {
      const payload = this.parseToken(tokenToCheck)
      return payload
    } catch (error) {
      console.error('从token获取用户信息失败:', error)
      return null
    }
  }

  /**
   * 清除所有认证信息
   */
  static clearAuth(): void {
    this.removeToken()
    localStorage.removeItem('user-storage')
  }
}

export default TokenManager
