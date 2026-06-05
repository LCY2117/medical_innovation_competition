from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_ENV_FILE = ROOT_DIR / ".env"


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv(value: str | None, default: list[str]) -> list[str]:
    if value is None:
        return default
    items = [item.strip() for item in value.split(",")]
    parsed = [item for item in items if item]
    return parsed or default


def _parse_phone_csv(value: str | None) -> tuple[str, ...]:
    phones = []
    for item in _parse_csv(value, default=[]):
        normalized = "".join(ch for ch in item if ch.isdigit())
        if normalized:
            phones.append(normalized)
    return tuple(dict.fromkeys(phones))


def _resolve_path(value: str | None, default: Path) -> Path:
    if not value:
        return default
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = ROOT_DIR / candidate
    return candidate.resolve()


@dataclass(frozen=True)
class Settings:
    app_name: str
    api_prefix: str
    host: str
    port: int
    reload: bool
    sos_duration_sec: int
    dispatch_delay_sec: int
    cors_origins: list[str]
    db_path: Path
    web_dist_dir: Path
    web_dev_host: str = "127.0.0.1"
    web_dev_port: int = 5173
    siliconflow_api_key: str | None = None
    siliconflow_model: str = "Qwen/Qwen2-7B-Instruct"
    siliconflow_base_url: str = "https://api.siliconflow.cn/v1"
    siliconflow_timeout_sec: int = 8
    dispatch_llm_budget_sec: float = 1.0
    local_model_base_url: str | None = None
    local_model_name: str = "default"
    local_model_timeout_sec: int = 30
    prefer_local_model: bool = True
    demo_admin_token: str | None = None
    admin_phones: tuple[str, ...] = ()
    auth_token_ttl_sec: int = 604800
    health_provider: str = "mock"
    map_provider: str = "demo"
    amap_web_key: str | None = None
    amap_web_security_js_code: str | None = None
    amap_service_key: str | None = None
    map_distance_timeout_sec: int = 3
    audit_log_enabled: bool = True
    rate_limit_enabled: bool = True
    rate_limit_auth_per_minute: int = 20
    rate_limit_admin_per_minute: int = 60
    rate_limit_actor_per_minute: int = 120
    push_provider: str = "websocket"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    _load_dotenv(DEFAULT_ENV_FILE)

    api_prefix = os.getenv("LRA_API_PREFIX", "/api").strip() or "/api"
    if not api_prefix.startswith("/"):
        api_prefix = f"/{api_prefix}"

    return Settings(
        app_name=os.getenv("LRA_APP_NAME", "Life Reflex Arc - Distributed Emergency Response"),
        api_prefix=api_prefix.rstrip("/") or "/api",
        host=os.getenv("LRA_HOST", "0.0.0.0"),
        port=int(os.getenv("LRA_PORT", "8080")),
        reload=_parse_bool(os.getenv("LRA_RELOAD"), default=False),
        sos_duration_sec=int(os.getenv("LRA_SOS_DURATION_SEC", "5")),
        dispatch_delay_sec=int(os.getenv("LRA_DISPATCH_DELAY_SEC", "0")),
        cors_origins=_parse_csv(
            os.getenv("LRA_CORS_ORIGINS"),
            default=["http://localhost:5173", "http://127.0.0.1:5173"],
        ),
        db_path=_resolve_path(os.getenv("LRA_DB_PATH"), ROOT_DIR / "data" / "lifereflexarc.db"),
        web_dist_dir=_resolve_path(os.getenv("LRA_WEB_DIST_DIR"), ROOT_DIR / "web" / "dist"),
        web_dev_host=os.getenv("LRA_WEB_DEV_HOST", "127.0.0.1"),
        web_dev_port=int(os.getenv("LRA_WEB_DEV_PORT", "5173")),
        siliconflow_api_key=os.getenv("LRA_SILICONFLOW_API_KEY"),
        siliconflow_model=os.getenv("LRA_SILICONFLOW_MODEL", "Qwen/Qwen2-7B-Instruct"),
        siliconflow_base_url=os.getenv("LRA_SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1").rstrip("/"),
        siliconflow_timeout_sec=int(os.getenv("LRA_SILICONFLOW_TIMEOUT_SEC", "8")),
        dispatch_llm_budget_sec=float(os.getenv("LRA_DISPATCH_LLM_BUDGET_SEC", "1")),
        local_model_base_url=os.getenv("LRA_LOCAL_MODEL_BASE_URL", "http://localhost:8008/v1").rstrip("/") if os.getenv("LRA_LOCAL_MODEL_BASE_URL") else None,
        local_model_name=os.getenv("LRA_LOCAL_MODEL_NAME", "default"),
        local_model_timeout_sec=int(os.getenv("LRA_LOCAL_MODEL_TIMEOUT_SEC", "30")),
        prefer_local_model=_parse_bool(os.getenv("LRA_PREFER_LOCAL_MODEL"), default=True),
        demo_admin_token=(os.getenv("LRA_demo_ADMIN_TOKEN") or "").strip() or None,
        admin_phones=_parse_phone_csv(os.getenv("LRA_ADMIN_PHONES")),
        auth_token_ttl_sec=int(os.getenv("LRA_AUTH_TOKEN_TTL_SEC", "604800")),
        health_provider=os.getenv("LRA_HEALTH_PROVIDER", "mock").strip() or "mock",
        map_provider=os.getenv("LRA_MAP_PROVIDER", "demo").strip() or "demo",
        amap_web_key=(os.getenv("LRA_AMAP_WEB_KEY") or "").strip() or None,
        amap_web_security_js_code=(os.getenv("LRA_AMAP_WEB_SECURITY_JS_CODE") or "").strip() or None,
        amap_service_key=(os.getenv("LRA_AMAP_SERVICE_KEY") or "").strip() or None,
        map_distance_timeout_sec=int(os.getenv("LRA_MAP_DISTANCE_TIMEOUT_SEC", "3")),
        audit_log_enabled=_parse_bool(os.getenv("LRA_AUDIT_LOG_ENABLED"), default=True),
        rate_limit_enabled=_parse_bool(os.getenv("LRA_RATE_LIMIT_ENABLED"), default=True),
        rate_limit_auth_per_minute=int(os.getenv("LRA_RATE_LIMIT_AUTH_PER_MINUTE", "20")),
        rate_limit_admin_per_minute=int(os.getenv("LRA_RATE_LIMIT_ADMIN_PER_MINUTE", "60")),
        rate_limit_actor_per_minute=int(os.getenv("LRA_RATE_LIMIT_ACTOR_PER_MINUTE", "120")),
        push_provider=os.getenv("LRA_PUSH_PROVIDER", "websocket").strip() or "websocket",
    )
