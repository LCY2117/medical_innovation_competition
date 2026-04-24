package com.example.lifereflexarc.data

data class IncidentState(
    val incidentId: String,
    val phase: String,
    val sos: SosState? = null,
    val roles: RoleStates,
    val logs: List<LogEntry>,
    val patientUserId: String? = null,
    val dispatchSource: String? = null,
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

data class CreateIncidentResponse(
    val incidentId: String,
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
)

data class WsMessage(
    val type: String,
    val payload: IncidentState?,
)
