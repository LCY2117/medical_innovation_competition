from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field


SUPPORTED_PUSH_PROVIDERS = {"websocket", "noop", "jpush", "vendor"}


@dataclass(frozen=True)
class NotificationIntent:
    incident_id: str
    event_type: str
    title: str
    body: str
    severity: str = "info"
    actor_user_id: str | None = None
    target_user_id: str | None = None
    audience_roles: tuple[str, ...] = ()
    payload: dict = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationResult:
    provider: str
    channel: str
    delivered: int
    fallbackReason: str | None = None


class NotificationProvider:
    async def notify(self, intent: NotificationIntent) -> NotificationResult:
        raise NotImplementedError

    def explain(self) -> dict:
        raise NotImplementedError


class WebSocketFallbackNotificationProvider(NotificationProvider):
    def __init__(
        self,
        provider: str = "websocket",
        send_state: Callable[[str], Awaitable[int]] | None = None,
    ) -> None:
        normalized = provider.strip().lower() if provider else "websocket"
        self.requested_provider = normalized or "websocket"
        self.provider = normalized if normalized in SUPPORTED_PUSH_PROVIDERS else "websocket"
        self.send_state = send_state

    async def notify(self, intent: NotificationIntent) -> NotificationResult:
        delivered = 0
        if self.send_state is not None:
            delivered = await self.send_state(intent.incident_id)

        fallback_reason = None
        if self.requested_provider not in SUPPORTED_PUSH_PROVIDERS:
            fallback_reason = "unsupported_provider"
        elif self.provider in {"jpush", "vendor"}:
            fallback_reason = f"{self.provider}_adapter_pending"

        return NotificationResult(
            provider="websocket",
            channel="websocket_state",
            delivered=delivered,
            fallbackReason=fallback_reason,
        )

    def explain(self) -> dict:
        fallback_reason = None
        if self.requested_provider not in SUPPORTED_PUSH_PROVIDERS:
            fallback_reason = "unsupported_provider"
        elif self.provider in {"jpush", "vendor"}:
            fallback_reason = f"{self.provider}_adapter_pending"

        return {
            "requestedProvider": self.requested_provider,
            "mode": self.provider,
            "activeProvider": "websocket",
            "configured": self.provider == "websocket",
            "fallbackEnabled": True,
            "fallbackReason": fallback_reason,
            "channel": "websocket_state",
        }


class NoopNotificationProvider(NotificationProvider):
    async def notify(self, intent: NotificationIntent) -> NotificationResult:
        return NotificationResult(
            provider="noop",
            channel="none",
            delivered=0,
            fallbackReason="notifications_disabled",
        )

    def explain(self) -> dict:
        return {
            "requestedProvider": "noop",
            "mode": "noop",
            "activeProvider": "noop",
            "configured": True,
            "fallbackEnabled": False,
            "fallbackReason": "notifications_disabled",
            "channel": "none",
        }
