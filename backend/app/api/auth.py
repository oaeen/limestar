"""Authentication API Routes"""

import secrets
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# 会话存储（token -> True，持久化直到服务重启）
_sessions: set[str] = set()


def require_auth(authorization: Optional[str] = Header(None)):
    """
    认证依赖：验证请求头中的 Bearer token
    用于保护需要管理员权限的 API 端点
    """
    if not settings.WEB_ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Web 管理功能未启用")

    if not authorization:
        raise HTTPException(status_code=401, detail="未提供认证信息")

    # 解析 Bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="无效的认证格式")

    token = authorization[7:]  # 去掉 "Bearer " 前缀

    if token not in _sessions:
        raise HTTPException(status_code=401, detail="无效或已过期的 token")

    return token


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
