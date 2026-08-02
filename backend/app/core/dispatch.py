"""分派引擎（★核心）：可插拔策略 + 规则打分 + 超时自动分派 + 未确认递补。

- DispatchStrategy 协议：select(event, candidates) -> dict[role, list[ResponderProfile]]
  返回每个角色按优先级排序的候选列表（index 0 为主选）。
- RuleBasedStrategy：按设计契约打分：
    PRIME  = 0.40*skill + 0.35*(1-distance/5km) + 0.15*fitness + 0.10*health_active
    RUNNER = 0.55*(1-distance/5km) + 0.45*(1-aed_distance/5km)
    GUIDE  = 0.60*(1-distance/5km) + 0.40*venue_familiarity
- LLMStrategy：设计要求的接口占位（AI 加分点，不阻塞核心流程）。
- 超时：分派超时(DISPATCH_TIMEOUT) 自动 DISPATCH；未确认(CONFIRM_TIMEOUT) 置 DECLINED + 递补。
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from sqlmodel import Session, select

from app.core.state_machine import Action, Role, StateMachineEngine
from app.models.responder import ResponderProfile

if TYPE_CHECKING:  # 避免循环导入（models 不依赖 core）
    from app.models.event import Event

logger = logging.getLogger("lifereflex.dispatch")

REQUIRED_ROLES = [Role.PRIME.value, Role.RUNNER.value, Role.GUIDE.value]


@dataclass
class DispatchResult:
    """分派结果。"""

    assigned: dict[str, int] = field(default_factory=dict)  # role -> responder_id
    missing: list[str] = field(default_factory=list)  # 无候选的角色
    scores: dict[str, float] = field(default_factory=dict)
    reason: str = ""


class DispatchStrategy(Protocol):
    """分派策略协议：可插拔。"""

    name: str

    def select(
        self, event: "Event", candidates: list[ResponderProfile]
    ) -> dict[str, list[ResponderProfile]]:
        """返回 角色 -> 有序候选列表（0 为主选，其余为递补）。"""
        ...


def _dist_score(distance_km: float, radius_km: float = 5.0) -> float:
    """距离分：0~1，越近越高，超出半径归零。"""
    return max(0.0, 1.0 - distance_km / radius_km)


class RuleBasedStrategy:
    """规则打分策略（默认）。"""

    name: str = "rule-based"

    def select(
        self, event: "Event", candidates: list[ResponderProfile]
    ) -> dict[str, list[ResponderProfile]]:
        pool: dict[str, list[ResponderProfile]] = {}
        for role in REQUIRED_ROLES:
            # TIRED/离线/忙碌的施救者直接过滤
            role_cands = [
                c
                for c in candidates
                if c.role == role
                and c.responder_status == "AVAILABLE"
            ]
            role_cands.sort(key=lambda c: self.score(role, c), reverse=True)
            pool[role] = role_cands
        return pool

    def score(self, role: str, profile: ResponderProfile) -> float:
        dist = _dist_score(profile.distance_km)
        if role == Role.PRIME.value:
            return (
                0.40 * profile.skill_level
                + 0.35 * dist
                + 0.15 * profile.fitness
                + 0.10 * (1.0 if profile.health_active else 0.0)
            )
        if role == Role.RUNNER.value:
            aed_dist = _dist_score(profile.aed_distance_km)
            return 0.55 * dist + 0.45 * aed_dist
        if role == Role.GUIDE.value:
            return 0.60 * dist + 0.40 * profile.venue_familiarity
        return 0.0


class LLMStrategy:
    """LLM 决策接口占位（设计要求的预留，AI 加分点，不阻塞核心流程）。

    当前返回空选型并记录告警；接入真实 LLM 时实现同协议即可替换。
    """

    name: str = "llm"

    def select(
        self, event: "Event", candidates: list[ResponderProfile]
    ) -> dict[str, list[ResponderProfile]]:
        logger.warning(
            "LLMStrategy 为接口占位，未实际决策（event_id=%s），返回空选型",
            getattr(event, "id", None),
        )
        return {}


class DispatchEngine:
    """分派引擎：负责创建分派、执行自动分派、处理未确认递补。"""

    def __init__(
        self,
        strategy: DispatchStrategy,
        max_shocks: int = 3,
        confirm_timeout: float = 10.0,
    ) -> None:
        self.strategy = strategy
        self.max_shocks = max_shocks
        self.confirm_timeout = confirm_timeout
        self._sm = StateMachineEngine()

    # ---------- 打分 ----------
    def rank_candidates(
        self, event: "Event", candidates: list[ResponderProfile]
    ) -> dict[str, list[ResponderProfile]]:
        return self.strategy.select(event, candidates)

    # ---------- 分派 ----------
    def dispatch(
        self, session, event: "Event", actor_id: int | None = None, actor_role: str | None = None
    ) -> DispatchResult:
        """执行分派：为每个角色选择主选+递补，写入 event_assignments，
        并将事件 SOS → DISPATCHED。"""
        from app.models.event import EventAssignment, EventTransition

        candidates = session.exec(
            select(ResponderProfile).where(
                ResponderProfile.role.in_(REQUIRED_ROLES)
            )
        ).all()
        ranked = self.rank_candidates(event, candidates)

        result = DispatchResult()
        for role in REQUIRED_ROLES:
            ordered = ranked.get(role, [])
            if not ordered:
                result.missing.append(role)
                continue
            for priority, profile in enumerate(ordered[:2]):  # 主选 + 1 递补
                status = "PENDING" if priority == 0 else "BACKUP"
                score = 0.0
                if isinstance(self.strategy, RuleBasedStrategy):
                    score = self.strategy.score(role, profile)
                assignment = EventAssignment(
                    event_id=event.id,
                    responder_id=profile.user_id,
                    role=role,
                    status=status,
                    priority=priority,
                    score=round(score, 4),
                    reason=(
                        f"策略={self.strategy.name}"
                        f" 状态={profile.responder_status}"
                    ),
                )
                session.add(assignment)
                if priority == 0:
                    result.assigned[role] = profile.user_id
                    result.scores[role] = round(score, 4)

        result.reason = f"分派完成，策略={self.strategy.name}"
        # 事件推进：SOS → DISPATCHED，seq 自增（单调版本号）
        from app.core.state_machine import Status

        from_status = event.status  # 记录转移前状态（SOS），供时间线/证据使用
        event.status = Status.DISPATCHED.value
        event.seq += 1
        # 记录一条 SYSTEM/ADMIN 发起的 DISPATCH 转移
        result.transition = self._apply_dispatch_transition(
            session, event, from_status, actor_id, actor_role or Role.SYSTEM.value
        )
        session.commit()
        return result

    @staticmethod
    def _apply_dispatch_transition(
        session,
        event: "Event",
        from_status: str,
        actor_id: int | None,
        actor_role: str,
    ) -> "EventTransition":
        from app.core.state_machine import Action, Role, Status
        from app.models.event import EventTransition

        res = EventTransition(
            event_id=event.id,
            seq=event.seq,
            action=Action.DISPATCH.value,
            from_status=from_status,
            to_status=Status.DISPATCHED.value,
            actor_id=actor_id,
            actor_role=actor_role,
            duplicate=False,
            payload=json.dumps({"strategy": "rule-based"}, ensure_ascii=False),
        )
        session.add(res)
        return res

    # ---------- 超时自动分派 ----------
    async def schedule_auto_dispatch(
        self, app, event_id: int, delay: float
    ) -> asyncio.Task | None:
        """分派超时后自动 DISPATCH（若事件仍处于 SOS）。"""
        if delay <= 0:
            return None

        async def _task() -> None:
            await asyncio.sleep(delay)
            try:
                dispatched = await asyncio.to_thread(
                    self.auto_dispatch_if_pending, app, event_id
                )
                if dispatched:
                    # 回到事件循环内：启动确认超时计时器 + 向订阅者广播分派结果
                    self.schedule_confirm_timers(app, event_id)
                    await self.broadcast_auto_dispatch(app, event_id)
            except Exception:  # noqa: BLE001
                logger.exception("自动分派失败 event_id=%s", event_id)

        return asyncio.create_task(_task())

    def auto_dispatch_if_pending(self, app, event_id: int) -> bool:
        """事件仍为 SOS 时自动分派。返回是否分派。"""
        from app.api.deps import get_system_user
        from app.models.event import Event

        with app.state.session_factory() as session:
            event = session.get(Event, event_id)
            if event is None or event.status != "SOS":
                return False
            sys_user = get_system_user(session)
            self.dispatch(session, event, actor_id=sys_user.id if sys_user else None)
            return True

    async def broadcast_auto_dispatch(self, app, event_id: int) -> None:
        """自动分派后广播：EVENT_UPDATE + DISPATCH 转移 + ASSIGNMENT_UPDATE。

        手动分派（dispatch_api）已含广播；自动分派在 worker 线程中完成 DB 写入，
        需在事件循环中补发，否则订阅端收不到 DISPATCHED 状态（WS 实时同步要求）。
        """
        from app.api.serializers import (
            available_actions_for,
            event_dict_for_role,
            list_assignments,
        )
        from app.core.state_machine import Action, Status
        from app.models.event import Event, EventTransition

        hub = app.state.hub
        with app.state.session_factory() as session:
            event = session.get(Event, event_id)
            if event is None:
                return
            transition = session.exec(
                select(EventTransition)
                .where(
                    EventTransition.event_id == event_id,
                    EventTransition.action == Action.DISPATCH.value,
                )
                .order_by(EventTransition.id.desc())
            ).first()
            assignments = list_assignments(session, event.id)
            timeline_payload: dict = {"transitions": []}
            if transition is not None:
                timeline_payload = {
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
                    }
                }

            await hub.broadcast_event(
                event.id,
                "EVENT_UPDATE",
                lambda conn: event_dict_for_role(event, conn.role),
                version=event.seq,
            )
            await hub.broadcast_event(
                event.id,
                "TRANSITION_ADDED",
                lambda conn: {
                    **timeline_payload,
                    "available_actions": available_actions_for(event, conn.role),
                },
                version=event.seq,
            )
            await hub.broadcast_event(
                event.id,
                "ASSIGNMENT_UPDATE",
                lambda conn: {
                    "assignments": [a.model_dump() for a in assignments]
                },
                version=event.seq,
            )

    # ---------- 未确认递补 ----------
    def schedule_confirm_timers(self, app, event_id: int) -> list[asyncio.Task]:
        """为每个主选分派启动确认超时计时器。"""
        if self.confirm_timeout <= 0:
            return []
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # 非事件循环上下文（如 auto_dispatch 的 worker 线程）→ 跳过计时器，
            # 避免 asyncio.create_task 抛出 "no running event loop"。
            logger.warning(
                "schedule_confirm_timers 在非事件循环上下文被调用，跳过计时器 event_id=%s",
                event_id,
            )
            return []
        tasks = []

        async def _timer(assignment_id: int) -> None:
            await asyncio.sleep(self.confirm_timeout)
            try:
                await asyncio.to_thread(
                    self.process_confirm_timeout, app, assignment_id
                )
            except Exception:  # noqa: BLE001
                logger.exception(
                    "确认超时处理失败 assignment_id=%s", assignment_id
                )

        with app.state.session_factory() as session:
            from app.models.event import EventAssignment

            rows = session.exec(
                select(EventAssignment).where(
                    EventAssignment.event_id == event_id,
                    EventAssignment.status == "PENDING",
                )
            ).all()
            for row in rows:
                tasks.append(asyncio.create_task(_timer(row.id)))
        return tasks

    def process_confirm_timeout(self, app, assignment_id: int) -> bool:
        """PENDING 超时未确认 → DECLINED，并把该角色第一个 BACKUP 递补为 PENDING。"""
        from app.models.event import EventAssignment

        with app.state.session_factory() as session:
            assignment = session.get(EventAssignment, assignment_id)
            if assignment is None or assignment.status != "PENDING":
                return False

            assignment.status = "DECLINED"
            session.add(assignment)

            # 递补
            backup = session.exec(
                select(EventAssignment)
                .where(
                    EventAssignment.event_id == assignment.event_id,
                    EventAssignment.role == assignment.role,
                    EventAssignment.status == "BACKUP",
                )
                .order_by(EventAssignment.priority.asc())
            ).first()
            if backup is not None:
                backup.status = "PENDING"
                session.add(backup)
            session.commit()
            return True
