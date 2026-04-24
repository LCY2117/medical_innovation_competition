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
    local_model_base_url: str | None = None
    local_model_name: str = "default"
    local_model_timeout_sec: int = 30
    prefer_local_model: bool = True


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
        sos_duration_sec=int(os.getenv("LRA_SOS_DURATION_SEC", "10")),
        dispatch_delay_sec=int(os.getenv("LRA_DISPATCH_DELAY_SEC", "3")),
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
        local_model_base_url=os.getenv("LRA_LOCAL_MODEL_BASE_URL", "http://localhost:8008/v1").rstrip("/") if os.getenv("LRA_LOCAL_MODEL_BASE_URL") else None,
        local_model_name=os.getenv("LRA_LOCAL_MODEL_NAME", "default"),
        local_model_timeout_sec=int(os.getenv("LRA_LOCAL_MODEL_TIMEOUT_SEC", "30")),
        prefer_local_model=_parse_bool(os.getenv("LRA_PREFER_LOCAL_MODEL"), default=True),
    )
