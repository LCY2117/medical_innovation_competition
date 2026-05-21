from pydantic import BaseModel, Field, field_validator


AED_STATUS_VALUES = {"AVAILABLE", "MAINTENANCE", "UNAVAILABLE"}


class GeoPoint(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracyMeters: float | None = Field(default=None, ge=0, le=50_000)
    label: str | None = None
    floor: str | None = None
    source: str = "manual"
    updatedTs: int | None = Field(default=None, ge=0)


class HealthSignalSummary(BaseModel):
    source: str = "unavailable"
    authorizationStatus: str = "not_connected"
    provider: str = "OPPO_HEALTH"
    heartRateBpm: int | None = Field(default=None, ge=20, le=240)
    bloodOxygenPercent: float | None = Field(default=None, ge=0, le=100)
    pressureScore: int | None = Field(default=None, ge=0, le=100)
    activityLevel: str | None = None
    sleepQuality: str | None = None
    riskTags: list[str] = Field(default_factory=list)
    updatedTs: int | None = None
    note: str | None = None


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


class AuthDemoReq(BaseModel):
    persona: str


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
    tokenExpiresAt: int | None = None


class AuthMeResponse(BaseModel):
    ok: bool = True
    user: AuthUser
    tokenExpiresAt: int | None = None


class SimpleOkResponse(BaseModel):
    ok: bool = True


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
    location: GeoPoint | None = None
    healthSignals: HealthSignalSummary | None = None


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
    location: GeoPoint | None = None
    healthSignals: HealthSignalSummary | None = None


class ClientListResponse(BaseModel):
    clients: list[ClientInfo]


class ClientLocationUpdateReq(BaseModel):
    userId: str
    location: GeoPoint


class ClientHealthUpdateReq(BaseModel):
    userId: str
    healthSignals: HealthSignalSummary


class AedSite(BaseModel):
    siteId: str
    name: str
    location: GeoPoint
    status: str = "AVAILABLE"
    accessNotes: str = ""
    lastCheckedTs: int | None = None

    @field_validator("status")
    @classmethod
    def normalize_status(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in AED_STATUS_VALUES:
            raise ValueError(f"status must be one of {sorted(AED_STATUS_VALUES)}")
        return normalized


class AedSiteUpsertReq(BaseModel):
    siteId: str | None = None
    name: str
    location: GeoPoint
    status: str = "AVAILABLE"
    accessNotes: str = ""

    @field_validator("status")
    @classmethod
    def normalize_status(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in AED_STATUS_VALUES:
            raise ValueError(f"status must be one of {sorted(AED_STATUS_VALUES)}")
        return normalized


class AedSiteListResponse(BaseModel):
    aedSites: list[AedSite]


class DispatchReq(BaseModel):
    patientUserId: str


class ClientRegisterResponse(BaseModel):
    ok: bool = True
    userId: str


class HealthResponse(BaseModel):
    ok: bool


class HealthDetailResponse(BaseModel):
    ok: bool
    version: str | None = None
    storage: dict
    frontend: dict
    auth: dict = {}
    features: dict = {}
    healthProvider: dict = {}
    demoReadiness: dict = {}
    currentIncidentId: str | None = None
    loadedIncidents: int
    registeredClients: int = 0
    registeredAedSites: int = 0
    activeWebSockets: int
    activeSosTimers: int
    dispatch: dict = {}
    demoAdminAuthEnabled: bool = False


class IncidentLogEntry(BaseModel):
    ts: int
    msg: str


class DispatchRoleDecision(BaseModel):
    userId: str | None = None
    score: float = 0
    reasons: list[str] = []
    warnings: list[str] = []
    distanceToPatientMeters: float | None = None
    nearestAedSiteId: str | None = None
    distanceToAedMeters: float | None = None
    aedToPatientMeters: float | None = None


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
    aedSites: list[AedSite] = []
    dispatchRationale: dict[str, DispatchRoleDecision] = {}


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
    rationale: dict[str, DispatchRoleDecision] = {}


class DemoBootstrapResponse(BaseModel):
    ok: bool = True
    incidentId: str
    clients: list[ClientInfo]
    aedSites: list[AedSite]


class ExperimentExportResponse(BaseModel):
    incidentId: str
    generatedAt: int
    phase: str
    patientUserId: str | None
    dispatchSource: str | None
    assignments: dict[str, str | None]
    metrics: dict[str, int | float | None]
    timeline: list[IncidentLogEntry]
    clients: list[ClientInfo]
    aedSites: list[AedSite]
    dispatchRationale: dict[str, DispatchRoleDecision]


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
