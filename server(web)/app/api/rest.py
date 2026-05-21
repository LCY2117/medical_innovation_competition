import hmac
import hashlib
import threading
import time
import uuid
from collections import defaultdict, deque
from urllib.parse import quote

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import Response

from app.core.config import Settings
from app.core.frontend import frontend_health
from app.models.schemas import (
    ActionReq,
    AuditEvent,
    AuditLogResponse,
    AedSiteListResponse,
    AedSiteUpsertReq,
    AuthMeResponse,
    AuthLoginReq,
    AuthDemoReq,
    AuthResponse,
    AuthRegisterReq,
    AutoJoinReq,
    AutoJoinResponse,
    ClientHealthUpdateReq,
    ClientListResponse,
    ClientLocationUpdateReq,
    ClientRegisterReq,
    ClientRegisterResponse,
    CreateIncidentResponse,
    DemoBootstrapResponse,
    DispatchExplainResponse,
    DispatchReq,
    DispatchResponse,
    ExperimentExportResponse,
    HealthDetailResponse,
    HealthResponse,
    IncidentState,
    JoinReq,
    MutationResponse,
    SimpleOkResponse,
)
from app.services.auth import AuthService
from app.services.incidents import IncidentService


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, limit: int, window_sec: int = 60) -> None:
        if limit <= 0:
            return
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] > window_sec:
                hits.popleft()
            if len(hits) >= limit:
                raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
            hits.append(now)


def build_rest_router(service: IncidentService, auth_service: AuthService, settings: Settings) -> APIRouter:
    router = APIRouter()
    limiter = SlidingWindowRateLimiter()

    def now_ms() -> int:
        return int(time.time() * 1000)

    def request_hash(request: Request) -> str:
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        raw = f"{client_host}|{user_agent}".encode("utf-8", errors="ignore")
        return hashlib.sha256(raw).hexdigest()[:16]

    def rate_limit(request: Request, bucket: str, limit: int, actor_id: str | None = None) -> None:
        if not settings.rate_limit_enabled:
            return
        identity = actor_id or request_hash(request)
        limiter.check(f"{bucket}:{identity}", limit)

    def audit(
        request: Request,
        event_type: str,
        actor_type: str,
        actor_id: str | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        outcome: str = "success",
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> None:
        if not settings.audit_log_enabled:
            return
        safe_metadata = dict(metadata or {})
        safe_metadata.setdefault("path", request.url.path)
        try:
            service.record_audit_event(
                AuditEvent(
                    eventId=str(uuid.uuid4()),
                    ts=now_ms(),
                    eventType=event_type,
                    actorType=actor_type,
                    actorId=actor_id,
                    targetType=target_type,
                    targetId=target_id,
                    outcome=outcome,
                    requestHash=request_hash(request),
                    metadata=safe_metadata,
                )
            )
        except Exception:
            pass

    def is_demo_admin_authorized(x_demo_admin_token: str | None) -> bool:
        if not settings.demo_admin_token:
            return False
        header_token = (x_demo_admin_token or "").strip()
        return bool(header_token) and hmac.compare_digest(header_token, settings.demo_admin_token)

    def require_admin(
        request: Request,
        authorization: str | None = Header(default=None),
        x_demo_admin_token: str | None = Header(default=None),
    ) -> str:
        rate_limit(request, "admin", settings.rate_limit_admin_per_minute)
        if is_demo_admin_authorized(x_demo_admin_token):
            return "demo_admin"
        if authorization:
            try:
                user = auth_service.require_admin_user(authorization)
            except HTTPException as exc:
                audit(
                    request,
                    "admin_user_denied",
                    "user",
                    outcome="denied",
                    metadata={"statusCode": exc.status_code},
                )
                raise
            return user.user_id
        if settings.demo_admin_token or settings.admin_phones:
            denied_event = "demo_admin_denied" if settings.demo_admin_token else "admin_denied"
            audit(request, denied_event, "anonymous", outcome="denied")
            raise HTTPException(status_code=403, detail="缺少有效管理员权限")
        return "open_demo_admin"

    def require_actor_when_public_demo_is_protected(
        user_id: str,
        request: Request,
        authorization: str | None,
        x_demo_admin_token: str | None,
    ) -> None:
        if not settings.demo_admin_token:
            return
        if is_demo_admin_authorized(x_demo_admin_token):
            return
        user = auth_service.require_user(authorization)
        if auth_service.is_admin_user(user):
            return
        if user.user_id != user_id:
            audit(
                request,
                "actor_user_mismatch",
                "user",
                actor_id=user.user_id,
                target_type="client",
                target_id=user_id,
                outcome="denied",
            )
            raise HTTPException(status_code=403, detail="终端 userId 与登录账号不一致")

    @router.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(ok=True)

    @router.get("/health/detail", response_model=HealthDetailResponse)
    async def health_detail() -> HealthDetailResponse:
        details = service.health()
        details["frontend"] = frontend_health(settings)
        details["version"] = "competition-hardening"
        details["auth"] = {
            "tokenTtlSec": settings.auth_token_ttl_sec,
            "demoAdminAuthEnabled": settings.demo_admin_token is not None,
            "adminAccountAuthEnabled": bool(settings.admin_phones),
            "adminPhoneCount": len(settings.admin_phones),
        }
        details["features"] = {
            "experimentJsonExport": True,
            "experimentZipPackage": True,
            "mobileWeb": True,
            "androidMockHealthSync": True,
            "oppoHealthRealSdk": False,
        }
        details["healthProvider"] = {
            "mode": settings.health_provider,
            "mockFallbackEnabled": True,
            "realOppoBlockedByApproval": settings.health_provider.lower() != "mock",
        }
        details["security"] = {
            "auditLogEnabled": settings.audit_log_enabled,
            "rateLimitEnabled": settings.rate_limit_enabled,
            "rateLimitAuthPerMinute": settings.rate_limit_auth_per_minute,
            "rateLimitAdminPerMinute": settings.rate_limit_admin_per_minute,
            "rateLimitActorPerMinute": settings.rate_limit_actor_per_minute,
            "adminAccountAuthEnabled": bool(settings.admin_phones),
            "adminPhoneCount": len(settings.admin_phones),
        }
        details["demoAdminAuthEnabled"] = settings.demo_admin_token is not None
        return HealthDetailResponse(**details)

    @router.post("/incidents", response_model=CreateIncidentResponse)
    async def create_incident(request: Request, admin: str = Depends(require_admin)) -> CreateIncidentResponse:
        response = service.create_incident()
        audit(request, "incident_created", "admin", actor_id=admin, target_type="incident", target_id=response.incidentId)
        return response

    @router.post("/auth/register", response_model=AuthResponse)
    async def register(req: AuthRegisterReq, request: Request) -> AuthResponse:
        rate_limit(request, "auth", settings.rate_limit_auth_per_minute)
        try:
            response = auth_service.register(
                display_name=req.displayName,
                phone=req.phone,
                password=req.password,
                organization=req.organization,
                health_condition=req.healthCondition,
                profession_identity=req.professionIdentity,
                profile_bio=req.profileBio,
            )
        except HTTPException as exc:
            audit(request, "auth_register", "anonymous", outcome="denied", metadata={"statusCode": exc.status_code})
            raise
        audit(
            request,
            "auth_register",
            "user",
            actor_id=response.user.userId,
            target_type="user",
            target_id=response.user.userId,
            metadata={"credentialStatus": response.user.credentialStatus},
        )
        return response

    @router.post("/auth/login", response_model=AuthResponse)
    async def login(req: AuthLoginReq, request: Request) -> AuthResponse:
        rate_limit(request, "auth", settings.rate_limit_auth_per_minute)
        try:
            response = auth_service.login(phone=req.phone, password=req.password)
        except HTTPException as exc:
            audit(request, "auth_login", "anonymous", outcome="denied", metadata={"statusCode": exc.status_code})
            raise
        audit(request, "auth_login", "user", actor_id=response.user.userId, target_type="user", target_id=response.user.userId)
        return response

    @router.post("/auth/demo", response_model=AuthResponse)
    async def demo_login(req: AuthDemoReq, request: Request) -> AuthResponse:
        rate_limit(request, "auth", settings.rate_limit_auth_per_minute)
        response = auth_service.demo_login(req.persona)
        audit(
            request,
            "auth_demo_login",
            "user",
            actor_id=response.user.userId,
            target_type="user",
            target_id=response.user.userId,
            metadata={"persona": req.persona.strip().lower()},
        )
        return response

    @router.get("/auth/me", response_model=AuthMeResponse)
    async def auth_me(authorization: str | None = Header(default=None)) -> AuthMeResponse:
        return auth_service.me(authorization)

    @router.post("/auth/logout", response_model=SimpleOkResponse)
    async def logout(request: Request, authorization: str | None = Header(default=None)) -> SimpleOkResponse:
        user = auth_service.require_user(authorization)
        response = auth_service.logout(authorization)
        audit(request, "auth_logout", "user", actor_id=user.user_id, target_type="user", target_id=user.user_id)
        return response

    @router.post("/clients/register", response_model=ClientRegisterResponse)
    async def register_client(
        req: ClientRegisterReq,
        request: Request,
        authorization: str | None = Header(default=None),
    ) -> ClientRegisterResponse:
        user = auth_service.require_user(authorization)
        if req.userId != user.user_id:
            raise HTTPException(status_code=403, detail="终端 userId 与登录账号不一致")
        service.register_client(
            user.user_id,
            user.display_name,
            user.organization,
            user.health_condition,
            user.profession_identity,
            user.profile_bio,
            req.deviceType,
            req.location,
            req.healthSignals,
        )
        audit(
            request,
            "client_registered",
            "user",
            actor_id=user.user_id,
            target_type="client",
            target_id=user.user_id,
            metadata={"deviceType": req.deviceType},
        )
        return ClientRegisterResponse(userId=user.user_id)

    @router.get("/clients", response_model=ClientListResponse)
    async def list_clients() -> ClientListResponse:
        return ClientListResponse(clients=service.list_clients())

    @router.post("/clients/location", response_model=ClientRegisterResponse)
    async def update_client_location(
        req: ClientLocationUpdateReq,
        request: Request,
        authorization: str | None = Header(default=None),
    ) -> ClientRegisterResponse:
        rate_limit(request, "actor", settings.rate_limit_actor_per_minute, req.userId)
        user = auth_service.require_user(authorization)
        if req.userId != user.user_id:
            raise HTTPException(status_code=403, detail="终端 userId 与登录账号不一致")
        client = service.update_client_location(req.userId, req.location)
        audit(
            request,
            "client_location_updated",
            "user",
            actor_id=user.user_id,
            target_type="client",
            target_id=client.userId,
            metadata={"source": req.location.source, "hasLabel": bool(req.location.label)},
        )
        return ClientRegisterResponse(userId=client.userId)

    @router.post("/clients/health", response_model=ClientRegisterResponse)
    async def update_client_health(
        req: ClientHealthUpdateReq,
        request: Request,
        authorization: str | None = Header(default=None),
    ) -> ClientRegisterResponse:
        rate_limit(request, "actor", settings.rate_limit_actor_per_minute, req.userId)
        user = auth_service.require_user(authorization)
        if req.userId != user.user_id:
            raise HTTPException(status_code=403, detail="终端 userId 与登录账号不一致")
        client = service.update_client_health(req.userId, req.healthSignals)
        audit(
            request,
            "client_health_updated",
            "user",
            actor_id=user.user_id,
            target_type="client",
            target_id=client.userId,
            metadata={"source": req.healthSignals.source, "authorizationStatus": req.healthSignals.authorizationStatus},
        )
        return ClientRegisterResponse(userId=client.userId)

    @router.get("/aed-sites", response_model=AedSiteListResponse)
    async def list_aed_sites() -> AedSiteListResponse:
        return AedSiteListResponse(aedSites=service.list_aed_sites())

    @router.post("/aed-sites", response_model=AedSiteListResponse)
    async def upsert_aed_site(
        req: AedSiteUpsertReq,
        request: Request,
        admin: str = Depends(require_admin),
    ) -> AedSiteListResponse:
        site = service.upsert_aed_site(
            site_id=req.siteId,
            name=req.name,
            location=req.location,
            status=req.status,
            access_notes=req.accessNotes,
        )
        audit(
            request,
            "aed_site_upserted",
            "admin",
            actor_id=admin,
            target_type="aed_site",
            target_id=site.siteId,
            metadata={"status": site.status, "hasAccessNotes": bool(site.accessNotes)},
        )
        return AedSiteListResponse(aedSites=service.list_aed_sites())

    @router.get("/dispatch/meta", response_model=DispatchExplainResponse)
    async def dispatch_meta() -> DispatchExplainResponse:
        return DispatchExplainResponse(**service.dispatch_explain())

    @router.get("/incidents/current", response_model=IncidentState)
    async def get_current_incident() -> IncidentState:
        return service.get_current_incident()

    @router.post("/incidents/current/reset", response_model=MutationResponse)
    async def reset_current_incident(request: Request, admin: str = Depends(require_admin)) -> MutationResponse:
        response = await service.reset_current_incident()
        audit(request, "incident_reset", "admin", actor_id=admin, target_type="incident", target_id=response.incidentId)
        return response

    @router.post("/demo/bootstrap", response_model=DemoBootstrapResponse)
    async def demo_bootstrap(request: Request, admin: str = Depends(require_admin)) -> DemoBootstrapResponse:
        response = await service.bootstrap_demo()
        audit(
            request,
            "demo_bootstrapped",
            "admin",
            actor_id=admin,
            target_type="incident",
            target_id=response.incidentId,
            metadata={"clients": len(response.clients), "aedSites": len(response.aedSites)},
        )
        return response

    @router.get("/experiments/current/export", response_model=ExperimentExportResponse)
    async def export_current_experiment(request: Request, admin: str = Depends(require_admin)) -> ExperimentExportResponse:
        response = service.export_experiment()
        audit(request, "experiment_exported", "admin", actor_id=admin, target_type="incident", target_id=response.incidentId)
        return response

    @router.get("/experiments/current/package")
    async def export_current_experiment_package(request: Request, admin: str = Depends(require_admin)) -> Response:
        filename, content = service.export_experiment_package()
        audit(
            request,
            "experiment_package_exported",
            "admin",
            actor_id=admin,
            target_type="incident",
            target_id=service.get_current_incident().incidentId,
            metadata={"bytes": len(content)},
        )
        return Response(
            content=content,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
        )

    @router.get("/experiments/{incident_id}/export", response_model=ExperimentExportResponse)
    async def export_experiment(
        incident_id: str,
        request: Request,
        admin: str = Depends(require_admin),
    ) -> ExperimentExportResponse:
        response = service.export_experiment(incident_id)
        audit(request, "experiment_exported", "admin", actor_id=admin, target_type="incident", target_id=response.incidentId)
        return response

    @router.get("/experiments/{incident_id}/package")
    async def export_experiment_package(
        incident_id: str,
        request: Request,
        admin: str = Depends(require_admin),
    ) -> Response:
        filename, content = service.export_experiment_package(incident_id)
        audit(
            request,
            "experiment_package_exported",
            "admin",
            actor_id=admin,
            target_type="incident",
            target_id=incident_id,
            metadata={"bytes": len(content)},
        )
        return Response(
            content=content,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
        )

    @router.post("/incidents/current/designate_patient", response_model=DispatchResponse)
    async def designate_patient(
        req: DispatchReq,
        request: Request,
        admin: str = Depends(require_admin),
    ) -> DispatchResponse:
        response = await service.designate_patient(req.patientUserId)
        audit(
            request,
            "patient_designated",
            "admin",
            actor_id=admin,
            target_type="incident",
            target_id=response.incidentId,
            metadata={"patientUserId": response.patientUserId, "source": response.source},
        )
        return response

    @router.post("/incidents/current/join_auto", response_model=AutoJoinResponse)
    async def join_current_auto(
        req: AutoJoinReq,
        request: Request,
        authorization: str | None = Header(default=None),
        x_demo_admin_token: str | None = Header(default=None),
    ) -> AutoJoinResponse:
        require_actor_when_public_demo_is_protected(req.userId, request, authorization, x_demo_admin_token)
        rate_limit(request, "actor", settings.rate_limit_actor_per_minute, req.userId)
        response = await service.join_current_auto(req.userId)
        audit(
            request,
            "role_auto_joined",
            "client",
            actor_id=req.userId,
            target_type="incident",
            target_id=response.incidentId,
            metadata={"role": response.role},
        )
        return response

    @router.get("/incidents/{incident_id}", response_model=IncidentState)
    async def get_incident(incident_id: str) -> IncidentState:
        return service.get_incident(incident_id)

    @router.post("/incidents/{incident_id}/join", response_model=MutationResponse)
    async def join_incident(
        incident_id: str,
        req: JoinReq,
        request: Request,
        authorization: str | None = Header(default=None),
        x_demo_admin_token: str | None = Header(default=None),
    ) -> MutationResponse:
        require_actor_when_public_demo_is_protected(req.userId, request, authorization, x_demo_admin_token)
        rate_limit(request, "actor", settings.rate_limit_actor_per_minute, req.userId)
        response = await service.join_incident(incident_id, req.role, req.userId)
        audit(
            request,
            "role_joined",
            "client",
            actor_id=req.userId,
            target_type="incident",
            target_id=incident_id,
            metadata={"role": req.role.upper()},
        )
        return response

    @router.post("/incidents/{incident_id}/actions", response_model=MutationResponse)
    async def post_action(
        incident_id: str,
        req: ActionReq,
        request: Request,
        authorization: str | None = Header(default=None),
        x_demo_admin_token: str | None = Header(default=None),
    ) -> MutationResponse:
        require_actor_when_public_demo_is_protected(req.userId, request, authorization, x_demo_admin_token)
        rate_limit(request, "actor", settings.rate_limit_actor_per_minute, req.userId)
        response = await service.post_action(incident_id, req.action, req.userId)
        audit(
            request,
            "incident_action_posted",
            "client",
            actor_id=req.userId,
            target_type="incident",
            target_id=incident_id,
            metadata={"action": req.action.upper()},
        )
        return response

    @router.post("/incidents/{incident_id}/sos_start", response_model=MutationResponse)
    async def sos_start(
        incident_id: str,
        request: Request,
        admin: str = Depends(require_admin),
    ) -> MutationResponse:
        response = await service.sos_start(incident_id)
        audit(request, "sos_started", "admin", actor_id=admin, target_type="incident", target_id=incident_id)
        return response

    @router.post("/incidents/{incident_id}/sos_cancel", response_model=MutationResponse)
    async def sos_cancel(
        incident_id: str,
        request: Request,
        admin: str = Depends(require_admin),
    ) -> MutationResponse:
        response = await service.sos_cancel(incident_id)
        audit(request, "sos_cancelled", "admin", actor_id=admin, target_type="incident", target_id=incident_id)
        return response

    @router.post("/incidents/{incident_id}/patient_sos_start", response_model=MutationResponse)
    async def patient_sos_start(
        incident_id: str,
        request: Request,
        authorization: str | None = Header(default=None),
    ) -> MutationResponse:
        user = auth_service.require_user(authorization)
        rate_limit(request, "actor", settings.rate_limit_actor_per_minute, user.user_id)
        response = await service.patient_sos_start(incident_id, user.user_id)
        audit(request, "patient_sos_started", "user", actor_id=user.user_id, target_type="incident", target_id=incident_id)
        return response

    @router.post("/incidents/{incident_id}/patient_sos_cancel", response_model=MutationResponse)
    async def patient_sos_cancel(
        incident_id: str,
        request: Request,
        authorization: str | None = Header(default=None),
    ) -> MutationResponse:
        user = auth_service.require_user(authorization)
        rate_limit(request, "actor", settings.rate_limit_actor_per_minute, user.user_id)
        response = await service.patient_sos_cancel(incident_id, user.user_id)
        audit(request, "patient_sos_cancelled", "user", actor_id=user.user_id, target_type="incident", target_id=incident_id)
        return response

    @router.post("/incidents/{incident_id}/trigger", response_model=MutationResponse)
    async def trigger_incident(
        incident_id: str,
        request: Request,
        admin: str = Depends(require_admin),
    ) -> MutationResponse:
        response = await service.trigger_incident(incident_id)
        audit(request, "incident_triggered", "admin", actor_id=admin, target_type="incident", target_id=incident_id)
        return response

    @router.get("/audit/events", response_model=AuditLogResponse)
    async def list_audit_events(
        request: Request,
        limit: int = Query(default=100, ge=1, le=500),
        admin: str = Depends(require_admin),
    ) -> AuditLogResponse:
        events = service.list_audit_events(limit)
        audit(request, "audit_events_viewed", "admin", actor_id=admin, target_type="audit_log", metadata={"limit": limit})
        return AuditLogResponse(events=events)

    return router
