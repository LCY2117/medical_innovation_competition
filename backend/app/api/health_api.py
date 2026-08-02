"""健康数据路由。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.api.deps import AuthContext, get_current_user, get_session
from app.api.serializers import available_actions_for
from app.models.event import Event
from app.models.health import HealthReading
from app.schemas.health import HealthReadingCreate, HealthReadingOut

router = APIRouter(prefix="/events/{event_id}/health", tags=["健康"])


@router.post("", response_model=HealthReadingOut, status_code=201)
async def add_reading(
    event_id: int,
    body: HealthReadingCreate,
    request: Request,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """上报健康读数（PRIME 或系统）。"""
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="事件不存在"
        )
    if ctx.role not in ("PRIME", "RUNNER", "GUIDE", "SYSTEM", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权上报健康数据",
        )

    reading = HealthReading(
        event_id=event_id,
        reading_type=body.reading_type,
        value=body.value,
        unit=body.unit,
        source=body.source or ctx.role,
    )
    session.add(reading)
    session.commit()
    session.refresh(reading)

    # WS 推送
    hub = request.app.state.hub
    await hub.broadcast_event(
        event.id,
        "HEALTH_READING",
        lambda conn: {
            "reading": {
                "id": reading.id,
                "reading_type": reading.reading_type,
                "value": reading.value,
                "unit": reading.unit,
                "source": reading.source,
                "recorded_at": reading.recorded_at.isoformat()
                if reading.recorded_at
                else None,
            }
        },
        version=event.seq,
    )
    return HealthReadingOut(
        id=reading.id,
        event_id=reading.event_id,
        reading_type=reading.reading_type,
        value=reading.value,
        unit=reading.unit,
        source=reading.source,
        recorded_at=reading.recorded_at,
    )


@router.get("", response_model=list[HealthReadingOut])
def list_readings(
    event_id: int,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="事件不存在"
        )
    rows = session.exec(
        select(HealthReading)
        .where(HealthReading.event_id == event_id)
        .order_by(HealthReading.id.asc())
    ).all()
    return [
        HealthReadingOut(
            id=r.id,
            event_id=r.event_id,
            reading_type=r.reading_type,
            value=r.value,
            unit=r.unit,
            source=r.source,
            recorded_at=r.recorded_at,
        )
        for r in rows
    ]
