"""认证路由：登录 / 演示登录 / 当前用户。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from passlib.hash import pbkdf2_sha256
from sqlmodel import Session, select

from app.api.deps import (
    AuthContext,
    create_access_token,
    get_current_user,
    get_session,
)
from app.config import Settings
from app.models.user import User
from app.schemas.auth import (
    DemoLoginRequest,
    LoginRequest,
    TokenResponse,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["认证"])

DEMO_ROLES = ("PATIENT", "PRIME", "RUNNER", "GUIDE")


def _issue_token(user: User, settings: Settings) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user, settings),
        token_type="bearer",
        user_id=user.id,
        role=user.role,
        username=user.username,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    request: Request,
    session: Session = Depends(get_session),
):
    """账号密码登录（管理/系统账号）。"""
    settings: Settings = request.app.state.settings
    user = session.exec(
        select(User).where(User.username == body.username)
    ).first()
    if user is None or not pbkdf2_sha256.verify(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已禁用"
        )
    return _issue_token(user, settings)


@router.post("/demo", response_model=TokenResponse)
def demo_login(
    body: DemoLoginRequest,
    request: Request,
    session: Session = Depends(get_session),
):
    """演示登录：PATIENT/PRIME/RUNNER/GUIDE。"""
    settings: Settings = request.app.state.settings
    role = body.role.upper()
    if role not in DEMO_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"演示角色必须是 {', '.join(DEMO_ROLES)} 之一",
        )
    user = session.exec(
        select(User).where(
            User.role == role, User.username.in_(
                [r.lower() for r in DEMO_ROLES]
            )
        )
    ).first()
    if user is None:
        # 幂等创建演示用户（正常由 seed 写入，此处兜底）
        user = User(
            username=role.lower(),
            full_name=f"{role} 演示用户",
            role=role,
            hashed_password=pbkdf2_sha256.hash(settings.demo_password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return _issue_token(user, settings)


@router.get("/me", response_model=UserOut)
def me(ctx: AuthContext = Depends(get_current_user)):
    return UserOut(
        id=ctx.user.id,
        username=ctx.user.username,
        email=ctx.user.email,
        full_name=ctx.user.full_name,
        phone=ctx.user.phone,
        role=ctx.user.role,
        is_active=ctx.user.is_active,
        created_at=ctx.user.created_at,
    )
