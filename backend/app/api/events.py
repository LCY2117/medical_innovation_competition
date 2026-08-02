"""事件路由：SOS / 详情 / 动作 / 时间线 / 证据。"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.api.deps import AuthContext, get_current_user, get_session
from app.api.serializers import (
    available_actions_for,
    event_dict_for_role,
    list_assignments,
    list_timeline,
)
from app.core import evidence as evidence_mod
from app.core.state_machine import (
    ACTIVE_STATES,
    Action,
    EventState,
    StateMachineEngine,
    Status,
)
from app.models.event import Event, EventTransition
from app.models.user import User, utcnow
from app.schemas.event import (
    ActionRequest,
    ActiveEventResponse,
    ActionResult,
    EventDetail,
    EventOut,
    SOSRequest,
    TransitionOut,
)

router = APIRouter(prefix="/events", tags=["事件"])

_sm = StateMachineEngine()


def _get_event_or_404(session: Session, event_id: int) -> Event:
    event = session.get(Event, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="事件不存在"
        )
    return event


def _event_to_out(session: Session, event: Event, role: str) -> EventOut:
    from app.schemas.event import AvailableAction

    return EventOut(
        id=event.id,
        patient_id=event.patient_id,
        status=event.status,
        seq=event.seq,
        prime_confirmed=event.prime_confirmed,
        runner_confirmed=event.runner_confirmed,
        guide_confirmed=event.guide_confirmed,
        ambulance_arrived=event.ambulance_arrived,
        shock_count=event.shock_count,
        started_at=event.started_at,
        created_at=event.created_at,
        updated_at=event.updated_at,
        location=event.location,
        latitude=event.latitude,
        longitude=event.longitude,
        assignments=list_assignments(session, event.id),
        available_actions=[
            AvailableAction(**a) for a in available_actions_for(event, role)
        ],
    )


def _persist_state(event: Event, state: EventState) -> None:
    event.status = state.status
    event.seq = state.seq
    event.prime_confirmed = state.prime_confirmed
    event.runner_confirmed = state.runner_confirmed
    event.guide_confirmed = state.guide_confirmed
    event.ambulance_arrived = state.ambulance_arrived
    event.shock_count = state.shock_count
    event.updated_at = utcnow()


def _load_state(event: Event) -> EventState:
    return EventState(
        status=event.status,
        seq=event.seq,
        prime_confirmed=event.prime_confirmed,
        runner_confirmed=event.runner_confirmed,
        guide_confirmed=event.guide_confirmed,
        ambulance_arrived=event.ambulance_arrived,
        shock_count=event.shock_count,
    )


def _record_transition(
    session: Session,
    event: Event,
    action: str,
    state_from: EventState,
    state_to: EventState,
    ctx: AuthContext,
    duplicate: bool,
    payload: dict | None = None,
) -> EventTransition:
    t = EventTransition(
        event_id=event.id,
        seq=state_to.seq,
        action=action,
        from_status=state_from.status,
        to_status=state_to.status,
        actor_id=ctx.user_id,
        actor_role=ctx.role,
        duplicate=duplicate,
        payload=json.dumps(payload or {}, ensure_ascii=False),
    )
    session.add(t)
    return t


def _already_applied(
    session: Session, event_id: int, action: str, actor_id: int
) -> bool:
    row = session.exec(
        select(EventTransition).where(
            EventTransition.event_id == event_id,
            EventTransition.action == action,
            EventTransition.actor_id == actor_id,
            EventTransition.duplicate == False,  # noqa: E712
        )
    ).first()
    return row is not None


async def _broadcast_update(
    request: Request, event: Event, transition: EventTransition | None = None
) -> None:
    """向订阅该事件的连接广播事件更新 + 时间线追加。"""
    hub = request.app.state.hub

    await hub.broadcast_event(
        event.id,
        "EVENT_UPDATE",
        lambda conn: event_dict_for_role(event, conn.role),
        version=event.seq,
    )
    if transition is not None:
        await hub.broadcast_event(
            event.id,
            "TRANSITION_ADDED",
            lambda conn: {
                "transition": {
                    "id": transition.id,
                    "seq": transition.seq,
                    "action": transition.action,
                    "from_status": transition.from_status,
                    "to_status": transition.to_status,
                    "actor_role": transition.actor_role,
                    "duplicate": transition.duplicate,
                    "payload": json.loads(transition.payload or "{}"),
                    "created_at": transition.created_at.isoformat()
                    if transition.created_at
                    else None,
                },
                "available_actions": available_actions_for(
                    event, conn.role
                ),
            },
            version=event.seq,
        )


# ---------- 路由 ----------

@router.post("/sos", response_model=EventOut, status_code=201)
async def create_sos(
    body: SOSRequest,
    request: Request,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """患者发起 SOS（后端校验无进行中事件，防误触）。"""
    settings = request.app.state.settings
    if ctx.role != "PATIENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅患者可发起 SOS",
        )

    # 防误触：同一患者已有进行中事件则拒绝
    active = session.exec(
        select(Event).where(
            Event.patient_id == ctx.user_id,
            Event.status.in_(ACTIVE_STATES),
        )
    ).first()
    if active is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="已有进行中的事件，无法重复发起 SOS",
        )

    event = Event(
        patient_id=ctx.user_id,
        status=Status.CREATED.value,
        seq=0,
        location=body.location,
        latitude=body.latitude,
        longitude=body.longitude,
    )
    session.add(event)
    session.commit()
    session.refresh(event)

    # 执行 SOS_TRIGGERED
    action = await apply_action(
        request,
        session,
        event.id,
        ctx,
        ActionRequest(action=Action.SOS_TRIGGERED.value, metadata={"note": body.note}),
    )
    if not action.applied:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=action.reason,
        )

    # 启动分派超时自动分派
    await request.app.state.dispatch_engine.schedule_auto_dispatch(
        request.app, event.id, settings.dispatch_timeout
    )
    return _event_to_out(session, event, ctx.role)


@router.get("/active", response_model=ActiveEventResponse)
def get_active_event(
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """返回当前最近的非归档事件（响应端自动发现并订阅用）。

    - 优先返回 ACTIVE_STATES（SOS..HANDOVER）中最新的活跃事件；
    - 无活跃事件时，回退返回最近的非 ARCHIVED 事件（兼容 CREATED 残留）；
    - 都没有则 event=None。
    任意登录用户可查；注意本路由需定义在 /{event_id} 之前避免路径冲突。
    """
    event = session.exec(
        select(Event)
        .where(Event.status.in_(ACTIVE_STATES))
        .order_by(Event.id.desc())
    ).first()
    if event is None:
        event = session.exec(
            select(Event)
            .where(Event.status != Status.ARCHIVED.value)
            .order_by(Event.id.desc())
        ).first()
    if event is None:
        return ActiveEventResponse(event=None)
    return ActiveEventResponse(event=_event_to_out(session, event, ctx.role))


@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: int,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    event = _get_event_or_404(session, event_id)
    return _event_to_out(session, event, ctx.role)


@router.get("/{event_id}/actions", response_model=list)
def get_actions(
    event_id: int,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """获取当前用户可执行动作（服务端权威推导）。"""
    event = _get_event_or_404(session, event_id)
    return available_actions_for(event, ctx.role)


@router.post("/{event_id}/actions", response_model=ActionResult)
async def submit_action(
    event_id: int,
    body: ActionRequest,
    request: Request,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """提交状态机动作。"""
    result = await apply_action(request, session, event_id, ctx, body)
    return result


async def apply_action(
    request: Request,
    session: Session,
    event_id: int,
    ctx: AuthContext,
    body: ActionRequest,
) -> ActionResult:
    """状态机动作核心执行器（events / dispatch_api / demo 共用）。"""
    event = _get_event_or_404(session, event_id)
    settings = request.app.state.settings
    action = body.action.upper()

    if action == Action.DISPATCH.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DISPATCH 请使用分派接口 /events/{id}/dispatch",
        )

    # 幂等：同一 (action, actor) 已成功过且为不可重复动作 → 直接判 duplicate
    # （先于状态/守卫校验，保证“重复提交 → duplicate=true，seq 不增长”）
    from app.core.state_machine import REPEATABLE_ACTIONS

    if action not in REPEATABLE_ACTIONS and _already_applied(
        session, event_id, action, ctx.user_id
    ):
        return ActionResult(
            applied=False,
            duplicate=True,
            from_status=event.status,
            to_status=event.status,
            reason="动作已由该角色提交过（幂等），seq 不增长",
            new_seq=event.seq,
        )

    # 角色/状态/守卫校验（服务端权威）
    ok, reason = _sm.can(_load_state(event), action, ctx.role)
    if not ok:
        return ActionResult(
            applied=False,
            from_status=event.status,
            to_status=event.status,
            reason=reason,
            new_seq=event.seq,
        )

    # 额外业务校验
    # 说明：RESPONSE_CONFIRMED 按设计为“角色 + 状态 + 守卫”驱动（见 available_actions
    # 推导），无需分派先行；HANDOVER 的“已确认参与者”守卫已在状态机内校验。
    # （可选加固：如需仅允许被指派者确认，可在此按 event_assignments 校验。）

    state_from = _load_state(event)
    already = _already_applied(session, event_id, action, ctx.user_id)
    result = _sm.transition(
        state_from,
        action,
        ctx.role,
        actor_id=ctx.user_id,
        already_applied=already,
        max_shocks=settings.max_shocks,
    )

    if not result.applied:
        return ActionResult(
            applied=False,
            duplicate=result.duplicate,
            from_status=state_from.status,
            to_status=state_from.status,
            reason=result.reason,
            new_seq=event.seq,
        )

    # 持久化（state_from 已被引擎原地修改为转移后状态）
    if action == Action.SOS_TRIGGERED.value and event.started_at is None:
        event.started_at = datetime.now(timezone.utc).replace(tzinfo=None)
    _persist_state(event, state_from)
    transition = _record_transition(
        session,
        event,
        action,
        state_from,
        state_from,
        ctx,
        duplicate=False,
        payload=body.metadata,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    session.refresh(transition)

    # 广播
    await _broadcast_update(request, event, transition)

    return ActionResult(
        applied=True,
        duplicate=False,
        from_status=result.from_status,
        to_status=result.to_status,
        reason="",
        new_seq=event.seq,
        event=_event_to_out(session, event, ctx.role),
    )


@router.get("/{event_id}/timeline", response_model=list[TransitionOut])
def get_timeline(
    event_id: int,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    _get_event_or_404(session, event_id)
    return list_timeline(session, event_id)


@router.get("/{event_id}/evidence")
def get_evidence(
    event_id: int,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """事件证据包（JSON）。"""
    event = _get_event_or_404(session, event_id)
    return evidence_mod.build_evidence_bundle(session, event)


@router.get("/{event_id}/evidence.zip")
def get_evidence_zip(
    event_id: int,
    ctx: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """事件证据包（ZIP）。"""
    event = _get_event_or_404(session, event_id)
    bundle = evidence_mod.build_evidence_bundle(session, event)
    data = evidence_mod.build_zip_bytes(bundle)
    return StreamingResponse(
        iter([data]),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="event-{event_id}-evidence.zip"'
        },
    )
