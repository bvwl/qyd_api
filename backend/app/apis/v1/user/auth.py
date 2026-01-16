import hashlib
import secrets
from datetime import timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.crud.user.user import user_crud
from app.crud.user.token import token_crud
from app.schemas.user.user import Out as UserOut
from app.utils.time_tool import now_cn


app = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    nickname: str = Field(..., max_length=64, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class AuthResponse(BaseModel):
    message: str = Field("成功", description="提示信息")
    user: UserOut = Field(..., description="用户信息")
    access_token: str = Field(..., min_length=32, max_length=32, description="访问令牌")


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


async def _create_token_for_user(user_id: UUID) -> str:
    access_token = secrets.token_hex(16)
    expired_at = (now_cn() + timedelta(days=7)).replace(tzinfo=None)
    await token_crud.create(
        {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": None,
            "expired_at": expired_at,
            "is_revoked": False,
        }
    )
    return access_token


@app.post("/register", response_model=AuthResponse, description="用户注册", summary="用户注册")
async def register(item: RegisterRequest = Body(..., description="注册信息")):
    try:
        password_hash = _hash_password(item.password)
        user = await user_crud.create(
            {
                "email": item.email,
                "password_hash": password_hash,
                "nickname": item.nickname,
                "avatar": item.avatar,
            }
        )
        access_token = await _create_token_for_user(user.id)
        user_out = UserOut(
            message="成功",
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            avatar=user.avatar,
            status=user.status,
            create_time=user.create_time,
            update_time=user.update_time,
            roles=list(getattr(user, "roles", [])),
        )
        return AuthResponse(message="成功", user=user_out, access_token=access_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login", response_model=AuthResponse, description="用户登录", summary="用户登录")
async def login(item: LoginRequest = Body(..., description="登录信息")):
    try:
        user = await user_crud.model.get_or_none(email=item.email)
        if not user:
            raise HTTPException(status_code=400, detail="邮箱或密码错误")
        password_hash = _hash_password(item.password)
        if user.password_hash != password_hash:
            raise HTTPException(status_code=400, detail="邮箱或密码错误")
        access_token = await _create_token_for_user(user.id)
        user_out = UserOut(
            message="成功",
            id=user.id,
            email=user.email,
            nickname=user.nickname,
            avatar=user.avatar,
            status=user.status,
            create_time=user.create_time,
            update_time=user.update_time,
            roles=list(getattr(user, "roles", [])),
        )
        return AuthResponse(message="成功", user=user_out, access_token=access_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

