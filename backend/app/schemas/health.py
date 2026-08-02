"""健康契约。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HealthReadingCreate(BaseModel):
    reading_type: str
    value: float = 0.0
    unit: str = ""
    source: str = ""


class HealthReadingOut(BaseModel):
    id: int
    event_id: int
    reading_type: str
    value: float
    unit: str = ""
    source: str = ""
    recorded_at: Optional[datetime] = None
