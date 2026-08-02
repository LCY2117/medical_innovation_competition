"""分派路由：手动/自动分派、未确认递补触发。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.api.deps import AuthContext, get_current_user, get_session, require_roles
from app.api.events import _broadcast_update, _get_event_or_404, _event_to_out
from app.api.serializers import available_actions_for, list_assignments
from app.core.state_machine import Status
from app.models.event import EventAssignment
from app.schemas.event import DispatchRequest, EventOut

router = APIRouter(prefix="/events", tags=["分派"])


@router.post("/{event_id}/dispatch", response_model=EventOut)
async def dispatch_event(
    event_id: int,
    body: DispatchRequest,
    request: Request,
    ctx: AuthContext = Depends(
        require_roles("SYSTEM", "ADMIN")
    ),
    session: Session = Depends(get_session),
):
    """手动触发分派：打分选人 → 建分派记录 → SOS→DISPATCHED。"""
    event = _get_event_or_404(session, event_id)
    if event.status != Status.SOS.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"当前状态 {event.status} 无法分派（仅 SOS 可分派）",
        )

    engine = request.app.state.dispatch_engine
    result = engine.dispatch(
        session, event, actor_id=ctx.user_id, actor_role=ctx.role
    )
    session.refresh(event)
    transition = result.transition
    if transition is not None:
        session.refresh(transition)

    # 广播
    hub = request.app.state.hub
    await _broadcast_update(request, event, transition)
    await hub.broadcast_event(
        event.id,
        "ASSIGNMENT_UPDATE",
        lambda conn: {
            "assignments": [
                a.model_dump() for a in list_assignments(
                    request.app.state.session_factory(), event.id
                )
            ]
        },
        version=event.seq,
    )

    # 启动确认超时递补
    engine.schedule_confirm_timers(request.app, event.id)

    return _event_to_out(session, event, ctx.role)


@router.post("/{event_id}/dispatch/confirm-timeout")
def process_confirm_timeout(
    event_id: int,
    request: Request,
    ctx: AuthContext = Depends(
        require_roles("SYSTEM", "ADMIN")
    ),
    session: Session = Depends(get_session),
):
    """立即触发该事件所有 PENDING 分派的超时递补（联调/演示用）。"""
    rows = session.exec(
        select(EventAssignment).where(
            EventAssignment.event_id == event_id,
            EventAssignment.status == "PENDING",
        )
    ).all()
    processed = 0
    for row in rows:
        if request.app.state.dispatch_engine.process_confirm_timeout(
            request.app, row.id
        ):
            processed += 1
    return {"processed": processed}
