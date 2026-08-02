"""SQLModel ORM 模型包。所有模型在此注册到 SQLModel.metadata，供建表使用。"""
from app.models.user import User  # noqa: F401
from app.models.responder import ResponderProfile  # noqa: F401
from app.models.event import (  # noqa: F401
    Event,
    EventAssignment,
    EventTransition,
)
from app.models.health import HealthReading  # noqa: F401
from app.models.aed import AedDevice  # noqa: F401

__all__ = [
    "User",
    "ResponderProfile",
    "Event",
    "EventAssignment",
    "EventTransition",
    "HealthReading",
    "AedDevice",
]
