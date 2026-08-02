"""用户模型。"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(SQLModel, table=True):
    """系统用户。role 取值见 app.core.state_machine.Role。"""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(default="", index=True)
    hashed_password: str = Field(default="")
    full_name: str = Field(default="")
    phone: str = Field(default="")
    role: str = Field(index=True)  # PATIENT / PRIME / RUNNER / GUIDE / SYSTEM / ADMIN
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow)
