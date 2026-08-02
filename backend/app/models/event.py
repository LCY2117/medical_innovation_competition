"""事件、分派、时间线模型。

event_transitions 是时间线/证据的唯一来源：
每次状态机成功转移都会写入一行，同时 events.seq 自增（作为 WS 版本号）。
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.user import utcnow


class Event(SQLModel, table=True):
    """一次救援事件。status/seq 为核心状态机字段。"""

    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(index=True, foreign_key="users.id")

    # ---- 状态机核心 ----
    status: str = Field(default="CREATED", index=True)
    seq: int = Field(default=0)  # 单调递增 WS 版本号

    # ---- 并行标志 ----
    prime_confirmed: bool = Field(default=False)
    runner_confirmed: bool = Field(default=False)
    guide_confirmed: bool = Field(default=False)
    ambulance_arrived: bool = Field(default=False)
    shock_count: int = Field(default=0)

    # ---- 时间 ----
    started_at: Optional[datetime] = Field(default=None)  # 黄金时间起点(SOS)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    # ---- 事件地点 ----
    location: str = Field(default="")
    latitude: float = Field(default=0.0)
    longitude: float = Field(default=0.0)


class EventAssignment(SQLModel, table=True):
    """分派结果：每个角色对应一名被指派的施救者。"""

    __tablename__ = "event_assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(index=True, foreign_key="events.id")
    responder_id: int = Field(index=True, foreign_key="users.id")
    role: str = Field(index=True)  # PRIME / RUNNER / GUIDE
    status: str = Field(default="PENDING")  # PENDING / CONFIRMED / DECLINED / BACKUP
    priority: int = Field(default=0)  # 递补顺序，0 为主选
    score: float = Field(default=0.0)  # 打分结果(审计用)
    reason: str = Field(default="")
    assigned_at: datetime = Field(default_factory=utcnow)
    responded_at: Optional[datetime] = Field(default=None)


class EventTransition(SQLModel, table=True):
    """状态机转移记录：时间线与证据的唯一来源。"""

    __tablename__ = "event_transitions"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(index=True, foreign_key="events.id")
    seq: int = Field(default=0)  # 与事件 seq 对齐
    action: str = Field(index=True)
    from_status: str = Field(default="")
    to_status: str = Field(default="")
    actor_id: Optional[int] = Field(default=None, foreign_key="users.id")
    actor_role: str = Field(default="")
    duplicate: bool = Field(default=False)
    payload: str = Field(default="")  # JSON 字符串
    created_at: datetime = Field(default_factory=utcnow)
