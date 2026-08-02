"""应用配置：环境变量 + 常量。"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


@dataclass
class Settings:
    """全部配置项。测试可通过 create_app(settings=Settings(...)) 注入。"""

    # ---- JWT ----
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))

    # ---- 数据库 ----
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./lifereflex.db")

    # ---- CORS ----
    cors_origins: list[str] = field(
        default_factory=lambda: [
            o.strip()
            for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
            if o.strip()
        ]
    )

    # ---- 状态机 ----
    max_shocks: int = int(os.getenv("MAX_SHOCKS", "3"))  # 除颤上限
    dispatch_timeout: float = _env_float("DISPATCH_TIMEOUT", 10.0)  # 分派超时(秒)
    confirm_timeout: float = _env_float("CONFIRM_TIMEOUT", 10.0)  # 未确认递补超时(秒)

    # ---- 分派打分常量 ----
    prime_radius_km: float = _env_float("PRIME_RADIUS_KM", 5.0)  # 距离归一化半径

    # ---- 演示/种子 ----
    seed_on_startup: bool = _env_bool("SEED_ON_STARTUP", True)
    demo_password: str = os.getenv("DEMO_PASSWORD", "demo1234")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin1234")

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent  # backend/


settings = Settings()
