"""演示/管理路由：重置、初始化种子、一键触发演示事件。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import delete
from sqlmodel import Session, select

from app.api.deps import get_session, require_roles
from app.models.event import Event, EventAssignment, EventTransition
from app.models.health import HealthReading
from app.models.user import User

router = APIRouter(prefix="/demo", tags=["演示"])


@router.post("/init")
def demo_init(
    request: Request,
    ctx=Depends(require_roles("SYSTEM", "ADMIN")),
    session: Session = Depends(get_session),
):
    """确保种子数据存在（幂等）。"""
    from app.seed import seed_if_empty

    seeded = seed_if_empty(session, request.app.state.settings)
    return {"ok": True, "seeded": seeded}


@router.post("/reset")
def demo_reset(
    request: Request,
    ctx=Depends(require_roles("SYSTEM", "ADMIN")),
    session: Session = Depends(get_session),
):
    """清空全部业务数据（保留用户/AED/施救者画像），并重新种入。"""
    for model in (HealthReading, EventTransition, EventAssignment, Event):
        session.exec(delete(model))
    session.commit()

    from app.seed import seed_if_empty

    seed_if_empty(session, request.app.state.settings)
    return {"ok": True, "message": "演示数据已重置"}


@router.post("/trigger")
async def demo_trigger(
    request: Request,
    ctx=Depends(require_roles("SYSTEM", "ADMIN")),
    session: Session = Depends(get_session),
):
    """一键触发：创建事件 → SOS → 立即分派，返回事件详情。"""
    from app.api.events import apply_action, _event_to_out
    from app.core.state_machine import Action
    from app.models.user import utcnow
    from app.schemas.event import ActionRequest, SOSRequest

    # 找一个演示患者
    patient = session.exec(select(User).where(User.role == "PATIENT")).first()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="无演示患者"
        )
    # 若已有进行中事件，先返回其 id（避免并发冲突）
    from app.core.state_machine import ACTIVE_STATES

    active = session.exec(
        select(Event).where(
            Event.patient_id == patient.id,
            Event.status.in_(ACTIVE_STATES),
        )
    ).first()

    class _FakePatientCtx:
        user_id = patient.id
        role = "PATIENT"
        username = patient.username

    if active is not None:
        event = active
    else:
        event = Event(
            patient_id=patient.id,
            status="CREATED",
            seq=0,
            location="演示场地·中心广场",
            latitude=30.1,
            longitude=120.2,
            started_at=utcnow(),
        )
        session.add(event)
        session.commit()
        session.refresh(event)

        res = await apply_action(
            request,
            session,
            event.id,
            _FakePatientCtx(),
            ActionRequest(
                action=Action.SOS_TRIGGERED.value,
                metadata={"note": "演示触发"},
            ),
        )
        if not res.applied:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=res.reason
            )

    # 立即分派
    if event.status == "SOS":
        engine = request.app.state.dispatch_engine
        result = engine.dispatch(
            session,
            event,
            actor_id=ctx.user_id,
            actor_role=ctx.role,
        )
        session.refresh(event)
        if result.transition is not None:
            session.refresh(result.transition)
        engine.schedule_confirm_timers(request.app, event.id)

    return _event_to_out(session, event, "SYSTEM")
