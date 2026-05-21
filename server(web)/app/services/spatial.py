from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from urllib import error, parse, request

from app.models.schemas import GeoPoint


SUPPORTED_MAP_PROVIDERS = {"demo", "amap", "tencent", "baidu"}


@dataclass(frozen=True)
class DistanceResult:
    meters: float | None
    provider: str
    source: str
    fallbackReason: str | None = None


class SpatialProvider:
    def __init__(
        self,
        provider: str = "demo",
        amap_service_key: str | None = None,
        timeout_sec: int = 3,
    ) -> None:
        normalized = provider.strip().lower() if provider else "demo"
        self.provider = normalized if normalized in SUPPORTED_MAP_PROVIDERS else "demo"
        self.requested_provider = normalized or "demo"
        self.amap_service_key = (amap_service_key or "").strip() or None
        self.timeout_sec = max(1, timeout_sec)
        self._distance_cache: dict[tuple[str, str, str], DistanceResult] = {}

    def explain(self) -> dict:
        configured = self.provider == "amap" and bool(self.amap_service_key)
        fallback_reason = None
        if self.requested_provider not in SUPPORTED_MAP_PROVIDERS:
            fallback_reason = "unsupported_provider"
        elif self.provider == "amap" and not self.amap_service_key:
            fallback_reason = "amap_service_key_missing"
        elif self.provider in {"tencent", "baidu"}:
            fallback_reason = f"{self.provider}_adapter_pending"

        active_provider = self.provider if configured else "demo"
        return {
            "requestedProvider": self.requested_provider,
            "mode": self.provider,
            "activeProvider": active_provider,
            "configured": configured,
            "fallbackEnabled": True,
            "fallbackReason": fallback_reason,
            "distanceSource": "amap_web_service" if configured else "haversine_demo",
            "timeoutSec": self.timeout_sec,
        }

    def distance_meters(self, origin: GeoPoint | None, destination: GeoPoint | None) -> DistanceResult:
        if origin is None or destination is None:
            return DistanceResult(meters=None, provider=self.provider, source="missing_location")

        if self.provider == "amap" and self.amap_service_key:
            cached = self._distance_cache.get(self._cache_key(origin, destination))
            if cached is not None:
                return cached
            result = self._amap_distance(origin, destination)
            self._distance_cache[self._cache_key(origin, destination)] = result
            return result

        fallback_reason = None
        if self.requested_provider not in SUPPORTED_MAP_PROVIDERS:
            fallback_reason = "unsupported_provider"
        elif self.provider == "amap":
            fallback_reason = "amap_service_key_missing"
        elif self.provider in {"tencent", "baidu"}:
            fallback_reason = f"{self.provider}_adapter_pending"
        return DistanceResult(
            meters=self._haversine_distance_meters(origin, destination),
            provider="demo",
            source="haversine_demo",
            fallbackReason=fallback_reason,
        )

    def _amap_distance(self, origin: GeoPoint, destination: GeoPoint) -> DistanceResult:
        query = parse.urlencode(
            {
                "origins": f"{origin.longitude},{origin.latitude}",
                "destination": f"{destination.longitude},{destination.latitude}",
                "type": 1,
                "key": self.amap_service_key,
            }
        )
        req = request.Request(
            url=f"https://restapi.amap.com/v3/distance?{query}",
            headers={"User-Agent": "LifeReflexArc/competition-hardening"},
        )
        try:
            started = time.monotonic()
            with request.urlopen(req, timeout=self.timeout_sec) as response:
                body = json.loads(response.read().decode("utf-8"))
            results = body.get("results") if isinstance(body, dict) else None
            first = results[0] if isinstance(results, list) and results else {}
            distance = float(first.get("distance"))
            return DistanceResult(
                meters=distance,
                provider="amap",
                source="amap_web_service",
                fallbackReason=None if time.monotonic() - started <= self.timeout_sec else "amap_timeout",
            )
        except (ValueError, KeyError, TypeError, json.JSONDecodeError, error.URLError, error.HTTPError, TimeoutError):
            return DistanceResult(
                meters=self._haversine_distance_meters(origin, destination),
                provider="demo",
                source="haversine_demo",
                fallbackReason="amap_distance_failed",
            )

    @staticmethod
    def _cache_key(origin: GeoPoint, destination: GeoPoint) -> tuple[str, str, str]:
        return (
            f"{origin.latitude:.6f},{origin.longitude:.6f}",
            f"{destination.latitude:.6f},{destination.longitude:.6f}",
            "walking",
        )

    @staticmethod
    def _haversine_distance_meters(origin: GeoPoint, destination: GeoPoint) -> float:
        radius = 6_371_000
        lat1 = math.radians(origin.latitude)
        lat2 = math.radians(destination.latitude)
        delta_lat = math.radians(destination.latitude - origin.latitude)
        delta_lon = math.radians(destination.longitude - origin.longitude)
        hav = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
        return 2 * radius * math.asin(math.sqrt(hav))
