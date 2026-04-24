from pydantic import BaseModel


class AuthRegisterReq(BaseModel):
    displayName: str
    phone: str
    password: str
    organization: str
    healthCondition: str
    professionIdentity: str
    profileBio: str


class AuthLoginReq(BaseModel):
    phone: str
    password: str


class AuthUser(BaseModel):
    userId: str
    displayName: str
    phone: str
    organization: str
    healthCondition: str
    professionIdentity: str
    profileBio: str
    credentialStatus: str


class AuthResponse(BaseModel):
    ok: bool = True
    token: str
    user: AuthUser


class JoinReq(BaseModel):
    role: str
    userId: str


class ActionReq(BaseModel):
    action: str
    userId: str


class AutoJoinReq(BaseModel):
    userId: str


class ClientRegisterReq(BaseModel):
    userId: str
    displayName: str
    organization: str
    healthCondition: str
    professionIdentity: str
    profileBio: str
    deviceType: str = "ANDROID"


class ClientInfo(BaseModel):
    userId: str
    displayName: str
    organization: str
    healthCondition: str
    professionIdentity: str
    profileBio: str
    deviceType: str = "ANDROID"
    online: bool = True
    lastSeenTs: int
    assignedRole: str | None = None
    patientCandidate: bool = False
    isPatient: bool = False


class ClientListResponse(BaseModel):
    clients: list[ClientInfo]


class DispatchReq(BaseModel):
    patientUserId: str


class ClientRegisterResponse(BaseModel):
    ok: bool = True
    userId: str


class HealthResponse(BaseModel):
    ok: bool


class HealthDetailResponse(BaseModel):
    ok: bool
    storage: dict
    frontend: dict
    currentIncidentId: str | None = None
    loadedIncidents: int
    activeWebSockets: int
    activeSosTimers: int


class IncidentLogEntry(BaseModel):
    ts: int
    msg: str


class RoleState(BaseModel):
    status: str | None = None
    userId: str | None = None


class RoleStates(BaseModel):
    PRIME: RoleState
    RUNNER: RoleState
    GUIDE: RoleState


class SosState(BaseModel):
    status: str
    startTs: int | None = None
    durationSec: int


class IncidentState(BaseModel):
    incidentId: str
    phase: str
    sos: SosState
    roles: RoleStates
    logs: list[IncidentLogEntry]
    patientUserId: str | None = None
    dispatchSource: str | None = None


class CreateIncidentResponse(BaseModel):
    incidentId: str


class MutationResponse(BaseModel):
    ok: bool = True
    incidentId: str
    phase: str | None = None


class AutoJoinResponse(BaseModel):
    ok: bool = True
    incidentId: str
    role: str


class DispatchResponse(BaseModel):
    ok: bool = True
    incidentId: str
    patientUserId: str
    assignments: dict[str, str | None]
    source: str


class DispatchExplainResponse(BaseModel):
    configured: bool
    provider: str
    dispatchDelaySec: int
    model: str
    baseUrl: str
    timeoutSec: int
    configFile: str
    envKeys: list[str]
    candidateFields: list[str]
    selectionRules: dict[str, str]
    responseFormat: dict[str, str]
    systemPrompt: str
