"""FastAPI 应用工厂与入口。

本地运行：
    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    aed_api,
    auth,
    demo,
    dispatch_api,
    events,
    health_api,
    ws,
)
from app.config import Settings, settings as default_settings
from app.core.dispatch import DispatchEngine, RuleBasedStrategy
from app.core.websocket_hub import WebSocketHub
from app.db import build_engine, init_db, session_factory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger("lifereflex")


def create_app(settings: Settings | None = None) -> FastAPI:
    """应用工厂。测试可注入自定义 Settings。"""
    settings = settings or default_settings

    engine = build_engine(settings.database_url)
    init_db(engine)

    app = FastAPI(
        title="生命反射弧 Life Reflex Arc",
        description="急救响应协同系统后端（M1）",
        version="0.1.0",
    )

    # 应用级状态
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory(engine)
    app.state.hub = WebSocketHub()
    app.state.dispatch_engine = DispatchEngine(
        strategy=RuleBasedStrategy(),
        max_shocks=settings.max_shocks,
        confirm_timeout=settings.confirm_timeout,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # 启动：种子数据
        from app.seed import seed_if_empty

        if settings.seed_on_startup:
            with app.state.session_factory() as session:
                try:
                    seed_if_empty(session, settings)
                except Exception:  # noqa: BLE001
                    logger.exception("种子数据写入失败")
        # WS 心跳循环
        heartbeat = asyncio.create_task(app.state.hub.heartbeat_loop(30.0))
        logger.info("Life Reflex Arc 后端启动完成")
        yield
        heartbeat.cancel()
        try:
            await heartbeat
        except asyncio.CancelledError:
            pass

    app.router.lifespan_context = lifespan

    # 路由
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(events.router, prefix="/api/v1")
    app.include_router(dispatch_api.router, prefix="/api/v1")
    app.include_router(health_api.router, prefix="/api/v1")
    app.include_router(aed_api.router, prefix="/api/v1")
    app.include_router(demo.router, prefix="/api/v1")
    app.include_router(ws.router)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok", "service": "lifereflex-backend"}

    return app


app = create_app()
