package com.example.lifereflexarc.viewmodel

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.lifereflexarc.BuildConfig
import com.example.lifereflexarc.data.AuthRepository
import com.example.lifereflexarc.data.AuthResponse
import com.example.lifereflexarc.data.HealthCondition
import com.example.lifereflexarc.data.IncidentArchiveEntry
import com.example.lifereflexarc.data.IncidentState
import com.example.lifereflexarc.data.ProfessionIdentity
import com.example.lifereflexarc.data.UserSession
import com.example.lifereflexarc.data.UserRole
import com.example.lifereflexarc.ui.phaseTitle
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class SessionViewModel(application: Application) : AndroidViewModel(application) {

    private val prefs = application.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val repository = AuthRepository(apiBase = BuildConfig.LRA_API_BASE)
    private val gson = Gson()

    private val _session = MutableStateFlow(loadSession())
    val session: StateFlow<UserSession> = _session.asStateFlow()
    private val _archives = MutableStateFlow(loadArchives())
    val archives: StateFlow<List<IncidentArchiveEntry>> = _archives.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading.asStateFlow()

    fun register(
        displayName: String,
        phone: String,
        password: String,
        organization: String,
        healthCondition: HealthCondition,
        professionIdentity: ProfessionIdentity,
        bio: String,
    ) {
        val normalizedPhone = normalizePhone(phone)
        val validationError = validateRegister(displayName, normalizedPhone, password, bio)
        if (validationError != null) {
            _error.value = validationError
            return
        }

        viewModelScope.launch {
            try {
                _loading.value = true
                _error.value = null
                val response = repository.register(
                    displayName = displayName.trim(),
                    phone = normalizedPhone,
                    password = password,
                    organization = organization.trim().ifBlank { "生命反射弧网络" },
                    healthCondition = healthCondition.label,
                    professionIdentity = professionIdentity.label,
                    profileBio = bio.trim(),
                )
                persistAuthSession(response)
            } catch (e: Exception) {
                _error.value = e.message ?: "注册失败"
            } finally {
                _loading.value = false
            }
        }
    }

    fun login(
        phone: String,
        password: String,
    ) {
        val normalizedPhone = normalizePhone(phone)
        if (normalizedPhone.length < 11) {
            _error.value = "请输入有效手机号"
            return
        }
        if (password.length < 4) {
            _error.value = "密码至少 4 位"
            return
        }

        viewModelScope.launch {
            try {
                _loading.value = true
                _error.value = null
                val response = repository.login(
                    phone = normalizedPhone,
                    password = password,
                )
                persistAuthSession(response)
            } catch (e: Exception) {
                _error.value = e.message ?: "登录失败"
            } finally {
                _loading.value = false
            }
        }
    }

    fun signOut() {
        prefs.edit()
            .remove(KEY_LOGGED_IN)
            .remove(KEY_USER_ID)
            .remove(KEY_AUTH_TOKEN)
            .remove(KEY_NAME)
            .remove(KEY_PHONE)
            .remove(KEY_ORGANIZATION)
            .remove(KEY_HEALTH)
            .remove(KEY_IDENTITY)
            .remove(KEY_BIO)
            .remove(KEY_CREDENTIAL)
            .apply()
        _session.value = UserSession()
        _error.value = null
        _loading.value = false
    }

    fun clearError() {
        _error.value = null
    }

    private fun persistAuthSession(response: AuthResponse) {
        val healthCondition = HealthCondition.entries.firstOrNull { it.label == response.user.healthCondition }
            ?: HealthCondition.GENERAL
        val professionIdentity = ProfessionIdentity.entries.firstOrNull { it.label == response.user.professionIdentity }
            ?: ProfessionIdentity.BASIC_KNOWLEDGE
        val newSession = UserSession(
            isLoggedIn = true,
            userId = response.user.userId,
            authToken = response.token,
            displayName = response.user.displayName,
            phone = response.user.phone,
            organization = response.user.organization,
            healthCondition = healthCondition,
            professionIdentity = professionIdentity,
            bio = response.user.profileBio,
            credentialStatus = response.user.credentialStatus,
        )
        saveSession(newSession)
        _session.value = newSession
        _error.value = null
    }

    fun recordIncidentArchive(
        incidentState: IncidentState,
        assignedRole: UserRole?,
    ) {
        val current = _session.value
        if (!current.isLoggedIn || incidentState.phase != "ARCHIVED") {
            return
        }
        val startedAt = incidentState.logs.firstOrNull()?.ts ?: System.currentTimeMillis()
        val endedAt = incidentState.logs.lastOrNull()?.ts ?: startedAt
        val isPatient = incidentState.patientUserId == current.userId
        val roleLabel = when {
            isPatient -> "患者端"
            assignedRole != null -> assignedRole.label
            else -> "协同终端"
        }
        val entry = IncidentArchiveEntry(
            incidentId = incidentState.incidentId,
            userId = current.userId,
            title = if (isPatient) "患者端救援记录已归档" else "$roleLabel 任务记录已归档",
            summary = if (isPatient) {
                "本次心脏骤停事件已完成院前协同救援，并由救护车接管。"
            } else {
                "你以${roleLabel}身份参与了本次院前协同救援，现场任务已完成并进入归档。"
            },
            roleLabel = roleLabel,
            phaseLabel = phaseTitle(incidentState.phase),
            dispatchSource = incidentState.dispatchSource ?: "规则调度",
            isPatient = isPatient,
            startedAt = startedAt,
            endedAt = endedAt,
            durationSec = ((endedAt - startedAt).coerceAtLeast(0L) / 1000L),
        )
        val next = _archives.value
            .filterNot { it.incidentId == entry.incidentId && it.userId == entry.userId }
            .plus(entry)
            .sortedByDescending { it.endedAt }
        _archives.value = next
        saveArchives(next)
    }

    private fun loadSession(): UserSession {
        val loggedIn = prefs.getBoolean(KEY_LOGGED_IN, false)
        if (!loggedIn) {
            return UserSession()
        }
        val healthValue = prefs.getString(KEY_HEALTH, HealthCondition.GENERAL.name).orEmpty()
        val healthCondition = HealthCondition.entries.firstOrNull { it.name == healthValue } ?: HealthCondition.GENERAL
        val identityValue = prefs.getString(KEY_IDENTITY, ProfessionIdentity.BASIC_KNOWLEDGE.name).orEmpty()
        val professionIdentity = ProfessionIdentity.entries.firstOrNull { it.name == identityValue }
            ?: ProfessionIdentity.BASIC_KNOWLEDGE
        return UserSession(
            isLoggedIn = true,
            userId = prefs.getString(KEY_USER_ID, "").orEmpty(),
            authToken = prefs.getString(KEY_AUTH_TOKEN, "").orEmpty(),
            displayName = prefs.getString(KEY_NAME, "").orEmpty(),
            phone = prefs.getString(KEY_PHONE, "").orEmpty(),
            organization = prefs.getString(KEY_ORGANIZATION, "").orEmpty(),
            healthCondition = healthCondition,
            professionIdentity = professionIdentity,
            bio = prefs.getString(KEY_BIO, "").orEmpty(),
            credentialStatus = prefs.getString(KEY_CREDENTIAL, "未认证").orEmpty(),
        )
    }

    private fun saveSession(session: UserSession) {
        prefs.edit()
            .putBoolean(KEY_LOGGED_IN, session.isLoggedIn)
            .putString(KEY_USER_ID, session.userId)
            .putString(KEY_AUTH_TOKEN, session.authToken)
            .putString(KEY_NAME, session.displayName)
            .putString(KEY_PHONE, session.phone)
            .putString(KEY_ORGANIZATION, session.organization)
            .putString(KEY_HEALTH, session.healthCondition.name)
            .putString(KEY_IDENTITY, session.professionIdentity.name)
            .putString(KEY_BIO, session.bio)
            .putString(KEY_CREDENTIAL, session.credentialStatus)
            .apply()
    }

    private fun loadArchives(): List<IncidentArchiveEntry> {
        val json = prefs.getString(KEY_ARCHIVES, null) ?: return emptyList()
        val type = object : TypeToken<List<IncidentArchiveEntry>>() {}.type
        return runCatching { gson.fromJson<List<IncidentArchiveEntry>>(json, type) ?: emptyList() }
            .getOrDefault(emptyList())
    }

    private fun saveArchives(entries: List<IncidentArchiveEntry>) {
        prefs.edit()
            .putString(KEY_ARCHIVES, gson.toJson(entries))
            .apply()
    }

    private fun validateRegister(
        displayName: String,
        normalizedPhone: String,
        password: String,
        bio: String,
    ): String? {
        if (displayName.isBlank()) {
            return "请输入姓名"
        }
        if (normalizedPhone.length < 11) {
            return "请输入有效手机号"
        }
        if (password.length < 4) {
            return "密码至少 4 位"
        }
        if (bio.trim().length < 8) {
            return "个人介绍至少 8 个字，便于 AI 调度"
        }
        return null
    }

    private fun normalizePhone(phone: String): String = phone.filter(Char::isDigit)

    private companion object {
        const val PREFS_NAME = "lra_session"
        const val KEY_LOGGED_IN = "logged_in"
        const val KEY_USER_ID = "user_id"
        const val KEY_AUTH_TOKEN = "auth_token"
        const val KEY_NAME = "name"
        const val KEY_PHONE = "phone"
        const val KEY_ORGANIZATION = "organization"
        const val KEY_HEALTH = "health"
        const val KEY_IDENTITY = "identity"
        const val KEY_BIO = "bio"
        const val KEY_CREDENTIAL = "credential"
        const val KEY_ARCHIVES = "archives"
    }
}
