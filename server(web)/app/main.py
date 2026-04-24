from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.rest import build_rest_router
from app.api.ws import build_ws_router
from app.core.config import Settings, get_settings
from app.core.frontend import mount_frontend
from app.services.auth import AuthService
from app.services.incidents import IncidentService
from app.storage.sqlite_auth_store import SqliteAuthStore
from app.storage.sqlite_store import SqliteIncidentStore


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    store = SqliteIncidentStore(db_path=settings.db_path)
    auth_store = SqliteAuthStore(db_path=settings.db_path)
    auth_service = AuthService(store=auth_store)
    service = IncidentService(
        store=store,
        sos_duration_sec=settings.sos_duration_sec,
        dispatch_delay_sec=settings.dispatch_delay_sec,
        siliconflow_api_key=settings.siliconflow_api_key,
        siliconflow_model=settings.siliconflow_model,
        siliconflow_base_url=settings.siliconflow_base_url,
        siliconflow_timeout_sec=settings.siliconflow_timeout_sec,
        local_model_base_url=settings.local_model_base_url,
        local_model_name=settings.local_model_name,
        local_model_timeout_sec=settings.local_model_timeout_sec,
        prefer_local_model=settings.prefer_local_model,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await service.bootstrap()
        yield

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.settings = settings
    app.state.incident_service = service
    app.state.auth_service = auth_service

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(build_rest_router(service, auth_service, settings))
    app.include_router(build_rest_router(service, auth_service, settings), prefix=settings.api_prefix)
    app.include_router(build_ws_router(service))
    mount_frontend(app, settings)

    return app


app = create_app()
