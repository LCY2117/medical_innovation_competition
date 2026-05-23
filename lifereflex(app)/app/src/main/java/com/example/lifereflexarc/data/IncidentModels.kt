package com.example.lifereflexarc.data

data class IncidentState(
    val incidentId: String,
    val phase: String,
    val sos: SosState? = null,
    val roles: RoleStates,
    val logs: List<LogEntry>,
    val patientUserId: String? = null,
    val dispatchSource: String? = null,
    val aedSites: List<AedSite> = emptyList(),
    val dispatchRationale: Map<String, DispatchRoleDecision> = emptyMap(),
)

fun IncidentState.isArchived(): Boolean = phase == "ARCHIVED"

data class SosState(
    val status: String,
    val startTs: Long?,
    val durationSec: Int,
)

data class RoleStates(
    val PRIME: RoleState,
    val RUNNER: RoleState,
    val GUIDE: RoleState,
)

data class RoleState(
    val status: String?,
    val userId: String?,
)

data class LogEntry(
    val ts: Long,
    val msg: String,
)

data class GeoPoint(
    val latitude: Double,
    val longitude: Double,
    val accuracyMeters: Double? = null,
    val label: String? = null,
    val floor: String? = null,
    val source: String = "manual",
    val updatedTs: Long? = null,
)

data class AedSite(
    val siteId: String,
    val name: String,
    val location: GeoPoint,
    val status: String = "AVAILABLE",
    val accessNotes: String = "",
    val lastCheckedTs: Long? = null,
)

data class DispatchRoleDecision(
    val userId: String? = null,
    val score: Double = 0.0,
    val reasons: List<String> = emptyList(),
    val warnings: List<String> = emptyList(),
    val distanceToPatientMeters: Double? = null,
    val nearestAedSiteId: String? = null,
    val distanceToAedMeters: Double? = null,
    val aedToPatientMeters: Double? = null,
)

data class HealthSignalSummary(
    val source: String = "unavailable",
    val authorizationStatus: String = "not_connected",
    val provider: String = "OPPO_HEALTH",
    val heartRateBpm: Int? = null,
    val bloodOxygenPercent: Double? = null,
    val pressureScore: Int? = null,
    val activityLevel: String? = null,
    val sleepQuality: String? = null,
    val riskTags: List<String> = emptyList(),
    val updatedTs: Long? = null,
    val note: String? = null,
)

data class HealthIntegrationReadiness(
    val providerName: String = "OPPO_HEALTH_MOCK",
    val heytapHealthInstalled: Boolean = false,
    val heytapMarketAvailable: Boolean = false,
    val realSdkAvailable: Boolean = false,
    val statusText: String = "健康摘要样例接入",
    val detailText: String = "真实健康授权完成前，系统使用健康摘要样例维持协同流程闭环。",
)

data class CreateIncidentResponse(
    val incidentId: String,
)

data class MutationResponse(
    val incidentId: String,
    val phase: String,
)

data class JoinRequest(
    val role: String,
    val userId: String,
)

data class ActionRequest(
    val action: String,
    val userId: String,
)

data class AutoJoinRequest(
    val userId: String,
)

data class AutoJoinResponse(
    val ok: Boolean,
    val incidentId: String,
    val role: String,
)

data class ClientRegisterRequest(
    val userId: String,
    val displayName: String,
    val organization: String,
    val healthCondition: String,
    val professionIdentity: String,
    val profileBio: String,
    val deviceType: String = "ANDROID",
    val location: GeoPoint? = null,
    val healthSignals: HealthSignalSummary? = null,
)

data class ClientLocationUpdateRequest(
    val userId: String,
    val location: GeoPoint,
)

data class ClientHealthUpdateRequest(
    val userId: String,
    val healthSignals: HealthSignalSummary,
)

data class WsMessage(
    val type: String,
    val payload: IncidentState?,
)
