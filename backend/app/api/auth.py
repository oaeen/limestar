"""Authentication API Routes"""

import secrets
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# 会话存储（token -> True，持久化直到服务重启）
_sessions: set[str] = set()


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    success: bool
    token: str | None = None
    message: str


class VerifyRequest(BaseModel):
    token: str


class VerifyResponse(BaseModel):
    valid: bool


class LogoutRequest(BaseModel):
    token: str


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    """验证密码并返回会话 token"""
    if not settings.WEB_ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Web 管理功能未启用")

    if data.password != settings.WEB_ADMIN_PASSWORD:
        return LoginResponse(success=False, message="密码错误")

    # 生成会话 token
    token = secrets.token_urlsafe(32)
    _sessions.add(token)

    return LoginResponse(success=True, token=token, message="登录成功")


@router.post("/verify", response_model=VerifyResponse)
def verify(data: VerifyRequest):
    """验证 token 是否有效"""
    return VerifyResponse(valid=data.token in _sessions)


@router.post("/logout")
def logout(data: LogoutRequest):
    """登出，使 token 失效"""
    _sessions.discard(data.token)
    return {"success": True}
