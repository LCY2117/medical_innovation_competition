from fastapi import APIRouter, Header, HTTPException

from app.core.config import Settings
from app.core.frontend import frontend_ready
from app.models.schemas import (
    ActionReq,
    AuthLoginReq,
    AuthResponse,
    AuthRegisterReq,
    AutoJoinReq,
    AutoJoinResponse,
    ClientListResponse,
    ClientRegisterReq,
    ClientRegisterResponse,
    CreateIncidentResponse,
    DispatchExplainResponse,
    DispatchReq,
    DispatchResponse,
    HealthDetailResponse,
    HealthResponse,
    IncidentState,
    JoinReq,
    MutationResponse,
)
from app.services.auth import AuthService
from app.services.incidents import IncidentService


def build_rest_router(service: IncidentService, auth_service: AuthService, settings: Settings) -> APIRouter:
    router = APIRouter()

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
        return HealthDetailResponse(**details)

    @router.post("/incidents", response_model=CreateIncidentResponse)
    async def create_incident() -> CreateIncidentResponse:
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
        )
        return ClientRegisterResponse(userId=user.user_id)

    @router.get("/clients", response_model=ClientListResponse)
    async def list_clients() -> ClientListResponse:
        return ClientListResponse(clients=service.list_clients())

    @router.get("/dispatch/meta", response_model=DispatchExplainResponse)
    async def dispatch_meta() -> DispatchExplainResponse:
        return DispatchExplainResponse(**service.dispatch_explain())

    @router.get("/incidents/current", response_model=IncidentState)
    async def get_current_incident() -> IncidentState:
        return service.get_current_incident()

    @router.post("/incidents/current/reset", response_model=MutationResponse)
    async def reset_current_incident() -> MutationResponse:
        return await service.reset_current_incident()

    @router.post("/incidents/current/designate_patient", response_model=DispatchResponse)
    async def designate_patient(req: DispatchReq) -> DispatchResponse:
        return await service.designate_patient(req.patientUserId)

    @router.post("/incidents/current/join_auto", response_model=AutoJoinResponse)
    async def join_current_auto(req: AutoJoinReq) -> AutoJoinResponse:
        return await service.join_current_auto(req.userId)

    @router.get("/incidents/{incident_id}", response_model=IncidentState)
    async def get_incident(incident_id: str) -> IncidentState:
        return service.get_incident(incident_id)

    @router.post("/incidents/{incident_id}/join", response_model=MutationResponse)
    async def join_incident(incident_id: str, req: JoinReq) -> MutationResponse:
        return await service.join_incident(incident_id, req.role, req.userId)

    @router.post("/incidents/{incident_id}/actions", response_model=MutationResponse)
    async def post_action(incident_id: str, req: ActionReq) -> MutationResponse:
        return await service.post_action(incident_id, req.action, req.userId)

    @router.post("/incidents/{incident_id}/sos_start", response_model=MutationResponse)
    async def sos_start(incident_id: str) -> MutationResponse:
        return await service.sos_start(incident_id)

    @router.post("/incidents/{incident_id}/sos_cancel", response_model=MutationResponse)
    async def sos_cancel(incident_id: str) -> MutationResponse:
        return await service.sos_cancel(incident_id)

    @router.post("/incidents/{incident_id}/trigger", response_model=MutationResponse)
    async def trigger_incident(incident_id: str) -> MutationResponse:
        return await service.trigger_incident(incident_id)

    return router
