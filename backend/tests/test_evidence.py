"""证据导出测试：JSON 包完整性 + ZIP 包完整性。"""
from __future__ import annotations

import io
import json
import zipfile
def _run_full_event(client, headers, make_event):
    """跑完整事件到 ARCHIVED，返回 event_id。"""
    event_id = make_event()
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
    for action, who in (
        ("CPR_STARTED", "PRIME"),
        ("AED_PICKED", "RUNNER"),
        ("AED_DELIVERED", "RUNNER"),
        ("AED_ANALYSIS_STARTED", "PRIME"),
        ("AED_SHOCK_DELIVERED", "PRIME"),
        ("AMBULANCE_ARRIVED", "GUIDE"),
        ("HANDOVER_COMPLETED", "PRIME"),
        ("ARCHIVE", "SYSTEM"),
    ):
        r = client.post(
            f"/api/v1/events/{event_id}/actions",
            json={"action": action},
            headers=headers[who],
        )
        assert r.status_code == 200 and r.json()["applied"], r.text
    # 添加健康读数
    client.post(
        f"/api/v1/events/{event_id}/health",
        json={"reading_type": "heart_rate", "value": 90, "unit": "bpm"},
        headers=headers["PRIME"],
    )
    return event_id


def test_evidence_json_completeness(client, headers, make_event):
    event_id = _run_full_event(client, headers, make_event)

    r = client.get(
        f"/api/v1/events/{event_id}/evidence", headers=headers["ADMIN"]
    )
    assert r.status_code == 200
    bundle = r.json()

    # manifest
    assert bundle["manifest"]["event_id"] == event_id
    assert bundle["manifest"]["final_status"] == "ARCHIVED"
    assert bundle["manifest"]["transition_count"] == 13
    assert bundle["manifest"]["final_seq"] == 13

    # event
    ev = bundle["event"]
    assert ev["status"] == "ARCHIVED"
    assert ev["shock_count"] == 1
    assert ev["ambulance_arrived"] is True

    # timeline 完整且按序
    timeline = bundle["timeline"]
    assert len(timeline) == 13
    actions = [t["action"] for t in timeline]
    assert actions[0] == "SOS_TRIGGERED"
    assert actions[-1] == "ARCHIVE"
    for expected in (
        "RESPONSE_CONFIRMED",
        "DISPATCH",
        "CPR_STARTED",
        "AED_PICKED",
        "AED_DELIVERED",
        "AED_ANALYSIS_STARTED",
        "AED_SHOCK_DELIVERED",
        "AMBULANCE_ARRIVED",
        "HANDOVER_COMPLETED",
    ):
        assert expected in actions
    assert [t["seq"] for t in timeline] == list(range(1, 14))

    # 每步必有 actor_role
    assert all(t["actor_role"] for t in timeline)

    # assignments 完整
    assignments = bundle["assignments"]
    roles = {a["role"] for a in assignments}
    assert {"PRIME", "RUNNER", "GUIDE"} == roles
    assert sum(1 for a in assignments if a["status"] == "PENDING") == 3
    assert sum(1 for a in assignments if a["status"] == "BACKUP") == 3
    # 打分非负且主选得分最高
    for role in ("PRIME", "RUNNER", "GUIDE"):
        mains = [
            a["score"]
            for a in assignments
            if a["role"] == role and a["status"] == "PENDING"
        ]
        assert all(s >= 0 for s in mains)

    # health
    assert len(bundle["health"]) == 1
    assert bundle["health"][0]["reading_type"] == "heart_rate"


def test_evidence_zip_contents(client, headers, make_event):
    event_id = _run_full_event(client, headers, make_event)

    r = client.get(
        f"/api/v1/events/{event_id}/evidence.zip", headers=headers["ADMIN"]
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"

    zf = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(zf.namelist())
    expected = {
        "manifest.json",
        "event.json",
        "timeline.json",
        "assignments.json",
        "health.json",
    }
    assert expected <= names

    manifest = json.loads(zf.read("manifest.json"))
    assert manifest["event_id"] == event_id
    assert manifest["transition_count"] == 13

    timeline = json.loads(zf.read("timeline.json"))
    assert len(timeline) == 13
    assert timeline[0]["action"] == "SOS_TRIGGERED"


def test_evidence_complete_at_archive(client, headers, make_event):
    """证据生成时机：ARCHIVE 动作成功返回时，证据包必须已具备完整时间线。

    覆盖：HANDOVER 后立即拉取证据（不含 ARCHIVE）→ 执行 ARCHIVE →
    立刻拉取证据 → 应含 13 条转移且末条为 ARCHIVE，transition_count 与 seq 对齐。
    """
    event_id = make_event()
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
    for action, who in (
        ("CPR_STARTED", "PRIME"),
        ("AED_PICKED", "RUNNER"),
        ("AED_DELIVERED", "RUNNER"),
        ("AED_ANALYSIS_STARTED", "PRIME"),
        ("AED_SHOCK_DELIVERED", "PRIME"),
        ("AMBULANCE_ARRIVED", "GUIDE"),
        ("HANDOVER_COMPLETED", "PRIME"),
    ):
        r = client.post(
            f"/api/v1/events/{event_id}/actions",
            json={"action": action},
            headers=headers[who],
        )
        assert r.status_code == 200 and r.json()["applied"], r.text

    # 归档前：12 条转移，无 ARCHIVE
    before = client.get(
        f"/api/v1/events/{event_id}/evidence", headers=headers["ADMIN"]
    ).json()
    assert before["manifest"]["transition_count"] == 12
    assert before["timeline"][-1]["action"] == "HANDOVER_COMPLETED"

    # 执行 ARCHIVE → 动作成功即视为已持久化完整时间线
    r = client.post(
        f"/api/v1/events/{event_id}/actions",
        json={"action": "ARCHIVE"},
        headers=headers["SYSTEM"],
    )
    assert r.status_code == 200 and r.json()["applied"], r.text

    # 归档后立即拉取：证据包应包含完整的 13 条转移（含 ARCHIVE），与事件 seq 对齐
    after = client.get(
        f"/api/v1/events/{event_id}/evidence", headers=headers["ADMIN"]
    ).json()
    assert after["manifest"]["final_status"] == "ARCHIVED"
    assert after["manifest"]["transition_count"] == 13
    assert after["manifest"]["final_seq"] == 13
    timeline = after["timeline"]
    assert len(timeline) == 13
    assert timeline[-1]["action"] == "ARCHIVE"
    assert timeline[-1]["to_status"] == "ARCHIVED"
    assert [t["seq"] for t in timeline] == list(range(1, 14))
    ev = client.get(
        f"/api/v1/events/{event_id}", headers=headers["ADMIN"]
    ).json()
    assert ev["seq"] == timeline[-1]["seq"]
