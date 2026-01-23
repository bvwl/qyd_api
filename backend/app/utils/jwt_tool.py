import uuid
from jose import jwt
from datetime import timedelta, datetime, timezone
from app.core import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException


class JWTTool:
    """JWT工具类"""
    # 异常类
    JWTError = jwt.JWTError
    ExpiredSignatureError = jwt.ExpiredSignatureError

    def create_token(self, data: dict, expire_time: int | None = None) -> str:
        """
        生成JWT
        :param data: 需要进行JWT令牌加密的用户信息（解密的时候会用到）
        :param expire_time: 令牌有效期，单位：秒
        :return: jwt
        """
        now_time = datetime.now(timezone.utc)
        if expire_time:
            expire = now_time + timedelta(seconds=expire_time)
        else:
            expire = now_time + timedelta(seconds=settings.JWT['expire_time'])

        # 组装载荷数据的标准声明
        payload = {
            "exp": expire,  # 过期时间
            "iat": now_time,  # 生成时间
            "jti": str(uuid.uuid4())  # 唯一标记
        }
        # 组装载荷数据的公共声明
        payload.update(data)

        # 自动生成jwt
        token = jwt.encode(payload, settings.JWT['secret_key'], algorithm=settings.JWT['algorithm'])
        return token

    def verify_token(self, token: str) -> dict:
        """
        验证token
        :param token: 客户端发送过来的token
        :return: 返回用户信息
        """
        payload = jwt.decode(token, settings.JWT['secret_key'], algorithms=[settings.JWT['algorithm']])
        return payload

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """从JWT token中获取当前用户（基础认证）"""
        try:
            # 验证token
            payload = self.verify_token(credentials.credentials)
            user_id = payload.get('id')
            roles = payload.get('roles', [])
            if not user_id:
                raise HTTPException(status_code=401, detail="无效的token")
            return {"user_id": user_id, "roles": roles}
        except self.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="token已过期")
        except self.JWTError:
            raise HTTPException(status_code=401, detail="token无效")
        except Exception:
            raise HTTPException(status_code=401, detail="认证失败")

    async def get_admin_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """获取管理员用户，自动验证管理员权限"""
        user_info = await self.get_current_user(credentials)
        if "ADMIN" not in user_info["roles"]:
            raise HTTPException(status_code=403, detail="需要管理员权限")
        return user_info

    async def get_gm_user(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        """获取GM用户，自动验证GM权限"""
        user_info = await self.get_current_user(credentials)
        if not any(role in user_info["roles"] for role in ["GM", "ADMIN"]):
            raise HTTPException(status_code=403, detail="需要GM(项目管理员)或管理员权限")
        return user_info


JwtToken = JWTTool()


def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """
    创建访问令牌的便捷函数
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间（秒），如果为None则使用默认配置
        
    Returns:
        str: JWT token
    """
    return JwtToken.create_token(data, expires_delta)
