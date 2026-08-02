"""认证契约。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class DemoLoginRequest(BaseModel):
    role: str = Field(description="PATIENT/PRIME/RUNNER/GUIDE")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    username: str
    expires_in: int


class UserOut(BaseModel):
    id: int
    username: str
    email: str = ""
    full_name: str = ""
    phone: str = ""
    role: str
    is_active: bool = True
    created_at: Optional[datetime] = None
