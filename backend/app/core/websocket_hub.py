"""WebSocket 连接中枢：连接注册、按事件广播、心跳、版本化消息。

协议：
    连接  : /ws/events?token=<JWT>
    客户端 : {"type":"SUBSCRIBE_EVENT","data":{"event_id":...}} / {"type":"PING"}
    服务端 : {"type":"EVENT_SNAPSHOT"|"EVENT_UPDATE"|"TRANSITION_ADDED"
              |"ASSIGNMENT_UPDATE"|"HEALTH_READING"|"TIMER_SYNC"|"PONG"|"ERROR",
              "ts":..., "version":..., "data":{...}}

版本化：所有事件类消息携带 version = event.seq（单调递增）。
客户端 reducer 依据 version 丢弃旧消息，防止回退。
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger("lifereflex.ws")

# 无订阅事件时的兜底广播组（调度大屏等全局监听者）
_GLOBAL = "__global__"


@dataclass
class Conn:
    ws: WebSocket
    user_id: int
    role: str
    username: str = ""
    subscribed: Optional[int] = field(default=None)  # event_id


class WebSocketHub:
    """管理所有 WS 连接与事件订阅关系。"""

    def __init__(self) -> None:
        self._conns: dict[WebSocket, Conn] = {}
        self._by_event: dict[int, set[WebSocket]] = {}
        self._global: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    # ---------- 注册 ----------
    async def connect(self, ws: WebSocket, user_id: int, role: str, username: str) -> Conn:
        await ws.accept()
        conn = Conn(ws=ws, user_id=user_id, role=role, username=username)
        async with self._lock:
            self._conns[ws] = conn
            self._global.add(ws)
        return conn

    async def disconnect(self, ws: WebSocket) -> None:
        async with self._lock:
            conn = self._conns.pop(ws, None)
            self._global.discard(ws)
            if conn is not None and conn.subscribed is not None:
                event_ws = self._by_event.get(conn.subscribed)
                if event_ws:
                    event_ws.discard(ws)
                    if not event_ws:
                        self._by_event.pop(conn.subscribed, None)

    async def subscribe(self, ws: WebSocket, event_id: int) -> None:
        async with self._lock:
            conn = self._conns.get(ws)
            if conn is None:
                return
            if conn.subscribed is not None:
                old = self._by_event.get(conn.subscribed)
                if old:
                    old.discard(ws)
            conn.subscribed = event_id
            self._by_event.setdefault(event_id, set()).add(ws)
            self._global.discard(ws)  # 订阅具体事件后退出全局广播

    def conn_for(self, ws: WebSocket) -> Optional[Conn]:
        return self._conns.get(ws)

    # ---------- 发送 ----------
    @staticmethod
    def _pack(msg_type: str, data: dict, version: int | None = None) -> dict:
        payload: dict[str, Any] = {
            "type": msg_type,
            "ts": time.time(),
            "data": data,
        }
        if version is not None:
            payload["version"] = version
        return payload

    async def send(self, ws: WebSocket, msg_type: str, data: dict, version: int | None = None) -> None:
        try:
            payload = self._pack(msg_type, data, version)
            await ws.send_json(jsonable_encoder(payload))
        except Exception:  # noqa: BLE001
            logger.exception("WS 发送失败")
            await self.disconnect(ws)

    async def send_to_user(
        self, user_id: int, msg_type: str, data: dict, version: int | None = None
    ) -> None:
        async with self._lock:
            targets = [
                ws for ws, c in self._conns.items() if c.user_id == user_id
            ]
        for ws in targets:
            await self.send(ws, msg_type, data, version)

    async def broadcast_event(
        self,
        event_id: int,
        msg_type: str,
        builder: Callable[[Conn], dict],
        version: int | None = None,
    ) -> None:
        """按事件广播：为每个订阅连接按角色裁剪数据后下发。"""
        async with self._lock:
            targets = list(self._by_event.get(event_id, set())) + list(self._global)
        for ws in targets:
            conn = self.conn_for(ws)
            if conn is None:
                continue
            try:
                data = builder(conn)
                payload = self._pack(msg_type, data, version)
                await ws.send_json(jsonable_encoder(payload))
            except Exception:  # noqa: BLE001
                logger.exception("广播失败")
                await self.disconnect(ws)

    # ---------- 心跳 ----------
    async def handle_ping(self, ws: WebSocket) -> None:
        await self.send(ws, "PONG", {"ok": True})

    async def heartbeat_loop(self, interval: float = 30.0) -> None:
        """定期向所有连接发送服务端心跳，并清理失效连接。"""
        while True:
            await asyncio.sleep(interval)
            async with self._lock:
                snapshot = list(self._conns.values())
            for conn in snapshot:
                try:
                    await conn.ws.send_json(
                        jsonable_encoder(
                            self._pack("PING", {"server_ts": time.time()})
                        )
                    )
                except Exception:  # noqa: BLE001
                    await self.disconnect(conn.ws)
