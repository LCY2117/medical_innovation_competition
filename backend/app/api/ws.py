"""WebSocket 路由：/ws/events。

连接：/ws/events?token=<JWT>
客户端消息：SUBSCRIBE_EVENT / PING
服务端消息：EVENT_SNAPSHOT / EVENT_UPDATE / TRANSITION_ADDED / ASSIGNMENT_UPDATE
            / HEALTH_READING / TIMER_SYNC / PONG / ERROR
所有事件类消息携带 version = event.seq（单调版本，防回退）。
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from app.api.serializers import (
    event_dict_for_role,
    list_timeline,
)
from app.models.event import Event

logger = logging.getLogger("lifereflex.ws")

router = APIRouter()


def _elapsed(event: Event) -> float:
    if event.started_at is None:
        return 0.0
    start = event.started_at
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - start).total_seconds())


@router.websocket("/ws/events")
async def ws_events(ws: WebSocket):
    app = ws.app
    settings = app.state.settings
    token = ws.query_params.get("token", "")
    if not token:
        await ws.close(code=4001, reason="缺少 token")
        return

    from app.api.deps import ws_user_from_token

    try:
        auth = ws_user_from_token(settings, token)
    except HTTPException:
        await ws.close(code=4001, reason="token 无效")
        return

    hub = app.state.hub
    session_factory = app.state.session_factory
    conn = await hub.connect(
        ws, user_id=auth.user_id, role=auth.role, username=auth.username
    )

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await hub.send(ws, "ERROR", {"message": "JSON 解析失败"})
                continue

            msg_type = msg.get("type")
            data = msg.get("data") or {}

            if msg_type == "PING":
                await hub.handle_ping(ws)
                continue

            if msg_type == "SUBSCRIBE_EVENT":
                event_id = int(data.get("event_id", 0))
                with session_factory() as session:
                    event = session.get(Event, event_id)
                    if event is None:
                        await hub.send(
                            ws, "ERROR", {"message": "事件不存在"}
                        )
                        continue
                    await hub.subscribe(ws, event_id)
                    # 快照 + 时间线 + 计时器
                    await hub.send(
                        ws,
                        "EVENT_SNAPSHOT",
                        event_dict_for_role(event, conn.role),
                        version=event.seq,
                    )
                    await hub.send(
                        ws,
                        "TRANSITION_ADDED",
                        {
                            "transitions": [
                                t.model_dump()
                                for t in list_timeline(session, event.id)
                            ]
                        },
                        version=event.seq,
                    )
                    await hub.send(
                        ws,
                        "TIMER_SYNC",
                        {"elapsed": _elapsed(event), "started_at": (
                            event.started_at.isoformat()
                            if event.started_at
                            else None
                        )},
                        version=event.seq,
                    )
                continue

            await hub.send(
                ws,
                "ERROR",
                {"message": f"未知消息类型 {msg_type}"},
            )
    except WebSocketDisconnect:
        await hub.disconnect(ws)
    except Exception:  # noqa: BLE001
        logger.exception("WS 连接异常")
        await hub.disconnect(ws)
