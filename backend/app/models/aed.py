"""AED 设备模型。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.user import utcnow


class AedDevice(SQLModel, table=True):
    """AED 自动体外除颤仪点位。"""

    __tablename__ = "aed_devices"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    location: str = Field(default="")
    latitude: float = Field(default=0.0)
    longitude: float = Field(default=0.0)
    available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
