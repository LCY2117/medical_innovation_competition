"""REST 集成测试：登录 → SOS → 分派 → 动作全链路 → 归档 → 健康/AED。"""
from __future__ import annotations

import json


def _action(client, headers, event_id, action, metadata=None, who="PRIME"):
    return client.post(
        f"/api/v1/events/{event_id}/actions",
        json={"action": action, "metadata": metadata or {}},
        headers=headers[who],
    )


def _apply(client, headers, event_id, action, who, expect_applied=True):
    r = _action(client, headers, event_id, action, who=who)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["applied"] is expect_applied, body
    return body


def test_full_rest_flow(client, headers, make_event):
    event_id = make_event()

    # ---- SOS 防误触 ----
    r = client.post(
        "/api/v1/events/sos",
        json={"location": "第二场地"},
        headers=headers["PATIENT"],
    )
    assert r.status_code == 409
    assert "进行中" in r.json()["detail"]

    # ---- 初始状态 ----
    r = client.get(f"/api/v1/events/{event_id}", headers=headers["PATIENT"])
    assert r.status_code == 200
    assert r.json()["status"] == "SOS"
    assert r.json()["seq"] == 1

    # 患者当前无可执行动作
    acts = client.get(
        f"/api/v1/events/{event_id}/actions", headers=headers["PATIENT"]
    ).json()
    assert acts == []

    # ---- 三个施救角色确认响应（角色+状态驱动，可先于分派）----
    for who in ("PRIME", "RUNNER", "GUIDE"):
        _apply(client, headers, event_id, "RESPONSE_CONFIRMED", who)
    detail = client.get(
        f"/api/v1/events/{event_id}", headers=headers["PRIME"]
    ).json()
    assert detail["prime_confirmed"] and detail["runner_confirmed"]
    assert detail["guide_confirmed"]

    # 非施救角色不能确认响应（引擎角色守卫）
    r = _action(client, headers, event_id, "RESPONSE_CONFIRMED", who="PATIENT")
    assert r.json()["applied"] is False
    assert "无权" in r.json()["reason"]

    # ---- 系统分派 ----
    r = client.post(
        f"/api/v1/events/{event_id}/dispatch",
        json={},
        headers=headers["SYSTEM"],
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "DISPATCHED"
    assert len(body["assignments"]) == 6  # 3 主选 + 3 递补
    # 主选必须是演示用户
    prime_assignment = next(
        a for a in body["assignments"]
        if a["role"] == "PRIME" and a["status"] == "PENDING"
    )
    assert prime_assignment["responder_name"].find("核心施救") >= 0

    # 非 SYSTEM/ADMIN 不能分派
    r = client.post(
        f"/api/v1/events/{event_id}/dispatch",
        json={},
        headers=headers["PRIME"],
    )
    assert r.status_code == 403

    # PRIME 可执行动作：已确认 → 只看得到 CPR_STARTED（RESPONSE_CONFIRMED 不再出现）
    acts = client.get(
        f"/api/v1/events/{event_id}/actions", headers=headers["PRIME"]
    ).json()
    names = [a["action"] for a in acts]
    assert "CPR_STARTED" in names and "RESPONSE_CONFIRMED" not in names

    # ---- CPR ----
    _apply(client, headers, event_id, "CPR_STARTED", "PRIME")
    assert client.get(
        f"/api/v1/events/{event_id}", headers=headers["PRIME"]
    ).json()["status"] == "CPR"

    # ---- AED 分析守卫：RUNNER 未送达前不可分析 ----
    r = _action(client, headers, event_id, "AED_ANALYSIS_STARTED", who="PRIME")
    assert r.json()["applied"] is False
    assert "AED" in r.json()["reason"] or "送达" in r.json()["reason"]

    # ---- RUNNER 取/送 AED ----
    _apply(client, headers, event_id, "AED_PICKED", "RUNNER")
    _apply(client, headers, event_id, "AED_DELIVERED", "RUNNER")

    # ---- AED 分析 + 除颤 ----
    _apply(client, headers, event_id, "AED_ANALYSIS_STARTED", "PRIME")
    r = _apply(client, headers, event_id, "AED_SHOCK_DELIVERED", "PRIME")
    assert r["event"]["shock_count"] == 1
    assert r["event"]["status"] == "SHOCK_DELIVERED"

    # ---- 交接守卫：救护车未到不可交接 ----
    r = _action(client, headers, event_id, "HANDOVER_COMPLETED", who="PRIME")
    assert r.json()["applied"] is False
    assert "救护车" in r.json()["reason"]

    # ---- 救护车到场（状态不变）----
    r = _apply(client, headers, event_id, "AMBULANCE_ARRIVED", "GUIDE")
    assert r["event"]["ambulance_arrived"] is True
    assert r["event"]["status"] == "SHOCK_DELIVERED"

    # ---- 交接 + 归档 ----
    _apply(client, headers, event_id, "HANDOVER_COMPLETED", "PRIME")
    r = _apply(client, headers, event_id, "ARCHIVE", "SYSTEM")
    assert r["event"]["status"] == "ARCHIVED"

    # ---- 幂等：重复确认 → duplicate，seq 不增长 ----
    r = client.post(
        f"/api/v1/events/{event_id}/actions",
        json={"action": "RESPONSE_CONFIRMED"},
        headers=headers["PRIME"],
    )
    body = r.json()
    assert body["duplicate"] is True and body["applied"] is False

    # ---- 时间线 ----
    timeline = client.get(
        f"/api/v1/events/{event_id}/timeline", headers=headers["ADMIN"]
    ).json()
    assert len(timeline) == 13
    assert timeline[0]["action"] == "SOS_TRIGGERED"
    assert timeline[-1]["action"] == "ARCHIVE"
    assert all(
        t["seq"] < u["seq"] for t, u in zip(timeline, timeline[1:])
    )
    # 与事件 seq 对齐
    ev = client.get(
        f"/api/v1/events/{event_id}", headers=headers["ADMIN"]
    ).json()
    assert ev["seq"] == 13 == timeline[-1]["seq"]

    # ---- 归档后患者可再次发起 SOS ----
    r = client.post(
        "/api/v1/events/sos", json={}, headers=headers["PATIENT"]
    )
    assert r.status_code == 201


def test_health_and_aed(client, headers, make_event):
    event_id = make_event()

    # 健康读数
    r = client.post(
        f"/api/v1/events/{event_id}/health",
        json={
            "reading_type": "heart_rate",
            "value": 88,
            "unit": "bpm",
            "source": "PRIME",
        },
        headers=headers["PRIME"],
    )
    assert r.status_code == 201, r.text
    reading_id = r.json()["id"]
    r = client.post(
        f"/api/v1/events/{event_id}/health",
        json={
            "reading_type": "spo2",
            "value": 96,
            "unit": "%",
            "source": "PRIME",
        },
        headers=headers["PRIME"],
    )
    assert r.status_code == 201

    readings = client.get(
        f"/api/v1/events/{event_id}/health", headers=headers["PRIME"]
    ).json()
    assert len(readings) == 2
    assert any(x["id"] == reading_id for x in readings)

    # 患者不能上报健康数据
    r = client.post(
        f"/api/v1/events/{event_id}/health",
        json={"reading_type": "note", "value": 0},
        headers=headers["PATIENT"],
    )
    assert r.status_code == 403

    # ---- AED CRUD ----
    devices = client.get("/api/v1/aed", headers=headers["GUIDE"]).json()
    assert len(devices) >= 4

    r = client.post(
        "/api/v1/aed",
        json={"name": "AED-05 测试", "location": "仓库", "available": True},
        headers=headers["ADMIN"],
    )
    assert r.status_code == 201, r.text
    aed_id = r.json()["id"]

    r = client.patch(
        f"/api/v1/aed/{aed_id}",
        json={"available": False},
        headers=headers["ADMIN"],
    )
    assert r.status_code == 200 and r.json()["available"] is False

    r = client.get(f"/api/v1/aed/{aed_id}", headers=headers["PRIME"])
    assert r.status_code == 200 and r.json()["name"] == "AED-05 测试"

    r = client.delete(f"/api/v1/aed/{aed_id}", headers=headers["ADMIN"])
    assert r.status_code == 204

    r = client.delete(f"/api/v1/aed/{aed_id}", headers=headers["ADMIN"])
    assert r.status_code == 404


def test_auth_and_me(client, headers):
    r = client.get("/api/v1/auth/me", headers=headers["PRIME"])
    assert r.status_code == 200
    assert r.json()["role"] == "PRIME"

    # 错误密码
    r = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert r.status_code == 401

    # 无 token
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401

    # 非法演示角色
    r = client.post("/api/v1/auth/demo", json={"role": "HACKER"})
    assert r.status_code == 400


def test_demo_endpoints(client, headers):
    # init 幂等
    r = client.post("/api/v1/demo/init", headers=headers["ADMIN"])
    assert r.status_code == 200
    assert r.json()["seeded"] is False  # 已有种子

    # trigger 一键触发
    r = client.post("/api/v1/demo/trigger", headers=headers["ADMIN"])
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "DISPATCHED"
    assert len(body["assignments"]) >= 3

    # reset 清空业务数据
    r = client.post("/api/v1/demo/reset", headers=headers["ADMIN"])
    assert r.status_code == 200
    assert r.json()["ok"] is True
