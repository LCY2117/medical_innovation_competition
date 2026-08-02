"""AED 设备契约。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AedCreate(BaseModel):
    name: str
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    available: bool = True


class AedUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    available: Optional[bool] = None


class AedOut(BaseModel):
    id: int
    name: str
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    available: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
