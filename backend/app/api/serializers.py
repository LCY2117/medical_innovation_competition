"""事件序列化工具：EventOut / 时间线 / WS 推送数据。"""
from __future__ import annotations

import json
from typing import Any

from sqlmodel import Session, select

from app.core.state_machine import EventState, StateMachineEngine
from app.models.event import Event, EventAssignment, EventTransition
from app.models.user import User
from app.schemas.event import AssignmentOut, AvailableAction, TransitionOut

_sm = StateMachineEngine()


def _to_event_state(event: Event) -> EventState:
    return EventState(
        status=event.status,
        seq=event.seq,
        prime_confirmed=event.prime_confirmed,
        runner_confirmed=event.runner_confirmed,
        guide_confirmed=event.guide_confirmed,
        ambulance_arrived=event.ambulance_arrived,
        shock_count=event.shock_count,
    )


def available_actions_for(event: Event, role: str) -> list[dict]:
    """推导指定角色的可执行动作。"""
    return _sm.available_actions(_to_event_state(event), role)


def _assignment_to_out(ass: EventAssignment, session: Session) -> AssignmentOut:
    responder = session.get(User, ass.responder_id)
    name = responder.full_name if responder else ""
    return AssignmentOut(
        id=ass.id,
        responder_id=ass.responder_id,
        responder_name=name or (responder.username if responder else ""),
        role=ass.role,
        status=ass.status,
        priority=ass.priority,
        score=ass.score,
        assigned_at=ass.assigned_at,
        responded_at=ass.responded_at,
    )


def list_assignments(session: Session, event_id: int) -> list[AssignmentOut]:
    rows = session.exec(
        select(EventAssignment)
        .where(EventAssignment.event_id == event_id)
        .order_by(EventAssignment.priority.asc(), EventAssignment.id.asc())
    ).all()
    return [_assignment_to_out(r, session) for r in rows]


def _transition_to_out(t: EventTransition) -> TransitionOut:
    return TransitionOut(
        id=t.id,
        seq=t.seq,
        action=t.action,
        from_status=t.from_status,
        to_status=t.to_status,
        actor_id=t.actor_id,
        actor_role=t.actor_role,
        duplicate=t.duplicate,
        payload=json.loads(t.payload) if t.payload else {},
        created_at=t.created_at,
    )


def list_timeline(session: Session, event_id: int) -> list[TransitionOut]:
    rows = session.exec(
        select(EventTransition)
        .where(EventTransition.event_id == event_id)
        .order_by(EventTransition.seq.asc(), EventTransition.id.asc())
    ).all()
    return [_transition_to_out(r) for r in rows]


def event_dict_for_role(
    event: Event, role: str
) -> dict[str, Any]:
    """WS EVENT_UPDATE / EVENT_SNAPSHOT 的 data 载荷（按角色裁剪）。"""
    return {
        "id": event.id,
        "status": event.status,
        "seq": event.seq,
        "patient_id": event.patient_id,
        "prime_confirmed": event.prime_confirmed,
        "runner_confirmed": event.runner_confirmed,
        "guide_confirmed": event.guide_confirmed,
        "ambulance_arrived": event.ambulance_arrived,
        "shock_count": event.shock_count,
        "started_at": event.started_at.isoformat() if event.started_at else None,
        "created_at": event.created_at.isoformat() if event.created_at else None,
        "updated_at": event.updated_at.isoformat() if event.updated_at else None,
        "location": event.location,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "available_actions": available_actions_for(event, role),
    }
