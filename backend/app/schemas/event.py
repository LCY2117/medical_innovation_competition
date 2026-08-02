"""事件契约。"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AvailableAction(BaseModel):
    action: str
    label: str
    to_status: Optional[str] = None


class AssignmentOut(BaseModel):
    id: int
    responder_id: int
    responder_name: str = ""
    role: str
    status: str
    priority: int = 0
    score: float = 0.0
    assigned_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None


class EventOut(BaseModel):
    id: int
    patient_id: int
    status: str
    seq: int
    prime_confirmed: bool = False
    runner_confirmed: bool = False
    guide_confirmed: bool = False
    ambulance_arrived: bool = False
    shock_count: int = 0
    started_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    assignments: list[AssignmentOut] = Field(default_factory=list)
    available_actions: list[AvailableAction] = Field(default_factory=list)


class TransitionOut(BaseModel):
    id: int
    seq: int
    action: str
    from_status: str
    to_status: str
    actor_id: Optional[int] = None
    actor_role: str = ""
    duplicate: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class ActiveEventResponse(BaseModel):
    """GET /events/active 响应：无进行中事件时 event 为 null。"""

    event: Optional[EventOut] = None


class EventDetail(EventOut):
    timeline: list[TransitionOut] = Field(default_factory=list)


class SOSRequest(BaseModel):
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    note: str = ""


class ActionRequest(BaseModel):
    action: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActionResult(BaseModel):
    applied: bool
    duplicate: bool = False
    from_status: str
    to_status: str
    reason: str = ""
    new_seq: int
    event: Optional[EventOut] = None


class DispatchRequest(BaseModel):
    force: bool = False
