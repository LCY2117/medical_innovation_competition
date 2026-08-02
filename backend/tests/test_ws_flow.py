"""WebSocket 集成测试：连接鉴权 / 订阅快照 / 心跳 / seq 单调 / 防回退。"""
from __future__ import annotations

import pytest


def _ws_url(token: str) -> str:
    return f"/ws/events?token={token}"


def test_ws_full_flow(client, headers, make_event):
    event_id = make_event()
    admin_token = headers["SYSTEM"]["Authorization"].split(" ")[1]
    versions: list[int] = []

    with client.websocket_connect(_ws_url(admin_token)) as ws:
        # ---- 心跳 ----
        ws.send_json({"type": "PING"})
        pong = ws.receive_json()
        assert pong["type"] == "PONG"
        assert pong["data"]["ok"] is True

        # ---- 订阅 → 快照 ----
        ws.send_json(
            {"type": "SUBSCRIBE_EVENT", "data": {"event_id": event_id}}
        )
        msg = ws.receive_json()
        assert msg["type"] == "EVENT_SNAPSHOT"
        assert msg["version"] == 1  # SOS 后 seq=1
        assert msg["data"]["status"] == "SOS"
        # 服务端按角色推导可用动作：SYSTEM 在 SOS 有 DISPATCH
        actions = {a["action"] for a in msg["data"]["available_actions"]}
        assert "DISPATCH" in actions
        versions.append(msg["version"])

        # 时间线 + 计时器
        t = ws.receive_json()
        assert t["type"] == "TRANSITION_ADDED"
        assert len(t["data"]["transitions"]) == 1
        timer = ws.receive_json()
        assert timer["type"] == "TIMER_SYNC"
        assert timer["data"]["elapsed"] >= 0

        # ---- 确认 + 分派：收到版本化推送 ----
        for who in ("PRIME", "RUNNER", "GUIDE"):
            client.post(
                f"/api/v1/events/{event_id}/actions",
                json={"action": "RESPONSE_CONFIRMED"},
                headers=headers[who],
            )
        r = client.post(
            f"/api/v1/events/{event_id}/dispatch",
            json={},
            headers=headers["SYSTEM"],
        )
        assert r.status_code == 200

        # 6 条确认 → EVENT_UPDATE+TRANSITION_ADDED 各 3 条（v2/3/4），分派 → 3 条（v5）
        received = [ws.receive_json() for _ in range(9)]
        versions.extend(m["version"] for m in received)
        types = [m["type"] for m in received]
        assert types.count("EVENT_UPDATE") == 4
        assert types.count("TRANSITION_ADDED") == 4
        assert "ASSIGNMENT_UPDATE" in types
        # 分派后的 EVENT_UPDATE 状态
        last_event_update = [
            m for m in received if m["type"] == "EVENT_UPDATE"
        ][-1]
        assert last_event_update["data"]["status"] == "DISPATCHED"

        # ---- seq 单调（可并列，但绝不回退；分派后版本到达 5）----
        assert versions == sorted(versions)
        assert versions[-1] == 5

        # ---- CPR 推进 ----
        client.post(
            f"/api/v1/events/{event_id}/actions",
            json={"action": "CPR_STARTED"},
            headers=headers["PRIME"],
        )
        msg = ws.receive_json()
        assert msg["type"] == "EVENT_UPDATE"
        assert msg["version"] == versions[-1] + 1  # 严格 +1
        versions.append(msg["version"])
        assert msg["data"]["status"] == "CPR"
        t = ws.receive_json()
        assert t["type"] == "TRANSITION_ADDED"
        assert t["version"] == msg["version"]

        # ---- 防回退：重复提交不产生新版本 ----
        r = client.post(
            f"/api/v1/events/{event_id}/actions",
            json={"action": "CPR_STARTED"},
            headers=headers["PRIME"],
        )
        assert r.json()["duplicate"] is True
        assert r.json()["new_seq"] == msg["version"]
        # 收到 TRANSITION_ADDED（含 duplicate 时间线追加？不：幂等不写库、不广播）
        # 不读取任何消息，验证无新版本推送：直接推进一步并检查版本 == 上一版 +1

        # RUNNER 取 AED → 版本应恰好再 +1（证明重复动作未推进版本）
        client.post(
            f"/api/v1/events/{event_id}/actions",
            json={"action": "AED_PICKED"},
            headers=headers["RUNNER"],
        )
        msg = ws.receive_json()
        assert msg["type"] == "EVENT_UPDATE"
        assert msg["version"] == versions[-1] + 1
        versions.append(msg["version"])
        t = ws.receive_json()
        assert t["type"] == "TRANSITION_ADDED"
        assert t["version"] == msg["version"]

        # ---- 错误消息类型 ----
        ws.send_json({"type": "NOT_A_TYPE", "data": {}})
        err = ws.receive_json()
        assert err["type"] == "ERROR"
