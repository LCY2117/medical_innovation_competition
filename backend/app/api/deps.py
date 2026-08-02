"""API 依赖：鉴权（JWT）、数据库会话、角色权限。"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from app.config import Settings
from app.models.user import User

_bearer = HTTPBearer(auto_error=False)


class AuthContext(BaseModel):
    """当前登录用户 + 角色。"""

    user_id: int
    role: str
    username: str
    user: User


# ---------- 会话 ----------

def get_session(request: Request) -> Session:
    factory = request.app.state.session_factory
    session = factory()
    try:
        yield session
    finally:
        session.close()


# ---------- JWT ----------

def create_access_token(user: User, settings: Settings) -> str:
    expires = timedelta(minutes=settings.access_token_expire_minutes)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "exp": now + expires,
        "iat": now,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str, settings: Settings) -> dict:
    return jwt.decode(
        token, settings.secret_key, algorithms=[settings.algorithm]
    )


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: Session = Depends(get_session),
) -> AuthContext:
    settings: Settings = request.app.state.settings
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少 Bearer Token",
        )
    try:
        payload = decode_token(credentials.credentials, settings)
        user_id = int(payload.get("sub", "0"))
        role = payload.get("role", "")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        )
    user = session.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用",
        )
    if role != user.role:  # 角色以数据库为准
        role = user.role
    return AuthContext(
        user_id=user.id, role=role, username=user.username, user=user
    )


def require_roles(*roles: str) -> Callable:
    """角色权限依赖工厂。"""

    def _dep(ctx: AuthContext = Depends(get_current_user)) -> AuthContext:
        if ctx.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"角色 {ctx.role} 无权访问该资源",
            )
        return ctx

    return _dep


def get_system_user(session: Session) -> User | None:
    """取 SYSTEM 账号（自动分派/后台任务用）。"""
    return session.exec(select(User).where(User.role == "SYSTEM")).first()


# ---------- 工具 ----------

def ws_user_from_token(settings: Settings, token: str) -> AuthContext:
    """WS 握手时解析 token（无 HTTP Header，使用 query 参数）。"""
    try:
        payload = decode_token(token, settings)
        user_id = int(payload.get("sub", "0"))
        role = payload.get("role", "")
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="WS Token 无效",
        )
    return AuthContext(
        user_id=user_id,
        role=role,
        username=payload.get("username", ""),
        user=User(id=user_id, role=role, username=payload.get("username", "")),
    )
