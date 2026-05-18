import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from app.core.config import Settings
from app.core.frontend import frontend_ready
from app.models.schemas import (
    ActionReq,
    AedSiteListResponse,
    AedSiteUpsertReq,
    AuthMeResponse,
    AuthLoginReq,
    AuthDemoReq,
    AuthResponse,
    AuthRegisterReq,
    AutoJoinReq,
    AutoJoinResponse,
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


def build_rest_router(service: IncidentService, auth_service: AuthService, settings: Settings) -> APIRouter:
    router = APIRouter()

    def require_demo_admin(request: Request, x_demo_admin_token: str | None = Header(default=None)) -> None:
        if not settings.demo_admin_token:
            return
        if is_demo_admin_authorized(request, x_demo_admin_token):
            return
        raise HTTPException(status_code=403, detail="缺少有效演示管理员口令")

    def is_demo_admin_authorized(request: Request, x_demo_admin_token: str | None) -> bool:
        if not settings.demo_admin_token:
            return True
        header_token = (x_demo_admin_token or "").strip()
        return bool(header_token) and hmac.compare_digest(header_token, settings.demo_admin_token)

    def require_actor_when_public_demo_is_protected(
        user_id: str,
        request: Request,
        authorization: str | None,
        x_demo_admin_token: str | None,
    ) -> None:
        if not settings.demo_admin_token:
            return
        if is_demo_admin_authorized(request, x_demo_admin_token):
            return
        user = auth_service.require_user(authorization)
        if user.user_id != user_id:
            raise HTTPException(status_code=403, detail="终端 userId 与登录账号不一致")

    @router.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(ok=True)

    @router.get("/health/detail", response_model=HealthDetailResponse)
    async def health_detail() -> HealthDetailResponse:
        details = service.health()
        details["frontend"] = {
            "ok": frontend_ready(settings),
            "webDistDir": str(settings.web_dist_dir),
        }
        details["demoAdminAuthEnabled"] = settings.demo_admin_token is not None
        return HealthDetailResponse(**details)

    @router.post("/incidents", response_model=CreateIncidentResponse)
    async def create_incident(admin: None = Depends(require_demo_admin)) -> CreateIncidentResponse:
        return service.create_incident()

    @router.post("/auth/register", response_model=AuthResponse)
    async def register(req: AuthRegisterReq) -> AuthResponse:
        return auth_service.register(
            display_name=req.displayName,
            phone=req.phone,
            password=req.password,
            organization=req.organization,
            health_condition=req.healthCondition,
            profession_identity=req.professionIdentity,
            profile_bio=req.profileBio,
        )

    @router.post("/auth/login", response_model=AuthResponse)
    async def login(req: AuthLoginReq) -> AuthResponse:
        return auth_service.login(phone=req.phone, password=req.password)

    @router.post("/auth/demo", response_model=AuthResponse)
    async def demo_login(req: AuthDemoReq) -> AuthResponse:
        return auth_service.demo_login(req.persona)

    @router.get("/auth/me", response_model=AuthMeResponse)
    async def auth_me(authorization: str | None = Header(default=None)) -> AuthMeResponse:
        return auth_service.me(authorization)

    @router.post("/auth/logout", response_model=SimpleOkResponse)
    async def logout(authorization: str | None = Header(default=None)) -> SimpleOkResponse:
        return auth_service.logout(authorization)

    @router.post("/clients/register", response_model=ClientRegisterResponse)
    async def register_client(
        req: ClientRegisterReq,
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
        )
        return ClientRegisterResponse(userId=user.user_id)

    @router.get("/clients", response_model=ClientListResponse)
    async def list_clients() -> ClientListResponse:
        return ClientListResponse(clients=service.list_clients())

    @router.post("/clients/location", response_model=ClientRegisterResponse)
    async def update_client_location(
        req: ClientLocationUpdateReq,
        authorization: str | None = Header(default=None),
    ) -> ClientRegisterResponse:
        user = auth_service.require_user(authorization)
        if req.userId != user.user_id:
            raise HTTPException(status_code=403, detail="终端 userId 与登录账号不一致")
        client = service.update_client_location(req.userId, req.location)
        return ClientRegisterResponse(userId=client.userId)

    @router.get("/aed-sites", response_model=AedSiteListResponse)
    async def list_aed_sites() -> AedSiteListResponse:
        return AedSiteListResponse(aedSites=service.list_aed_sites())

    @router.post("/aed-sites", response_model=AedSiteListResponse)
    async def upsert_aed_site(
        req: AedSiteUpsertReq,
        admin: None = Depends(require_demo_admin),
    ) -> AedSiteListResponse:
        service.upsert_aed_site(
            site_id=req.siteId,
            name=req.name,
            location=req.location,
            status=req.status,
            access_notes=req.accessNotes,
        )
        return AedSiteListResponse(aedSites=service.list_aed_sites())

    @router.get("/dispatch/meta", response_model=DispatchExplainResponse)
    async def dispatch_meta() -> DispatchExplainResponse:
        return DispatchExplainResponse(**service.dispatch_explain())

    @router.get("/incidents/current", response_model=IncidentState)
    async def get_current_incident() -> IncidentState:
        return service.get_current_incident()

    @router.post("/incidents/current/reset", response_model=MutationResponse)
    async def reset_current_incident(admin: None = Depends(require_demo_admin)) -> MutationResponse:
        return await service.reset_current_incident()

    @router.post("/demo/bootstrap", response_model=DemoBootstrapResponse)
    async def demo_bootstrap(admin: None = Depends(require_demo_admin)) -> DemoBootstrapResponse:
        return await service.bootstrap_demo()

    @router.get("/experiments/current/export", response_model=ExperimentExportResponse)
    async def export_current_experiment(admin: None = Depends(require_demo_admin)) -> ExperimentExportResponse:
        return service.export_experiment()

    @router.get("/experiments/{incident_id}/export", response_model=ExperimentExportResponse)
    async def export_experiment(
        incident_id: str,
        admin: None = Depends(require_demo_admin),
    ) -> ExperimentExportResponse:
        return service.export_experiment(incident_id)

    @router.post("/incidents/current/designate_patient", response_model=DispatchResponse)
    async def designate_patient(
        req: DispatchReq,
        admin: None = Depends(require_demo_admin),
    ) -> DispatchResponse:
        return await service.designate_patient(req.patientUserId)

    @router.post("/incidents/current/join_auto", response_model=AutoJoinResponse)
    async def join_current_auto(
        req: AutoJoinReq,
        request: Request,
        authorization: str | None = Header(default=None),
        x_demo_admin_token: str | None = Header(default=None),
    ) -> AutoJoinResponse:
        require_actor_when_public_demo_is_protected(req.userId, request, authorization, x_demo_admin_token)
        return await service.join_current_auto(req.userId)

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
        return await service.join_incident(incident_id, req.role, req.userId)

    @router.post("/incidents/{incident_id}/actions", response_model=MutationResponse)
    async def post_action(
        incident_id: str,
        req: ActionReq,
        request: Request,
        authorization: str | None = Header(default=None),
        x_demo_admin_token: str | None = Header(default=None),
    ) -> MutationResponse:
        require_actor_when_public_demo_is_protected(req.userId, request, authorization, x_demo_admin_token)
        return await service.post_action(incident_id, req.action, req.userId)

    @router.post("/incidents/{incident_id}/sos_start", response_model=MutationResponse)
    async def sos_start(incident_id: str) -> MutationResponse:
        return await service.sos_start(incident_id)

    @router.post("/incidents/{incident_id}/sos_cancel", response_model=MutationResponse)
    async def sos_cancel(incident_id: str) -> MutationResponse:
        return await service.sos_cancel(incident_id)

    @router.post("/incidents/{incident_id}/patient_sos_start", response_model=MutationResponse)
    async def patient_sos_start(
        incident_id: str,
        authorization: str | None = Header(default=None),
    ) -> MutationResponse:
        user = auth_service.require_user(authorization)
        return await service.patient_sos_start(incident_id, user.user_id)

    @router.post("/incidents/{incident_id}/patient_sos_cancel", response_model=MutationResponse)
    async def patient_sos_cancel(
        incident_id: str,
        authorization: str | None = Header(default=None),
    ) -> MutationResponse:
        user = auth_service.require_user(authorization)
        return await service.patient_sos_cancel(incident_id, user.user_id)

    @router.post("/incidents/{incident_id}/trigger", response_model=MutationResponse)
    async def trigger_incident(incident_id: str) -> MutationResponse:
        return await service.trigger_incident(incident_id)

    return router
