from typing import Optional
import time

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.crud.user.user import user_crud
from app.schemas.user.info import Out as UserOut
from app.utils.jwt_tool import JwtToken
from app.core.tools import hashing, gen_api_token


app = APIRouter()


class RegisterRequest(BaseModel):
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    nickname: str = Field(..., max_length=64, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """验证邮箱格式"""
        if not v:
            raise ValueError('邮箱不能为空')
        
        # 基本的邮箱格式验证
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('请输入有效的邮箱地址')
        
        return v.lower()


class LoginRequest(BaseModel):
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """验证邮箱格式，允许zhiyu账户"""
        if not v:
            raise ValueError('邮箱不能为空')
        
        # 允许zhiyu账户通过验证
        if v == 'zhiyu':
            return v
        
        # 其他账户需要符合邮箱格式
        if '@' not in v or '.' not in v.split('@')[-1]:
            raise ValueError('请输入有效的邮箱地址')
        
        return v.lower()


class RegisterResponse(BaseModel):
    message: str = Field("成功", description="提示信息")
    user: UserOut = Field(..., description="用户信息")
    api_token: str = Field(..., description="API访问令牌")


class AuthResponse(BaseModel):
    message: str = Field("成功", description="提示信息")
    user: UserOut = Field(..., description="用户信息")
    access_token: str = Field(..., description="JWT访问令牌")


@app.post("/register", response_model=RegisterResponse, description="用户注册", summary="用户注册")
async def register(item: RegisterRequest = Body(..., description="注册信息")):
    """
    用户注册
    - 使用bcrypt加密密码
    - 生成API token并存入数据库
    - 默认分配MANUAL角色
    - API token生成规则: MD5(用户名 + 13位时间戳 + "9527")
    """
    try:
        from app.models.user import UserRole, UserInfo, UserToken
        
        # 使用bcrypt加密密码
        password_hash = hashing.hash(item.password)
        
        user_out = await user_crud.create(
            {
                "email": item.email,
                "password": password_hash,
                "nickname": item.nickname,
                "avatar": item.avatar,
            }
        )
        
        # 分配默认角色MANUAL
        manual_role = await UserRole.get_or_none(code="MANUAL")
        if manual_role:
            user = await UserInfo.get(id=user_out.id)
            await user.roles.add(manual_role)
            # 重新获取用户信息（包含角色）
            await user.fetch_related('roles')
            user_out = UserOut.model_validate(user)
        
        # 生成API token
        # 使用邮箱作为用户名，13位时间戳（毫秒）
        timestamp_ms = int(time.time() * 1000)
        api_token = gen_api_token(item.email, timestamp_ms)
        
        # 保存token到数据库
        await UserToken.create(
            user_id=user_out.id,
            token=api_token,
            status=1  # 1: 正常
        )
        
        return RegisterResponse(message="注册成功", user=user_out, api_token=api_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login", response_model=AuthResponse, description="用户登录", summary="用户登录")
async def login(item: LoginRequest = Body(..., description="登录信息")):
    """
    用户登录
    - 使用bcrypt验证密码
    - 生成JWT token
    """
    try:
        from app.models.user import UserInfo
        user = await UserInfo.get_or_none(email=item.email).prefetch_related('roles')
        if not user:
            raise HTTPException(status_code=400, detail="邮箱或密码错误")
        
        # 使用bcrypt验证密码
        try:
            password_valid = hashing.verify(item.password, user.password)
        except Exception:
            # 捕获所有密码验证异常，统一返回错误信息
            raise HTTPException(status_code=400, detail="邮箱或密码错误")
        
        if not password_valid:
            raise HTTPException(status_code=400, detail="邮箱或密码错误")
        
        # 生成JWT token
        token_data = {
            "id": str(user.id),
            "email": user.email,
            "roles": [role.code for role in user.roles] if user.roles else []
        }
        access_token = JwtToken.create_token(token_data)
        
        user_out = UserOut(
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            avatar=user.avatar,
            status=user.status,
            create_time=user.create_time,
            update_time=user.update_time,
            roles=list(getattr(user, "roles", [])),
        )
        return AuthResponse(message="登录成功", user=user_out, access_token=access_token)
    except HTTPException:
        raise
    except Exception as e:
        # 捕获所有其他异常，不暴露系统细节
        raise HTTPException(status_code=400, detail="邮箱或密码错误")
