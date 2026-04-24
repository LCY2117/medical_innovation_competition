package com.example.lifereflexarc.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.lifereflexarc.BuildConfig
import com.example.lifereflexarc.data.IncidentRepository
import com.example.lifereflexarc.data.IncidentState
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
) : ViewModel() {

    private val _incidentId = MutableStateFlow<String?>(null)
    val incidentId: StateFlow<String?> = _incidentId.asStateFlow()

    val state: StateFlow<IncidentState?> = repository.state
    val connected: StateFlow<Boolean> = repository.connected

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
    private val _connecting = MutableStateFlow(false)
    val connecting: StateFlow<Boolean> = _connecting.asStateFlow()
    private val _assignedRole = MutableStateFlow<String?>(null)
    val assignedRole: StateFlow<String?> = _assignedRole.asStateFlow()
    private val _userId = MutableStateFlow<String?>(null)

    init {
        viewModelScope.launch {
            repository.latestError.collect { value ->
                if (!value.isNullOrBlank()) {
                    _error.value = value
                }
            }
        }
    }

    fun connectCurrent(userId: String, autoJoin: Boolean = false) {
        if (_connecting.value) {
            return
        }
        viewModelScope.launch {
            try {
                _connecting.value = true
                _error.value = null
                _userId.value = userId
                val current = repository.getCurrentIncident()
                _incidentId.value = current.incidentId
                if (autoJoin) {
                    val join = repository.joinCurrentAuto(userId)
                    _assignedRole.value = join.role
                } else {
                    _assignedRole.value = null
                }
                repository.connect(current.incidentId)
            } catch (e: Exception) {
                _error.value = e.message
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
                _error.value = e.message
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
                _error.value = e.message
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
                repository.join(id, role, userId)
            } catch (e: Exception) {
                _error.value = e.message
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
        viewModelScope.launch {
            try {
                _error.value = null
                repository.action(id, action, userId)
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun sosStart() {
        val id = _incidentId.value ?: return
        viewModelScope.launch {
            try {
                _error.value = null
                repository.sosStart(id)
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun sosCancel() {
        val id = _incidentId.value ?: return
        viewModelScope.launch {
            try {
                _error.value = null
                repository.sosCancel(id)
            } catch (e: Exception) {
                _error.value = e.message
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
                _error.value = e.message
            }
        }
    }

    fun clearError() {
        _error.value = null
    }

    fun registerTerminal(userId: String, session: UserSession) {
        viewModelScope.launch {
            try {
                repository.registerClient(
                    authToken = session.authToken,
                    userId = userId,
                    displayName = session.displayName,
                    organization = session.organization,
                    healthCondition = session.healthCondition.label,
                    professionIdentity = session.professionIdentity.label,
                    profileBio = session.bio,
                )
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }

    fun disconnect() {
        repository.clearLocalState()
        _incidentId.value = null
        _assignedRole.value = null
        _userId.value = null
        _error.value = null
        _connecting.value = false
    }
}
