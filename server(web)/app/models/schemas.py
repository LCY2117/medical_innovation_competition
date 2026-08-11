from pydantic import BaseModel, Field, field_validator


AED_STATUS_VALUES = {"AVAILABLE", "MAINTENANCE", "UNAVAILABLE"}
HEALTH_SOURCE_VALUES = {"mock", "manual", "oppo", "oppo_health", "unavailable"}
HEALTH_AUTHORIZATION_VALUES = {"sample", "not_connected", "authorized", "denied"}
HEALTH_ACTIVITY_VALUES = {"low", "normal", "high"}
HEALTH_SLEEP_VALUES = {"poor", "fair", "good"}
HEALTH_RISK_TAG_VALUES = {"tachycardia", "bradycardia", "low_spo2", "high_pressure", "limited_mobility"}


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
    updatedTs: int | None = Field(default=None, ge=0)
    note: str | None = None

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        normalized = value.strip().lower().replace("-", "_")
        if normalized not in HEALTH_SOURCE_VALUES:
            raise ValueError(f"source must be one of {sorted(HEALTH_SOURCE_VALUES)}")
        return normalized

    @field_validator("authorizationStatus")
    @classmethod
    def normalize_authorization_status(cls, value: str) -> str:
        normalized = value.strip().lower().replace("-", "_")
        if normalized not in HEALTH_AUTHORIZATION_VALUES:
            raise ValueError(f"authorizationStatus must be one of {sorted(HEALTH_AUTHORIZATION_VALUES)}")
        return normalized

    @field_validator("activityLevel")
    @classmethod
    def normalize_activity_level(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower().replace("-", "_")
        if normalized not in HEALTH_ACTIVITY_VALUES:
            raise ValueError(f"activityLevel must be one of {sorted(HEALTH_ACTIVITY_VALUES)}")
        return normalized

    @field_validator("sleepQuality")
    @classmethod
    def normalize_sleep_quality(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower().replace("-", "_")
        if normalized not in HEALTH_SLEEP_VALUES:
            raise ValueError(f"sleepQuality must be one of {sorted(HEALTH_SLEEP_VALUES)}")
        return normalized

    @field_validator("riskTags")
    @classmethod
    def normalize_risk_tags(cls, value: list[str]) -> list[str]:
        normalized_tags: list[str] = []
        for tag in value:
            normalized = tag.strip().lower().replace("-", "_")
            if normalized not in HEALTH_RISK_TAG_VALUES:
                raise ValueError(f"riskTags must use values from {sorted(HEALTH_RISK_TAG_VALUES)}")
            if normalized not in normalized_tags:
                normalized_tags.append(normalized)
        return normalized_tags


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


class AuthCodeRequestReq(BaseModel):
    phone: str


class AuthCodeLoginReq(BaseModel):
    phone: str
    code: str


class AuthCodeRegisterReq(BaseModel):
    phone: str
    code: str
    displayName: str
    organization: str
    healthCondition: str
    professionIdentity: str
    profileBio: str


class AuthCodeRequestResponse(BaseModel):
    ok: bool = True
    channel: str = "mock"
    expiresInSec: int = 300
    demoCode: str | None = None


class AuthProfileUpdateReq(BaseModel):
    displayName: str
    organization: str
    healthCondition: str
    professionIdentity: str
    profileBio: str


class AuthdemoReq(BaseModel):
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
    privileges: list[str] = Field(default_factory=list)


class AuthCodeLoginResponse(BaseModel):
    ok: bool = True
    needsProfileSetup: bool
    token: str | None = None
    user: AuthUser | None = None
    tokenExpiresAt: int | None = None
    phone: str | None = None


class AuthResponse(BaseModel):
    ok: bool = True
    token: str
    user: AuthUser
    tokenExpiresAt: int | None = None


class AuthMeResponse(BaseModel):
    ok: bool = True
    user: AuthUser
    tokenExpiresAt: int | None = None


class CreateAiTaskReq(BaseModel):
    userId: str
    message: str


class AiTaskActionReq(BaseModel):
    userId: str


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
    mapProvider: dict = {}
    pushProvider: dict = {}
    demoReadiness: dict = {}
    currentIncidentId: str | None = None
    loadedIncidents: int
    registeredClients: int = 0
    registeredAedSites: int = 0
    activeWebSockets: int
    activeSosTimers: int
    dispatch: dict = {}
    security: dict = {}
    demoAdminAuthEnabled: bool = False


class AuditEvent(BaseModel):
    eventId: str
    ts: int
    eventType: str
    actorType: str
    actorId: str | None = None
    targetType: str | None = None
    targetId: str | None = None
    outcome: str
    requestHash: str | None = None
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class AuditLogResponse(BaseModel):
    events: list[AuditEvent]


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


class AiTaskState(BaseModel):
    taskId: str
    title: str
    description: str
    requiredSkill: str = "fetch"
    priority: int = 3
    locationLabel: str | None = None
    createdBy: str = ""
    createdRole: str = ""
    status: str = "PENDING"
    assignableUserIds: list[str] = []
    runnerUserId: str | None = None
    supportUserIds: list[str] = []
    capScores: dict[str, int] = {}
    matchScores: dict[str, float] = {}
    matchReasons: dict[str, list[str]] = {}
    scoreRev: int = 0
    requires: list[str] = []
    createdAt: int = 0
    updatedAt: int = 0
    acceptedAt: int | None = None
    releasedAt: int | None = None
    completedAt: int | None = None
    statusLogs: list[dict] = []


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
    aiTasks: dict[str, AiTaskState] = {}


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


class demoBootstrapResponse(BaseModel):
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
    llmBudgetSec: float = 1.0
    configFile: str
    envKeys: list[str]
    candidateFields: list[str]
    selectionRules: dict[str, str]
    responseFormat: dict[str, str]
    systemPrompt: str
    mapProvider: dict = {}
