"""GET /events/active 自动发现端点测试。"""
from __future__ import annotations


def _active(client, headers, who="PRIME"):
    return client.get("/api/v1/events/active", headers=headers[who])


def _run_full_to_archived(client, headers, event_id) -> None:
    """把事件完整推到 ARCHIVED（镜像 test_api_flow 的全链路动作序列）。"""
    for who in ("PRIME", "RUNNER", "GUIDE"):
        client.post(
            f"/api/v1/events/{event_id}/actions",
            json={"action": "RESPONSE_CONFIRMED"},
            headers=headers[who],
        )
    client.post(
        f"/api/v1/events/{event_id}/dispatch",
        json={},
        headers=headers["SYSTEM"],
    )
    for who, action in (
        ("PRIME", "CPR_STARTED"),
        ("RUNNER", "AED_PICKED"),
        ("RUNNER", "AED_DELIVERED"),
        ("PRIME", "AED_ANALYSIS_STARTED"),
        ("PRIME", "AED_SHOCK_DELIVERED"),
        ("GUIDE", "AMBULANCE_ARRIVED"),
        ("PRIME", "HANDOVER_COMPLETED"),
    ):
        r = client.post(
            f"/api/v1/events/{event_id}/actions",
            json={"action": action},
            headers=headers[who],
        )
        assert r.json()["applied"] is True, (action, r.json())
    r = client.post(
        f"/api/v1/events/{event_id}/actions",
        json={"action": "ARCHIVE"},
        headers=headers["SYSTEM"],
    )
    assert r.json()["event"]["status"] == "ARCHIVED"


def test_active_requires_auth(client):
    r = client.get("/api/v1/events/active")
    assert r.status_code == 401


def test_active_none_when_no_event(client, headers):
    r = _active(client, headers)
    assert r.status_code == 200
    assert r.json() == {"event": None}


def test_active_returns_current_event(client, headers, make_event):
    event_id = make_event()
    r = _active(client, headers, who="RUNNER")
    assert r.status_code == 200
    body = r.json()
    assert body["event"] is not None
    assert body["event"]["id"] == event_id
    assert body["event"]["status"] == "SOS"
    assert body["event"]["seq"] == 1
    # 按角色裁剪：RUNNER 在 SOS 应能确认响应
    names = {a["action"] for a in body["event"]["available_actions"]}
    assert "RESPONSE_CONFIRMED" in names


def test_active_any_logged_in_user_can_query(client, headers, make_event):
    make_event()
    for who in ("PATIENT", "PRIME", "RUNNER", "GUIDE", "SYSTEM", "ADMIN"):
        r = _active(client, headers, who=who)
        assert r.status_code == 200, who
        assert r.json()["event"] is not None


def test_active_after_archive_returns_none(client, headers, make_event):
    event_id = make_event()
    _run_full_to_archived(client, headers, event_id)
    r = _active(client, headers)
    assert r.status_code == 200
    assert r.json()["event"] is None


def test_active_prefers_latest_non_archived(client, headers, make_event):
    """归档旧事件后再次 SOS，返回最新事件；且不与其他静态路由冲突。"""
    first = make_event()
    _run_full_to_archived(client, headers, first)

    second = make_event()
    r = _active(client, headers)
    assert r.json()["event"]["id"] == second
    assert r.json()["event"]["status"] == "SOS"

    # 两次 make_event 同时只有最新一个处于 SOS：再次查询仍返回 second
    r = _active(client, headers)
    assert r.json()["event"]["id"] == second
