"""健康读数模型（急救过程中的生理数据流）。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.user import utcnow


class HealthReading(SQLModel, table=True):
    """一次健康读数，如心率/血氧/CPR节拍/除颤次数等。"""

    __tablename__ = "health_readings"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(index=True, foreign_key="events.id")
    reading_type: str = Field(index=True)  # heart_rate / spo2 / cpr_cycles / note ...
    value: float = Field(default=0.0)
    unit: str = Field(default="")
    source: str = Field(default="")  # PRIME / RUNNER / SYSTEM ...
    recorded_at: datetime = Field(default_factory=utcnow)
