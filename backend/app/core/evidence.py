"""证据导出器：把一次事件完整打包为 JSON / ZIP。

证据包内容：
    - manifest.json      清单（事件ID、导出时间、统计）
    - event.json         事件主记录
    - timeline.json      状态机时间线（唯一事实来源）
    - assignments.json   分派记录
    - health.json        健康读数
"""
from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select


def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def build_event_dict(session: Session, event) -> dict[str, Any]:
    """组装 event.json 内容。"""
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
        "started_at": _iso(event.started_at),
        "created_at": _iso(event.created_at),
        "updated_at": _iso(event.updated_at),
        "location": event.location,
        "latitude": event.latitude,
        "longitude": event.longitude,
    }


def build_transitions(session: Session, event_id: int) -> list[dict[str, Any]]:
    from app.models.event import EventTransition

    rows = session.exec(
        select(EventTransition)
        .where(EventTransition.event_id == event_id)
        .order_by(EventTransition.seq.asc(), EventTransition.id.asc())
    ).all()
    return [
        {
            "id": r.id,
            "seq": r.seq,
            "action": r.action,
            "from_status": r.from_status,
            "to_status": r.to_status,
            "actor_id": r.actor_id,
            "actor_role": r.actor_role,
            "duplicate": r.duplicate,
            "payload": json.loads(r.payload) if r.payload else {},
            "created_at": _iso(r.created_at),
        }
        for r in rows
    ]


def build_assignments(session: Session, event_id: int) -> list[dict[str, Any]]:
    from app.models.event import EventAssignment

    rows = session.exec(
        select(EventAssignment)
        .where(EventAssignment.event_id == event_id)
        .order_by(EventAssignment.id.asc())
    ).all()
    return [
        {
            "id": r.id,
            "responder_id": r.responder_id,
            "role": r.role,
            "status": r.status,
            "priority": r.priority,
            "score": r.score,
            "reason": r.reason,
            "assigned_at": _iso(r.assigned_at),
            "responded_at": _iso(r.responded_at),
        }
        for r in rows
    ]


def build_health(session: Session, event_id: int) -> list[dict[str, Any]]:
    from app.models.health import HealthReading

    rows = session.exec(
        select(HealthReading)
        .where(HealthReading.event_id == event_id)
        .order_by(HealthReading.id.asc())
    ).all()
    return [
        {
            "id": r.id,
            "reading_type": r.reading_type,
            "value": r.value,
            "unit": r.unit,
            "source": r.source,
            "recorded_at": _iso(r.recorded_at),
        }
        for r in rows
    ]


def build_evidence_bundle(session: Session, event) -> dict[str, Any]:
    """完整证据包（JSON 结构）。"""
    timeline = build_transitions(session, event.id)
    manifest = {
        "event_id": event.id,
        "exported_at": _iso(datetime.now(timezone.utc)),
        "final_status": event.status,
        "final_seq": event.seq,
        "transition_count": len(timeline),
        "schema_version": "1.0",
    }
    return {
        "manifest": manifest,
        "event": build_event_dict(session, event),
        "timeline": timeline,
        "assignments": build_assignments(session, event.id),
        "health": build_health(session, event.id),
    }


def build_zip_bytes(bundle: dict[str, Any]) -> bytes:
    """把证据包压缩为 ZIP 字节流。"""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in (
            "manifest.json",
            "event.json",
            "timeline.json",
            "assignments.json",
            "health.json",
        ):
            key = {
                "manifest.json": "manifest",
                "event.json": "event",
                "timeline.json": "timeline",
                "assignments.json": "assignments",
                "health.json": "health",
            }[name]
            zf.writestr(name, json.dumps(bundle[key], ensure_ascii=False, indent=2))
    return buf.getvalue()
