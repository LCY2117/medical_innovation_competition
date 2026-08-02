"""施救者画像模型：分派打分所需的属性字段。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.user import utcnow


class ResponderProfile(SQLModel, table=True):
    """施救者画像。role 对应 PRIME/RUNNER/GUIDE。

    responder_status 用于过滤候选：
        AVAILABLE 可用 / TIRED 疲劳(需过滤) / OFFLINE 离线 / BUSY 忙碌
    """

    __tablename__ = "responder_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True, unique=True, foreign_key="users.id")
    role: str = Field(index=True)  # PRIME / RUNNER / GUIDE
    responder_status: str = Field(default="AVAILABLE", index=True)

    # ---- 打分字段（0~1 越大越好）----
    skill_level: float = Field(default=0.5)  # 施救技能(PRIME)
    fitness: float = Field(default=0.5)  # 体能(PRIME)
    health_active: bool = Field(default=True)  # 健康档案在线(PRIME)
    venue_familiarity: float = Field(default=0.5)  # 场地熟悉度(GUIDE)

    # ---- 距离（公里）----
    distance_km: float = Field(default=5.0)  # 距事发地
    aed_distance_km: float = Field(default=5.0)  # 距最近AED(RUNNER)

    latitude: float = Field(default=0.0)
    longitude: float = Field(default=0.0)

    updated_at: datetime = Field(default_factory=utcnow)
