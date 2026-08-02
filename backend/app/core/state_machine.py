"""事件状态机引擎（★核心）。

设计契约：
    CREATED → SOS → DISPATCHED → CPR → AED_PICKED → AED_DELIVERED
    → AED_ANALYZING → SHOCK_DELIVERED → HANDOVER → ARCHIVED

要点：
    1. 状态转移表驱动，所有合法动作/角色/来源状态/守卫显式声明。
    2. 单调性守卫：禁止状态回退（除颤往返 SHOCK_DELIVERED→AED_ANALYZING 例外）。
    3. 幂等：同一 (event, action, actor) 重复提交 → duplicate=True，seq 不增长。
    4. available_actions 由后端依据 status + role + 守卫推导并下发。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class Role(str, Enum):
    PATIENT = "PATIENT"
    PRIME = "PRIME"
    RUNNER = "RUNNER"
    GUIDE = "GUIDE"
    SYSTEM = "SYSTEM"
    ADMIN = "ADMIN"


class Status(str, Enum):
    CREATED = "CREATED"
    SOS = "SOS"
    DISPATCHED = "DISPATCHED"
    CPR = "CPR"
    AED_PICKED = "AED_PICKED"
    AED_DELIVERED = "AED_DELIVERED"
    AED_ANALYZING = "AED_ANALYZING"
    SHOCK_DELIVERED = "SHOCK_DELIVERED"
    HANDOVER = "HANDOVER"
    ARCHIVED = "ARCHIVED"


class Action(str, Enum):
    SOS_TRIGGERED = "SOS_TRIGGERED"
    RESPONSE_CONFIRMED = "RESPONSE_CONFIRMED"
    DISPATCH = "DISPATCH"
    CPR_STARTED = "CPR_STARTED"
    AED_PICKED = "AED_PICKED"
    AED_DELIVERED = "AED_DELIVERED"
    AED_ANALYSIS_STARTED = "AED_ANALYSIS_STARTED"
    AED_SHOCK_DELIVERED = "AED_SHOCK_DELIVERED"
    AMBULANCE_ARRIVED = "AMBULANCE_ARRIVED"
    HANDOVER_COMPLETED = "HANDOVER_COMPLETED"
    ARCHIVE = "ARCHIVE"


# 状态单调排名（用于回退守卫）
STATUS_RANK: dict[str, int] = {
    Status.CREATED.value: 0,
    Status.SOS.value: 1,
    Status.DISPATCHED.value: 2,
    Status.CPR.value: 3,
    Status.AED_PICKED.value: 4,
    Status.AED_DELIVERED.value: 5,
    Status.AED_ANALYZING.value: 6,
    Status.SHOCK_DELIVERED.value: 7,
    Status.HANDOVER.value: 8,
    Status.ARCHIVED.value: 9,
}

# 事件生命周期中的“活跃状态”（CREATED 之前、ARCHIVED 之后都不算）
ACTIVE_STATES = frozenset(
    {
        Status.SOS.value,
        Status.DISPATCHED.value,
        Status.CPR.value,
        Status.AED_PICKED.value,
        Status.AED_DELIVERED.value,
        Status.AED_ANALYZING.value,
        Status.SHOCK_DELIVERED.value,
        Status.HANDOVER.value,
    }
)

# 可重复的动作（幂等例外）：允许在守卫允许范围内多次执行
REPEATABLE_ACTIONS = frozenset(
    {Action.AED_ANALYSIS_STARTED.value, Action.AED_SHOCK_DELIVERED.value}
)

# 动作中文标签（前端“一屏一动作”渲染用）
ACTION_LABELS: dict[str, str] = {
    Action.SOS_TRIGGERED.value: "发起SOS",
    Action.RESPONSE_CONFIRMED.value: "确认响应",
    Action.DISPATCH.value: "立即分派",
    Action.CPR_STARTED.value: "开始CPR",
    Action.AED_PICKED.value: "已取AED",
    Action.AED_DELIVERED.value: "AED已送达",
    Action.AED_ANALYSIS_STARTED.value: "开始AED分析",
    Action.AED_SHOCK_DELIVERED.value: "实施除颤",
    Action.AMBULANCE_ARRIVED.value: "救护车已到场",
    Action.HANDOVER_COMPLETED.value: "完成交接",
    Action.ARCHIVE.value: "归档事件",
}


@dataclass
class EventState:
    """状态机所需的最小状态视图（与 Event 模型分离，便于纯逻辑单测）。"""

    status: str = Status.CREATED.value
    seq: int = 0
    prime_confirmed: bool = False
    runner_confirmed: bool = False
    guide_confirmed: bool = False
    ambulance_arrived: bool = False
    shock_count: int = 0


@dataclass
class TransitionDef:
    """单条转移定义。"""

    action: str
    roles: list[str]  # 允许提交该动作的角色
    from_states: list[str]  # 允许发起该动作的状态
    to: Optional[str] = None  # 目标状态；None 表示状态不变
    # 守卫：(state, actor_role) -> (ok, reason)
    guard: Optional[Callable[[EventState, str], tuple[bool, str]]] = None
    # 副作用：修改 state 的并行标志
    effect: Optional[Callable[[EventState, str], None]] = None


@dataclass
class TransitionResult:
    """转移执行结果。"""

    applied: bool = False
    duplicate: bool = False
    reason: str = ""
    from_status: str = ""
    to_status: str = ""
    new_seq: int = 0  # 幂等时不增长
    shock_count: int = 0


# ---------- 守卫/副作用 ----------

def _confirm_flag(state: EventState, role: str) -> str:
    return {
        Role.PRIME.value: "prime_confirmed",
        Role.RUNNER.value: "runner_confirmed",
        Role.GUIDE.value: "guide_confirmed",
    }.get(role, "")


def _guard_actor_confirmed(
    state: EventState, role: str
) -> tuple[bool, str]:
    """该角色的确认标志必须为真。"""
    flag = _confirm_flag(state, role)
    if not flag:
        return False, f"角色 {role} 不是参与确认角色"
    if getattr(state, flag):
        return True, ""
    return False, f"角色 {role} 尚未确认响应"


def _guard_confirm_not_already(
    state: EventState, role: str
) -> tuple[bool, str]:
    """该角色尚未确认响应（确认过的不再出现在 available_actions）。

    保证“一屏一动作”：已确认过响应的角色只看得到下一步执行动作
    （如 CPR_STARTED / AED_PICKED / AMBULANCE_ARRIVED），
    而非重复出现 RESPONSE_CONFIRMED。
    """
    flag = _confirm_flag(state, role)
    if not flag:
        return False, f"角色 {role} 不是参与确认角色"
    if getattr(state, flag):
        return False, f"角色 {role} 已确认过响应"
    return True, ""


def _guard_ambulance_not_arrived(
    state: EventState, role: str
) -> tuple[bool, str]:
    """救护车尚未到场（到场后 AMBULANCE_ARRIVED 不再出现，
    让 HANDOVER_COMPLETED 成为 GUIDE 的下一个主行动）。"""
    if not _role_confirmed(state, role):
        return False, f"角色 {role} 尚未确认响应"
    if state.ambulance_arrived:
        return False, "救护车已到场"
    return True, ""


def _guard_aed_analysis(state: EventState, role: str) -> tuple[bool, str]:
    """AED 分析需 RUNNER 已送达，且未超过除颤上限。"""
    if state.status not in (
        Status.AED_DELIVERED.value,
        Status.SHOCK_DELIVERED.value,
    ):
        return False, "AED 尚未送达，无法开始分析"
    if state.shock_count >= 3:
        return False, "已达除颤上限(3次)，无法再次分析"
    return True, ""


def _guard_shock(state: EventState, role: str) -> tuple[bool, str]:
    if state.shock_count >= 3:
        return False, "已达除颤上限(3次)"
    return True, ""


def _guard_handover(state: EventState, role: str) -> tuple[bool, str]:
    # “任意已确认参与者”：需该角色已确认响应，且救护车已到场
    if not _role_confirmed(state, role):
        return False, f"角色 {role} 尚未确认响应，不能完成交接"
    if not state.ambulance_arrived:
        return False, "救护车尚未到场，无法交接"
    return True, ""


def _effect_shock(state: EventState, role: str) -> None:
    state.shock_count += 1


def _effect_confirm(state: EventState, role: str) -> None:
    """RESPONSE_CONFIRMED 副作用：按提交角色置确认标志。"""
    flag = _confirm_flag(state, role)
    if flag:
        setattr(state, flag, True)


def _effect_ambulance(state: EventState, role: str) -> None:
    state.ambulance_arrived = True


def _effect_sos(state: EventState, role: str) -> None:
    pass


# ---------- 转移表 ----------

def _all_after(*statuses: str) -> list[str]:
    """返回给定状态之后的全部活跃状态（含给定状态）。"""
    ranks = {s: i for i, s in enumerate(
        [
            Status.CREATED.value,
            Status.SOS.value,
            Status.DISPATCHED.value,
            Status.CPR.value,
            Status.AED_PICKED.value,
            Status.AED_DELIVERED.value,
            Status.AED_ANALYZING.value,
            Status.SHOCK_DELIVERED.value,
            Status.HANDOVER.value,
            Status.ARCHIVED.value,
        ]
    )}
    min_rank = min(ranks[s] for s in statuses)
    return [s for s, r in ranks.items() if r >= min_rank]


CONFIRM_ROLES = [Role.PRIME.value, Role.RUNNER.value, Role.GUIDE.value]

TRANSITIONS: dict[str, TransitionDef] = {}


def _register(t: TransitionDef) -> None:
    TRANSITIONS[t.action] = t


# SOS_TRIGGERED：患者发起。from_states 放宽（任何未归档状态皆可提交），
# 由守卫做“防误触”校验：已有进行中事件则拒绝。
_register(
    TransitionDef(
        action=Action.SOS_TRIGGERED.value,
        roles=[Role.PATIENT.value],
        from_states=_all_after(Status.CREATED.value),  # CREATED..HANDOVER
        to=Status.SOS.value,
        guard=lambda s, r: (
            (True, "")
            if s.status == Status.CREATED.value
            else (False, "已有进行中的事件，无法重复发起SOS")
        ),
        effect=_effect_sos,
    )
)

# RESPONSE_CONFIRMED：三个施救角色确认响应，状态不变
# 守卫：已确认过响应的角色不再可见（available_actions 边界，见 _guard_confirm_not_already）
_register(
    TransitionDef(
        action=Action.RESPONSE_CONFIRMED.value,
        roles=CONFIRM_ROLES,
        from_states=list(ACTIVE_STATES),
        to=None,  # 状态不变
        guard=_guard_confirm_not_already,
        effect=_effect_confirm,
    )
)

# DISPATCH：系统/管理员分派，SOS → DISPATCHED
_register(
    TransitionDef(
        action=Action.DISPATCH.value,
        roles=[Role.SYSTEM.value, Role.ADMIN.value],
        from_states=[Status.SOS.value],
        to=Status.DISPATCHED.value,
    )
)

# CPR_STARTED：PRIME 开始 CPR（需 PRIME 已确认）
_register(
    TransitionDef(
        action=Action.CPR_STARTED.value,
        roles=[Role.PRIME.value],
        from_states=[Status.DISPATCHED.value],
        to=Status.CPR.value,
        guard=_guard_actor_confirmed,
    )
)

# AED_PICKED：RUNNER 取到 AED（需 RUNNER 已确认）
_register(
    TransitionDef(
        action=Action.AED_PICKED.value,
        roles=[Role.RUNNER.value],
        from_states=[Status.DISPATCHED.value, Status.CPR.value],
        to=Status.AED_PICKED.value,
        guard=_guard_actor_confirmed,
    )
)

# AED_DELIVERED：RUNNER 送达 AED
_register(
    TransitionDef(
        action=Action.AED_DELIVERED.value,
        roles=[Role.RUNNER.value],
        from_states=[Status.AED_PICKED.value],
        to=Status.AED_DELIVERED.value,
        guard=_guard_actor_confirmed,
    )
)

# AED_ANALYSIS_STARTED：PRIME 开始分析（需 RUNNER 已送达）
_register(
    TransitionDef(
        action=Action.AED_ANALYSIS_STARTED.value,
        roles=[Role.PRIME.value],
        from_states=[
            Status.AED_DELIVERED.value,
            Status.SHOCK_DELIVERED.value,
        ],
        to=Status.AED_ANALYZING.value,
        guard=_guard_aed_analysis,
    )
)

# AED_SHOCK_DELIVERED：PRIME 实施除颤（上限 3 次）
_register(
    TransitionDef(
        action=Action.AED_SHOCK_DELIVERED.value,
        roles=[Role.PRIME.value],
        from_states=[Status.AED_ANALYZING.value],
        to=Status.SHOCK_DELIVERED.value,
        guard=_guard_shock,
        effect=_effect_shock,
    )
)

# AMBULANCE_ARRIVED：GUIDE 确认救护车到场，状态不变
# 守卫：救护车到场后该动作不再出现（让 HANDOVER_COMPLETED 成为下一主行动）
_register(
    TransitionDef(
        action=Action.AMBULANCE_ARRIVED.value,
        roles=[Role.GUIDE.value],
        from_states=[
            Status.DISPATCHED.value,
            Status.CPR.value,
            Status.AED_PICKED.value,
            Status.AED_DELIVERED.value,
            Status.AED_ANALYZING.value,
            Status.SHOCK_DELIVERED.value,
        ],
        to=None,
        guard=_guard_ambulance_not_arrived,
        effect=_effect_ambulance,
    )
)

# HANDOVER_COMPLETED：任意已确认施救者完成交接（需救护车已到场）
_register(
    TransitionDef(
        action=Action.HANDOVER_COMPLETED.value,
        roles=CONFIRM_ROLES,
        from_states=[
            Status.DISPATCHED.value,
            Status.CPR.value,
            Status.AED_PICKED.value,
            Status.AED_DELIVERED.value,
            Status.AED_ANALYZING.value,
            Status.SHOCK_DELIVERED.value,
        ],
        to=Status.HANDOVER.value,
        guard=_guard_handover,
    )
)

# ARCHIVE：系统/管理员归档，仅 HANDOVER 之后
_register(
    TransitionDef(
        action=Action.ARCHIVE.value,
        roles=[Role.SYSTEM.value, Role.ADMIN.value],
        from_states=[Status.HANDOVER.value],
        to=Status.ARCHIVED.value,
    )
)


# ---------- 引擎 ----------

def _role_confirmed(state: EventState, role: str) -> bool:
    flag = _confirm_flag(state, role)
    return bool(flag) and getattr(state, flag)


def is_valid_action(action: str) -> bool:
    return action in TRANSITIONS


def is_active_status(status: str) -> bool:
    return status in ACTIVE_STATES


class StateMachineEngine:
    """纯逻辑状态机引擎，不依赖数据库。"""

    def can(
        self, state: EventState, action: str, actor_role: str
    ) -> tuple[bool, str]:
        """校验动作在当前状态/角色/守卫下是否可执行。"""
        t = TRANSITIONS.get(action)
        if t is None:
            return False, f"未知动作 {action}"
        if actor_role not in t.roles:
            return False, f"角色 {actor_role} 无权执行 {action}"
        if state.status not in t.from_states:
            return (
                False,
                f"当前状态 {state.status} 不允许执行 {action}"
                f"（仅 {', '.join(t.from_states)}）",
            )
        if t.guard is not None:
            ok, reason = t.guard(state, actor_role)
            if not ok:
                return False, reason
        return True, ""

    def available_actions(
        self, state: EventState, actor_role: str
    ) -> list[dict]:
        """推导当前用户可执行的动作列表（服务端权威，前端据此渲染）。"""
        result: list[dict] = []
        for action, t in TRANSITIONS.items():
            ok, _ = self.can(state, action, actor_role)
            if not ok:
                continue
            result.append(
                {
                    "action": action,
                    "label": ACTION_LABELS.get(action, action),
                    "to_status": t.to,
                }
            )
        return result

    def transition(
        self,
        state: EventState,
        action: str,
        actor_role: str,
        actor_id: Optional[int] = None,
        already_applied: bool = False,
        max_shocks: int = 3,
    ) -> TransitionResult:
        """执行转移。

        already_applied: 是否已存在同 (action, actor) 的历史记录（幂等检测）。
        """
        t = TRANSITIONS.get(action)
        result = TransitionResult(
            from_status=state.status,
            to_status=state.status,
            new_seq=state.seq,
            shock_count=state.shock_count,
        )

        if t is None:
            result.reason = f"未知动作 {action}"
            return result

        # 幂等：非可重复动作，若同一 (action, actor) 已成功过 → 直接返回 duplicate
        if (
            not result.applied
            and already_applied
            and action not in REPEATABLE_ACTIONS
        ):
            result.duplicate = True
            result.reason = f"动作 {action} 已由该角色提交过（幂等）"
            result.new_seq = state.seq
            return result

        ok, reason = self.can(state, action, actor_role)
        if not ok:
            result.reason = reason
            return result

        # 单调性守卫：除颤往返例外，禁止状态回退
        to = t.to
        if to is not None and to != state.status:
            if STATUS_RANK[to] < STATUS_RANK[state.status]:
                if not (
                    action == Action.AED_ANALYSIS_STARTED.value
                    and state.status == Status.SHOCK_DELIVERED.value
                    and state.shock_count < max_shocks
                ):
                    result.reason = (
                        f"禁止状态回退 {state.status} → {to}"
                    )
                    return result

        # 应用副作用并推进
        if t.effect is not None:
            t.effect(state, actor_role)

        new_seq = state.seq + 1
        if to is not None:
            state.status = to
        state.seq = new_seq

        result.applied = True
        result.duplicate = False
        result.to_status = state.status
        result.new_seq = new_seq
        result.shock_count = state.shock_count
        return result
