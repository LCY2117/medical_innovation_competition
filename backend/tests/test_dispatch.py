"""分派引擎单测：打分排序 / TIRED 过滤 / 缺角色超时 / 自动分派 / 递补 / LLM 占位。"""
from __future__ import annotations

from app.core.dispatch import DispatchEngine, LLMStrategy, RuleBasedStrategy
from app.core.state_machine import Status
from app.models.responder import ResponderProfile


def _profile(role, *, skill=0.5, fitness=0.5, health=True, venue=0.5,
             dist=5.0, aed_dist=5.0, status="AVAILABLE", uid=1):
    return ResponderProfile(
        user_id=uid, role=role, responder_status=status,
        skill_level=skill, fitness=fitness, health_active=health,
        venue_familiarity=venue, distance_km=dist, aed_distance_km=aed_dist,
    )


# ---------------- 打分公式 ----------------

def test_prime_score_formula():
    s = RuleBasedStrategy()
    far = _profile("PRIME", skill=0.5, fitness=0.5, health=True, dist=5.0)
    near = _profile("PRIME", skill=0.5, fitness=0.5, health=True, dist=0.0)
    assert s.score("PRIME", far) < s.score("PRIME", near)
    # 技能差异
    skilled = _profile("PRIME", skill=0.9, fitness=0.5, health=True, dist=2.0)
    assert s.score("PRIME", skilled) > s.score("PRIME", near)


def test_runner_score_formula():
    s = RuleBasedStrategy()
    with_aed = _profile("RUNNER", dist=1.0, aed_dist=0.2)
    without_aed = _profile("RUNNER", dist=1.0, aed_dist=5.0)
    assert s.score("RUNNER", with_aed) > s.score("RUNNER", without_aed)


def test_guide_score_formula():
    s = RuleBasedStrategy()
    familiar = _profile("GUIDE", venue=0.95, dist=2.0)
    stranger = _profile("GUIDE", venue=0.2, dist=2.0)
    assert s.score("GUIDE", familiar) > s.score("GUIDE", stranger)


# ---------------- TIRED 过滤与排序 ----------------

def test_tired_and_offline_filtered():
    s = RuleBasedStrategy()
    best = _profile("PRIME", skill=0.99, dist=0.2, uid=1)
    tired = _profile("PRIME", skill=0.99, dist=0.1, uid=2, status="TIRED")
    offline = _profile("PRIME", skill=0.99, dist=0.1, uid=3, status="OFFLINE")
    pool = s.select(None, [best, tired, offline])
    assert len(pool["PRIME"]) == 1
    assert pool["PRIME"][0].user_id == 1


def test_rank_order_best_first():
    s = RuleBasedStrategy()
    c1 = _profile("PRIME", skill=0.9, fitness=0.9, health=True, dist=1.0, uid=1)
    c2 = _profile("PRIME", skill=0.5, fitness=0.5, health=True, dist=4.0, uid=2)
    pool = s.select(None, [c2, c1])
    assert [p.user_id for p in pool["PRIME"]] == [1, 2]


# ---------------- 集成：DB 分派 ----------------

def _create_sos_event(app, session):
    from app.api.deps import get_system_user
    from app.core.state_machine import Action
    from app.models.event import Event
    from app.models.user import User
    from sqlmodel import select

    patient = session.exec(
        select(User).where(User.role == "PATIENT")
    ).first()
    event = Event(patient_id=patient.id, status="SOS", seq=1)
    session.add(event)
    session.commit()
    session.refresh(event)
    sys_user = get_system_user(session)
    return event, sys_user


def test_dispatch_creates_assignments_and_advances(app, session):
    from sqlmodel import select

    engine = app.state.dispatch_engine
    event, sys_user = _create_sos_event(app, session)

    result = engine.dispatch(session, event, actor_id=sys_user.id)

    from app.models.event import EventAssignment

    rows = session.exec(
        select(EventAssignment).where(EventAssignment.event_id == event.id)
    ).all()
    roles = {r.role for r in rows}
    assert {"PRIME", "RUNNER", "GUIDE"} <= roles
    # 每个角色有主选 + 递补
    assert sum(1 for r in rows if r.status == "PENDING") == 3
    assert sum(1 for r in rows if r.status == "BACKUP") == 3
    # 主选必须是种子里的演示用户（最高分）
    from app.models.user import User

    primes = [r for r in rows if r.role == "PRIME" and r.status == "PENDING"]
    responder = session.get(User, primes[0].responder_id)
    assert responder.username == "prime"

    # 事件推进到 DISPATCHED，seq 自增
    session.refresh(event)
    assert event.status == Status.DISPATCHED.value
    assert event.seq == 2
    assert result.missing == []


def test_dispatch_missing_role(app, session):
    """缺角色：PRIME 全部不可用 → missing 含 PRIME，事件仍可分派。"""
    from sqlmodel import update

    from app.models.responder import ResponderProfile

    session.exec(
        update(ResponderProfile)
        .where(ResponderProfile.role == "PRIME")
        .values(responder_status="TIRED")
    )
    session.commit()

    engine = app.state.dispatch_engine
    event, sys_user = _create_sos_event(app, session)
    result = engine.dispatch(session, event, actor_id=sys_user.id)
    assert "PRIME" in result.missing
    assert result.assigned.get("PRIME") is None
    session.refresh(event)
    assert event.status == Status.DISPATCHED.value


def test_auto_dispatch_when_pending(app, session):
    """超时自动分派：仅当事件仍为 SOS 时才触发。"""
    engine = app.state.dispatch_engine
    event, _ = _create_sos_event(app, session)

    # 第一次触发 → 分派成功
    assert engine.auto_dispatch_if_pending(app, event.id) is True
    # 事件已 DISPATCHED → 不再触发
    assert engine.auto_dispatch_if_pending(app, event.id) is False

    from app.models.event import Event

    session.expire_all()
    ev = session.get(Event, event.id)
    assert ev.status == Status.DISPATCHED.value


def test_confirm_timeout_declined_and_promote(app, session):
    """未确认超时：PENDING → DECLINED，BACKUP 递补为 PENDING。"""
    from sqlmodel import select

    from app.models.event import EventAssignment

    engine = app.state.dispatch_engine
    event, sys_user = _create_sos_event(app, session)
    engine.dispatch(session, event, actor_id=sys_user.id)

    primary = session.exec(
        select(EventAssignment).where(
            EventAssignment.event_id == event.id,
            EventAssignment.status == "PENDING",
            EventAssignment.role == "PRIME",
        )
    ).first()
    backup = session.exec(
        select(EventAssignment).where(
            EventAssignment.event_id == event.id,
            EventAssignment.role == "PRIME",
            EventAssignment.status == "BACKUP",
        )
    ).first()
    assert primary is not None and backup is not None

    assert engine.process_confirm_timeout(app, primary.id) is True

    session.expire_all()
    p2 = session.get(EventAssignment, primary.id)
    b2 = session.get(EventAssignment, backup.id)
    assert p2.status == "DECLINED"
    assert b2.status == "PENDING"


# ---------------- LLM 占位 ----------------

def test_llm_strategy_placeholder():
    strategy = LLMStrategy()
    assert strategy.name == "llm"
    # 占位：返回空选型，不抛异常
    picks = strategy.select(None, [])
    assert picks == {}
