package com.example.lifereflexarc.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.lifereflexarc.BuildConfig
import com.example.lifereflexarc.data.ErrorMessages
import com.example.lifereflexarc.data.GeoPoint
import com.example.lifereflexarc.data.HealthIntegrationReadiness
import com.example.lifereflexarc.data.HealthSignalProvider
import com.example.lifereflexarc.data.HealthSignalSummary
import com.example.lifereflexarc.data.IncidentRepository
import com.example.lifereflexarc.data.IncidentState
import com.example.lifereflexarc.data.LocationProvider
import com.example.lifereflexarc.data.LocationProviderStatus
import com.example.lifereflexarc.data.MockOppoHealthSignalProvider
import com.example.lifereflexarc.data.UserSession
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class IncidentViewModel(
    private val repository: IncidentRepository = IncidentRepository(
        apiBase = BuildConfig.LRA_API_BASE,
        wsBase = BuildConfig.LRA_WS_BASE,
    ),
    private val healthSignalProvider: HealthSignalProvider = MockOppoHealthSignalProvider(),
    private val locationProvider: LocationProvider? = null,
) : ViewModel() {

    private val _incidentId = MutableStateFlow<String?>(null)
    val incidentId: StateFlow<String?> = _incidentId.asStateFlow()

    val state: StateFlow<IncidentState?> = repository.state
    val connected: StateFlow<Boolean> = repository.connected

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    private val _connecting = MutableStateFlow(false)
    val connecting: StateFlow<Boolean> = _connecting.asStateFlow()
    private val _pendingAction = MutableStateFlow<String?>(null)
    val pendingAction: StateFlow<String?> = _pendingAction.asStateFlow()
    private val _assignedRole = MutableStateFlow<String?>(null)
    val assignedRole: StateFlow<String?> = _assignedRole.asStateFlow()
    private val _healthSignals = MutableStateFlow<HealthSignalSummary?>(null)
    val healthSignals: StateFlow<HealthSignalSummary?> = _healthSignals.asStateFlow()
    private val _healthReadiness = MutableStateFlow(healthSignalProvider.readiness())
    val healthReadiness: StateFlow<HealthIntegrationReadiness> = _healthReadiness.asStateFlow()
    private val _locationStatus = MutableStateFlow("定位未同步")
    val locationStatus: StateFlow<String> = _locationStatus.asStateFlow()
    private val _currentLocation = MutableStateFlow<GeoPoint?>(null)
    val currentLocation: StateFlow<GeoPoint?> = _currentLocation.asStateFlow()
    private val _userId = MutableStateFlow<String?>(null)
    private val _authToken = MutableStateFlow<String?>(null)

    init {
        viewModelScope.launch {
            repository.latestError.collect { value ->
                if (!value.isNullOrBlank()) {
                    _error.value = value
                }
            }
        }
    }

    fun connectCurrent(userId: String, authToken: String? = _authToken.value, autoJoin: Boolean = false) {
        if (_connecting.value) {
            return
        }
        viewModelScope.launch {
            try {
                _connecting.value = true
                _error.value = null
                _userId.value = userId
                if (!authToken.isNullOrBlank()) {
                    _authToken.value = authToken
                }
                val current = repository.getCurrentIncident()
                _incidentId.value = current.incidentId
                if (autoJoin) {
                    val join = repository.joinCurrentAuto(_authToken.value, userId)
                    _assignedRole.value = join.role
                    repository.getIncident(join.incidentId)
                } else {
                    _assignedRole.value = null
                }
                repository.connect(current.incidentId)
            } catch (e: Exception) {
                _error.value = operationError(e)
            } finally {
                _connecting.value = false
            }
        }
    }

    fun connect(incidentId: String) {
        if (_connecting.value) {
            return
        }
        viewModelScope.launch {
            try {
                _connecting.value = true
                _error.value = null
                _assignedRole.value = null
                val incident = repository.getIncident(incidentId)
                _incidentId.value = incident.incidentId
                repository.connect(incident.incidentId)
            } catch (e: Exception) {
                _error.value = operationError(e)
            } finally {
                _connecting.value = false
            }
        }
    }

    fun createIncident() {
        viewModelScope.launch {
            try {
                _error.value = null
                _assignedRole.value = null
                val id = repository.createIncident()
                _incidentId.value = id
                repository.connect(id)
            } catch (e: Exception) {
                _error.value = operationError(e)
            }
        }
    }

    fun joinPrime(userId: String) = join("PRIME", userId)
    fun joinRunner(userId: String) = join("RUNNER", userId)
    fun joinGuide(userId: String) = join("GUIDE", userId)

    private fun join(role: String, userId: String) {
        val id = _incidentId.value ?: return
        viewModelScope.launch {
            try {
                _error.value = null
                repository.join(_authToken.value, id, role, userId)
            } catch (e: Exception) {
                _error.value = operationError(e)
            }
        }
    }

    fun actionCprStarted(userId: String) = action("CPR_STARTED", userId)
    fun actionAedAnalysisStarted(userId: String) = action("AED_ANALYSIS_STARTED", userId)
    fun actionAedShockDelivered(userId: String) = action("AED_SHOCK_DELIVERED", userId)
    fun actionAedPicked(userId: String) = action("AED_PICKED", userId)
    fun actionAedDelivered(userId: String) = action("AED_DELIVERED", userId)
    fun actionAmbulanceArrived(userId: String) = action("AMBULANCE_ARRIVED", userId)
    fun actionHandoverCompleted(userId: String) = action("HANDOVER_COMPLETED", userId)

    private fun action(action: String, userId: String) {
        val id = _incidentId.value ?: return
        if (_pendingAction.value != null) {
            return
        }
        _pendingAction.value = action
        viewModelScope.launch {
            try {
                _error.value = null
                repository.action(_authToken.value, id, action, userId)
            } catch (e: Exception) {
                _error.value = operationError(e)
            } finally {
                if (_pendingAction.value == action) {
                    _pendingAction.value = null
                }
            }
        }
    }

    fun sosStart() {
        val id = _incidentId.value ?: return
        viewModelScope.launch {
            try {
                _error.value = null
                repository.patientSosStart(_authToken.value, id)
            } catch (e: Exception) {
                _error.value = operationError(e)
            }
        }
    }

    fun sosCancel() {
        val id = _incidentId.value ?: return
        viewModelScope.launch {
            try {
                _error.value = null
                repository.patientSosCancel(_authToken.value, id)
            } catch (e: Exception) {
                _error.value = operationError(e)
            }
        }
    }

    fun triggerIncident() {
        val id = _incidentId.value ?: return
        viewModelScope.launch {
            try {
                _error.value = null
                repository.trigger(id)
            } catch (e: Exception) {
                _error.value = operationError(e)
            }
        }
    }

    fun clearError() {
        _error.value = null
    }

    fun registerTerminal(userId: String, session: UserSession) {
        _authToken.value = session.authToken
        _userId.value = userId
        viewModelScope.launch {
            try {
                val healthSignals = healthSignalProvider.readSummary(session)
                _healthReadiness.value = healthSignalProvider.readiness()
                val fallbackLocation = demoLocationFor(
                    session.displayName,
                    session.professionIdentity.label,
                    session.healthCondition.label,
                )
                val locationResult = bestAvailableLocation(fallbackLocation)
                _healthSignals.value = healthSignals
                repository.registerClient(
                    authToken = session.authToken,
                    userId = userId,
                    displayName = session.displayName,
                    organization = session.organization,
                    healthCondition = session.healthCondition.label,
                    professionIdentity = session.professionIdentity.label,
                    profileBio = session.bio,
                    location = locationResult.location,
                    healthSignals = healthSignals,
                )
                _currentLocation.value = locationResult.location
                _locationStatus.value = locationResult.message
                repository.updateHealth(
                    authToken = session.authToken,
                    userId = userId,
                    healthSignals = healthSignals,
                )
            } catch (e: Exception) {
                _error.value = operationError(e)
            }
        }
    }

    fun updatedemoLocation(userId: String, label: String, latitude: Double, longitude: Double) {
        viewModelScope.launch {
            try {
                _error.value = null
                val location = GeoPoint(
                    latitude = latitude,
                    longitude = longitude,
                    label = label,
                    source = "app-demo",
                )
                repository.updateLocation(
                    authToken = _authToken.value,
                    userId = userId,
                    location = location,
                )
                _currentLocation.value = location
                _locationStatus.value = "已切换到协同点位：$label"
            } catch (e: Exception) {
                _error.value = operationError(e)
            }
        }
    }

    fun syncSystemLocation(userId: String) {
        viewModelScope.launch {
            try {
                _error.value = null
                val session = _userId.value
                if (session.isNullOrBlank()) {
                    _locationStatus.value = "请先登录并注册终端"
                    return@launch
                }
                val fallback = _currentLocation.value ?: GeoPoint(
                    latitude = 39.904260,
                    longitude = 116.407330,
                    label = "校园中心点",
                    floor = "1F",
                    source = "app-demo-fallback",
                )
                val result = bestAvailableLocation(fallback)
                repository.updateLocation(
                    authToken = _authToken.value,
                    userId = userId,
                    location = result.location,
                )
                _currentLocation.value = result.location
                _locationStatus.value = result.message
            } catch (e: Exception) {
                _error.value = operationError(e)
            }
        }
    }

    fun disconnect() {
        repository.clearLocalState()
        _incidentId.value = null
        _assignedRole.value = null
        _healthSignals.value = null
        _locationStatus.value = "定位未同步"
        _currentLocation.value = null
        _userId.value = null
        _authToken.value = null
        _error.value = null
        _connecting.value = false
        _pendingAction.value = null
    }

    private fun demoLocationFor(displayName: String, professionIdentity: String, healthCondition: String): GeoPoint {
        val text = "$displayName $professionIdentity $healthCondition"
        return when {
            "心脏" in text || "患者" in text -> GeoPoint(39.904120, 116.407210, label = "教学楼 A 座 2 层走廊", floor = "2F", source = "app-demo")
            "医生" in text || "医护" in text -> GeoPoint(39.904210, 116.407260, label = "教学楼 A 座 1 层大厅", floor = "1F", source = "app-demo")
            "安保" in text || "物业" in text -> GeoPoint(39.904500, 116.407620, label = "校门岗亭", floor = "1F", source = "app-demo")
            "体育" in text || "跑" in text -> GeoPoint(39.903920, 116.407020, label = "操场入口", floor = "1F", source = "app-demo")
            else -> GeoPoint(39.904260, 116.407330, label = "校园中心点", floor = "1F", source = "app-demo")
        }
    }

    private suspend fun bestAvailableLocation(fallback: GeoPoint): com.example.lifereflexarc.data.LocationProviderResult {
        val provider = locationProvider
        return if (provider == null) {
            com.example.lifereflexarc.data.LocationProviderResult(
                location = fallback,
                status = LocationProviderStatus.demo_FALLBACK,
                message = "未接入系统定位 provider，使用演示坐标",
            )
        } else {
            provider.currentLocation(fallback)
        }
    }

    private fun operationError(error: Throwable): String =
        ErrorMessages.forHttpOrNetwork(error, fallback = "协同操作失败，请稍后重试")
}
