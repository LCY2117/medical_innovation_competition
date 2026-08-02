"""状态机引擎单测：全链路 happy path + 全部边界场景。

覆盖：非法角色 / 守卫 / 幂等 / 回退 / 未知组合 / 超时 / 再除颤 / 重复触发 /
      available_actions 推导。
"""
from __future__ import annotations

import pytest

from app.core.state_machine import (
    Action,
    EventState,
    Role,
    StateMachineEngine,
    Status,
)

engine = StateMachineEngine()


def _fresh() -> EventState:
    return EventState()


def _assert_applied(r, to_status, seq):
    assert r.applied is True, r.reason
    assert not r.duplicate
    assert r.to_status == to_status
    assert r.new_seq == seq


# ---------------- 全链路 happy path ----------------

def test_full_happy_path():
    state = _fresh()

    # 1. 患者发起 SOS
    r = engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    _assert_applied(r, Status.SOS.value, seq=1)
    assert state.status == Status.SOS.value

    # 2. 三个施救角色确认响应（状态不变，置 *_confirmed）
    for role, flag in (
        (Role.PRIME, "prime_confirmed"),
        (Role.RUNNER, "runner_confirmed"),
        (Role.GUIDE, "guide_confirmed"),
    ):
        r = engine.transition(state, Action.RESPONSE_CONFIRMED, role)
        _assert_applied(r, Status.SOS.value, seq=state.seq)
        assert getattr(state, flag) is True

    # 3. 系统分派
    r = engine.transition(state, Action.DISPATCH, Role.SYSTEM)
    _assert_applied(r, Status.DISPATCHED.value, seq=5)
    assert state.status == Status.DISPATCHED.value

    # 4. PRIME 开始 CPR
    r = engine.transition(state, Action.CPR_STARTED, Role.PRIME)
    _assert_applied(r, Status.CPR.value, seq=6)

    # 5. RUNNER 取 AED
    r = engine.transition(state, Action.AED_PICKED, Role.RUNNER)
    _assert_applied(r, Status.AED_PICKED.value, seq=7)

    # 6. RUNNER 送达 AED
    r = engine.transition(state, Action.AED_DELIVERED, Role.RUNNER)
    _assert_applied(r, Status.AED_DELIVERED.value, seq=8)

    # 7. PRIME 开始 AED 分析
    r = engine.transition(state, Action.AED_ANALYSIS_STARTED, Role.PRIME)
    _assert_applied(r, Status.AED_ANALYZING.value, seq=9)

    # 8. PRIME 实施除颤
    r = engine.transition(state, Action.AED_SHOCK_DELIVERED, Role.PRIME)
    _assert_applied(r, Status.SHOCK_DELIVERED.value, seq=10)
    assert state.shock_count == 1

    # 9. GUIDE 确认救护车到场（状态不变）
    r = engine.transition(state, Action.AMBULANCE_ARRIVED, Role.GUIDE)
    _assert_applied(r, Status.SHOCK_DELIVERED.value, seq=11)
    assert state.ambulance_arrived is True

    # 10. 完成交接
    r = engine.transition(state, Action.HANDOVER_COMPLETED, Role.PRIME)
    _assert_applied(r, Status.HANDOVER.value, seq=12)

    # 11. 归档
    r = engine.transition(state, Action.ARCHIVE, Role.SYSTEM)
    _assert_applied(r, Status.ARCHIVED.value, seq=13)
    assert state.status == Status.ARCHIVED.value


# ---------------- 非法角色 ----------------

def test_wrong_role_rejected():
    state = _fresh()
    # 患者不能分派
    r = engine.transition(state, Action.DISPATCH, Role.PATIENT)
    assert not r.applied
    assert "无权" in r.reason
    # PRIME 不能发起 SOS（患者专属）
    r = engine.transition(state, Action.SOS_TRIGGERED, Role.PRIME)
    assert not r.applied
    assert "无权" in r.reason
    # RUNNER 不能开始 CPR
    r = engine.transition(state, Action.CPR_STARTED, Role.RUNNER)
    assert not r.applied
    # GUIDE 不能取 AED
    r = engine.transition(state, Action.AED_PICKED, Role.GUIDE)
    assert not r.applied


# ---------------- 守卫 ----------------

def test_guard_need_prime_confirmed_for_cpr():
    state = _fresh()
    # 先 SOS + DISPATCH，但不确认 PRIME
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    engine.transition(state, Action.DISPATCH, Role.SYSTEM)
    r = engine.transition(state, Action.CPR_STARTED, Role.PRIME)
    assert not r.applied
    assert "尚未确认" in r.reason


def test_guard_aed_analysis_requires_delivered():
    state = _fresh()
    # 直接尝试分析（AED 未送达）
    r = engine.transition(state, Action.AED_ANALYSIS_STARTED, Role.PRIME)
    assert not r.applied
    assert "AED" in r.reason or "送达" in r.reason


def test_guard_handover_requires_ambulance():
    state = _fresh()
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.PRIME)
    engine.transition(state, Action.DISPATCH, Role.SYSTEM)
    engine.transition(state, Action.CPR_STARTED, Role.PRIME)
    r = engine.transition(state, Action.HANDOVER_COMPLETED, Role.PRIME)
    assert not r.applied
    assert "救护车" in r.reason


# ---------------- 幂等 ----------------

def test_idempotent_duplicate_no_seq_growth():
    state = _fresh()
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    r1 = engine.transition(
        state, Action.RESPONSE_CONFIRMED, Role.PRIME, already_applied=False
    )
    assert r1.applied
    before = state.seq

    # 同一 (action, actor) 重复提交 → duplicate，seq 不增长
    r2 = engine.transition(
        state, Action.RESPONSE_CONFIRMED, Role.PRIME, already_applied=True
    )
    assert not r2.applied
    assert r2.duplicate is True
    assert r2.new_seq == before == state.seq


def test_repeatable_action_not_flagged_duplicate():
    state = _fresh()
    # 第 2 次除颤是合法可重复动作，不应被判为 duplicate
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.PRIME)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.RUNNER)
    engine.transition(state, Action.DISPATCH, Role.SYSTEM)
    engine.transition(state, Action.CPR_STARTED, Role.PRIME)
    engine.transition(state, Action.AED_PICKED, Role.RUNNER)
    engine.transition(state, Action.AED_DELIVERED, Role.RUNNER)
    engine.transition(state, Action.AED_ANALYSIS_STARTED, Role.PRIME)
    engine.transition(state, Action.AED_SHOCK_DELIVERED, Role.PRIME)
    assert state.shock_count == 1
    # 再分析（可重复）
    r = engine.transition(
        state, Action.AED_ANALYSIS_STARTED, Role.PRIME, already_applied=True
    )
    assert r.applied and not r.duplicate
    r = engine.transition(
        state, Action.AED_SHOCK_DELIVERED, Role.PRIME, already_applied=True
    )
    assert r.applied and not r.duplicate
    assert state.shock_count == 2


# ---------------- 回退 / 单调性 ----------------

def test_no_state_regression_after_shock_limit():
    state = _fresh()
    # 推进到 SHOCK_DELIVERED 并打满 3 次除颤
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.PRIME)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.RUNNER)
    engine.transition(state, Action.DISPATCH, Role.SYSTEM)
    engine.transition(state, Action.CPR_STARTED, Role.PRIME)
    engine.transition(state, Action.AED_PICKED, Role.RUNNER)
    engine.transition(state, Action.AED_DELIVERED, Role.RUNNER)
    for _ in range(3):
        engine.transition(state, Action.AED_ANALYSIS_STARTED, Role.PRIME)
        r = engine.transition(
            state, Action.AED_SHOCK_DELIVERED, Role.PRIME
        )
        assert r.applied
    assert state.shock_count == 3
    assert state.status == Status.SHOCK_DELIVERED.value

    # 打满后禁止再回到 AED_ANALYZING（防回退）
    r = engine.transition(state, Action.AED_ANALYSIS_STARTED, Role.PRIME)
    assert not r.applied


def test_re_shock_allowed_below_limit():
    state = _fresh()
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.PRIME)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.RUNNER)
    engine.transition(state, Action.DISPATCH, Role.SYSTEM)
    engine.transition(state, Action.CPR_STARTED, Role.PRIME)
    engine.transition(state, Action.AED_PICKED, Role.RUNNER)
    engine.transition(state, Action.AED_DELIVERED, Role.RUNNER)
    engine.transition(state, Action.AED_ANALYSIS_STARTED, Role.PRIME)
    engine.transition(state, Action.AED_SHOCK_DELIVERED, Role.PRIME)
    # 第二次分析（SHOCK_DELIVERED → AED_ANALYZING，上限内允许）
    r = engine.transition(state, Action.AED_ANALYSIS_STARTED, Role.PRIME)
    assert r.applied
    assert state.status == Status.AED_ANALYZING.value
    assert state.seq == 10  # 第 10 次转移


# ---------------- 未知组合 ----------------

def test_unknown_action():
    state = _fresh()
    r = engine.transition(state, "NONEXISTENT", Role.PATIENT)
    assert not r.applied
    assert "未知动作" in r.reason


def test_valid_action_from_wrong_state():
    state = _fresh()
    # CPR_STARTED 只能从 DISPATCHED 开始
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    r = engine.transition(state, Action.CPR_STARTED, Role.PRIME)
    assert not r.applied
    assert "当前状态" in r.reason


# ---------------- 超时自动分派（引擎层） ----------------

def test_dispatch_by_system_after_timeout():
    state = _fresh()
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    # 超时后 SYSTEM 自动执行 DISPATCH
    r = engine.transition(state, Action.DISPATCH, Role.SYSTEM)
    assert r.applied
    assert state.status == Status.DISPATCHED.value
    # 再分派（幂等）→ duplicate
    r = engine.transition(
        state, Action.DISPATCH, Role.SYSTEM, already_applied=True
    )
    assert r.duplicate is True
    assert not r.applied


# ---------------- 重复触发（SOS 防误触） ----------------

def test_sos_trigger_blocked_when_active():
    state = _fresh()
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    # 已有进行中事件 → 拒绝再次触发
    r = engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    assert not r.applied
    assert "进行中" in r.reason


# ---------------- available_actions 推导 ----------------

def test_available_actions_derivation():
    # PATIENT 在 CREATED 只有 SOS
    state = _fresh()
    acts = engine.available_actions(state, Role.PATIENT.value)
    assert [a["action"] for a in acts] == [Action.SOS_TRIGGERED.value]

    # SYSTEM 在 SOS 只有 DISPATCH
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    acts = engine.available_actions(state, Role.SYSTEM.value)
    assert [a["action"] for a in acts] == [Action.DISPATCH.value]

    # PRIME 在 DISPATCHED 未确认 → 仅 RESPONSE_CONFIRMED
    engine.transition(state, Action.DISPATCH, Role.SYSTEM)
    acts = engine.available_actions(state, Role.PRIME.value)
    assert [a["action"] for a in acts] == [Action.RESPONSE_CONFIRMED.value]

    # PRIME 确认后 → 仅 CPR_STARTED（RESPONSE_CONFIRMED 不再出现，避免“一屏一动作”重复）
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.PRIME)
    acts = engine.available_actions(state, Role.PRIME.value)
    names = [a["action"] for a in acts]
    assert names == [Action.CPR_STARTED.value]
    # 动作结构包含中文标签与目标状态
    assert "label" in acts[0] and "to_status" in acts[0]


def test_available_actions_empty_when_archived():
    state = _fresh()
    engine.transition(state, Action.SOS_TRIGGERED, Role.PATIENT)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.PRIME)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.RUNNER)
    engine.transition(state, Action.RESPONSE_CONFIRMED, Role.GUIDE)
    engine.transition(state, Action.DISPATCH, Role.SYSTEM)
    engine.transition(state, Action.CPR_STARTED, Role.PRIME)
    engine.transition(state, Action.AED_PICKED, Role.RUNNER)
    engine.transition(state, Action.AED_DELIVERED, Role.RUNNER)
    engine.transition(state, Action.AED_ANALYSIS_STARTED, Role.PRIME)
    engine.transition(state, Action.AED_SHOCK_DELIVERED, Role.PRIME)
    engine.transition(state, Action.AMBULANCE_ARRIVED, Role.GUIDE)
    engine.transition(state, Action.HANDOVER_COMPLETED, Role.PRIME)
    engine.transition(state, Action.ARCHIVE, Role.SYSTEM)
    acts = engine.available_actions(state, Role.PRIME.value)
    assert acts == []
