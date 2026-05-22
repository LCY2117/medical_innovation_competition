package com.example.lifereflexarc.viewmodel

import android.app.Application
import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.lifereflexarc.BuildConfig
import com.example.lifereflexarc.data.AuthRepository
import com.example.lifereflexarc.data.AuthResponse
import com.example.lifereflexarc.data.ErrorMessages
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

    private val legacyPrefs = application.getSharedPreferences(LEGACY_PREFS_NAME, Context.MODE_PRIVATE)
    private val prefs = runCatching { createSecurePreferences(application).also { migrateLegacyPreferences(it) } }
        .getOrNull()
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

    init {
        validateStoredSession()
    }

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
                _error.value = ErrorMessages.forHttpOrNetwork(e, fallback = "注册失败，请稍后重试")
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
                _error.value = ErrorMessages.forHttpOrNetwork(e, fallback = "登录失败，请稍后重试")
            } finally {
                _loading.value = false
            }
        }
    }

    fun signOut() {
        val token = _session.value.authToken
        if (token.isNotBlank()) {
            viewModelScope.launch {
                runCatching { repository.logout(token) }
            }
        }
        clearStoredSession()
        _session.value = UserSession()
        _error.value = null
        _loading.value = false
    }

    fun clearError() {
        _error.value = null
    }

    private fun validateStoredSession() {
        val current = _session.value
        if (!current.isLoggedIn || current.authToken.isBlank()) {
            return
        }
        if (current.tokenExpiresAt != null && current.tokenExpiresAt <= System.currentTimeMillis()) {
            clearStoredSession()
            _session.value = UserSession()
            _error.value = "登录态已过期，请重新登录"
            return
        }
        viewModelScope.launch {
            try {
                val response = repository.me(current.authToken)
                persistAuthSession(
                    AuthResponse(
                        ok = response.ok,
                        token = current.authToken,
                        user = response.user,
                        tokenExpiresAt = response.tokenExpiresAt,
                    )
                )
            } catch (e: Exception) {
                if (ErrorMessages.isUnauthorized(e)) {
                    clearStoredSession()
                    _session.value = UserSession()
                    _error.value = "登录态已失效，请重新登录"
                } else {
                    _error.value = ErrorMessages.forHttpOrNetwork(e, fallback = "暂时无法校验登录态，稍后会自动恢复")
                }
            }
        }
    }

    private fun clearStoredSession() {
        prefs?.let { activePrefs ->
            activePrefs.edit()
                .remove(KEY_LOGGED_IN)
                .remove(KEY_USER_ID)
                .remove(KEY_AUTH_TOKEN)
                .remove(KEY_TOKEN_EXPIRES_AT)
                .remove(KEY_NAME)
                .remove(KEY_PHONE)
                .remove(KEY_ORGANIZATION)
                .remove(KEY_HEALTH)
                .remove(KEY_IDENTITY)
                .remove(KEY_BIO)
                .remove(KEY_CREDENTIAL)
                .apply()
        }
        legacyPrefs.edit()
            .remove(KEY_LOGGED_IN)
            .remove(KEY_USER_ID)
            .remove(KEY_AUTH_TOKEN)
            .remove(KEY_TOKEN_EXPIRES_AT)
            .remove(KEY_NAME)
            .remove(KEY_PHONE)
            .remove(KEY_ORGANIZATION)
            .remove(KEY_HEALTH)
            .remove(KEY_IDENTITY)
            .remove(KEY_BIO)
            .remove(KEY_CREDENTIAL)
            .apply()
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
            tokenExpiresAt = response.tokenExpiresAt,
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
            taskSummary = archiveTaskSummary(incidentState, assignedRole, isPatient),
        )
        val next = _archives.value
            .filterNot { it.incidentId == entry.incidentId && it.userId == entry.userId }
            .plus(entry)
            .sortedByDescending { it.endedAt }
        _archives.value = next
        saveArchives(next)
    }

    private fun loadSession(): UserSession {
        val activePrefs = prefs ?: return UserSession()
        val loggedIn = activePrefs.getBoolean(KEY_LOGGED_IN, false)
        if (!loggedIn) {
            return UserSession()
        }
        val healthValue = activePrefs.getString(KEY_HEALTH, HealthCondition.GENERAL.name).orEmpty()
        val healthCondition = HealthCondition.entries.firstOrNull { it.name == healthValue } ?: HealthCondition.GENERAL
        val identityValue = activePrefs.getString(KEY_IDENTITY, ProfessionIdentity.BASIC_KNOWLEDGE.name).orEmpty()
        val professionIdentity = ProfessionIdentity.entries.firstOrNull { it.name == identityValue }
            ?: ProfessionIdentity.BASIC_KNOWLEDGE
        return UserSession(
            isLoggedIn = true,
            userId = activePrefs.getString(KEY_USER_ID, "").orEmpty(),
            authToken = activePrefs.getString(KEY_AUTH_TOKEN, "").orEmpty(),
            displayName = activePrefs.getString(KEY_NAME, "").orEmpty(),
            phone = activePrefs.getString(KEY_PHONE, "").orEmpty(),
            organization = activePrefs.getString(KEY_ORGANIZATION, "").orEmpty(),
            healthCondition = healthCondition,
            professionIdentity = professionIdentity,
            bio = activePrefs.getString(KEY_BIO, "").orEmpty(),
            credentialStatus = activePrefs.getString(KEY_CREDENTIAL, "未认证").orEmpty(),
            tokenExpiresAt = if (activePrefs.contains(KEY_TOKEN_EXPIRES_AT)) {
                activePrefs.getLong(KEY_TOKEN_EXPIRES_AT, 0L).takeIf { it > 0L }
            } else {
                null
            },
        )
    }

    private fun saveSession(session: UserSession) {
        val activePrefs = prefs ?: return
        val editor = activePrefs.edit()
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
        if (session.tokenExpiresAt != null) {
            editor.putLong(KEY_TOKEN_EXPIRES_AT, session.tokenExpiresAt)
        } else {
            editor.remove(KEY_TOKEN_EXPIRES_AT)
        }
        editor.apply()
    }

    private fun loadArchives(): List<IncidentArchiveEntry> {
        val json = prefs?.getString(KEY_ARCHIVES, null) ?: return emptyList()
        val type = object : TypeToken<List<IncidentArchiveEntry>>() {}.type
        return runCatching { gson.fromJson<List<IncidentArchiveEntry>>(json, type) ?: emptyList() }
            .getOrDefault(emptyList())
    }

    private fun saveArchives(entries: List<IncidentArchiveEntry>) {
        prefs?.let { activePrefs ->
            activePrefs.edit()
                .putString(KEY_ARCHIVES, gson.toJson(entries))
                .apply()
        }
    }

    private fun createSecurePreferences(context: Context): SharedPreferences {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        return EncryptedSharedPreferences.create(
            context,
            SECURE_PREFS_NAME,
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
        )
    }

    private fun migrateLegacyPreferences(securePrefs: SharedPreferences) {
        if (securePrefs.getBoolean(KEY_SECURE_MIGRATED, false)) {
            return
        }
        val legacyValues = legacyPrefs.all
        val keysToMigrate = SECURE_STORAGE_KEYS.filter { legacyValues.containsKey(it) }
        if (keysToMigrate.isEmpty()) {
            securePrefs.edit().putBoolean(KEY_SECURE_MIGRATED, true).apply()
            return
        }

        val secureEditor = securePrefs.edit()
        keysToMigrate.forEach { key ->
            when (val value = legacyValues[key]) {
                is Boolean -> secureEditor.putBoolean(key, value)
                is Float -> secureEditor.putFloat(key, value)
                is Int -> secureEditor.putInt(key, value)
                is Long -> secureEditor.putLong(key, value)
                is String -> secureEditor.putString(key, value)
            }
        }
        secureEditor.putBoolean(KEY_SECURE_MIGRATED, true).apply()

        val legacyEditor = legacyPrefs.edit()
        keysToMigrate.forEach { key -> legacyEditor.remove(key) }
        legacyEditor.putBoolean(KEY_SECURE_MIGRATED, true).apply()
    }

    private fun archiveTaskSummary(
        incidentState: IncidentState,
        assignedRole: UserRole?,
        isPatient: Boolean,
    ): List<String> {
        if (isPatient) {
            return listOf(
                "患者端触发或接入 SOS 协同流程",
                "等待核心施救、AED 保障和环境清障任务到场",
                "事件完成交接后进入匿名化协同记录",
            )
        }
        return when (assignedRole) {
            UserRole.PRIME -> listOf(
                "确认响应核心施救任务",
                if (incidentState.roles.PRIME.status == "AED_SHOCK_DELIVERED") "完成 AED 分析与一次除颤记录" else "执行 CPR 并等待 AED 链路",
                "配合救护车到场后完成交接归档",
            )
            UserRole.RUNNER -> listOf(
                "确认响应 AED 保障任务",
                if (incidentState.roles.RUNNER.status == "AED_DELIVERED") "完成 AED 取送并送达患者位置" else "参与 AED 取送链路",
                "回送距离与 AED 点位记录进入证据包",
            )
            UserRole.GUIDE -> listOf(
                "确认响应环境清障任务",
                if (incidentState.roles.GUIDE.status == "AMBULANCE_ARRIVED") "完成救护车到场接应记录" else "参与通道疏导和现场秩序维护",
                "交接状态进入本地档案与云端时间线",
            )
            UserRole.PATIENT -> listOf(
                "患者端触发或接入 SOS 协同流程",
                "等待核心施救、AED 保障和环境清障任务到场",
                "事件完成交接后进入匿名化协同记录",
            )
            null -> listOf(
                "保持在线待命，接收现场协同状态",
                "事件时间线已同步到本地档案",
            )
        }
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
            return "个人介绍至少 8 个字，便于智能调度"
        }
        return null
    }

    private fun normalizePhone(phone: String): String = phone.filter(Char::isDigit)

    private companion object {
        const val LEGACY_PREFS_NAME = "lra_session"
        const val SECURE_PREFS_NAME = "lra_session_secure"
        const val KEY_LOGGED_IN = "logged_in"
        const val KEY_USER_ID = "user_id"
        const val KEY_AUTH_TOKEN = "auth_token"
        const val KEY_TOKEN_EXPIRES_AT = "token_expires_at"
        const val KEY_NAME = "name"
        const val KEY_PHONE = "phone"
        const val KEY_ORGANIZATION = "organization"
        const val KEY_HEALTH = "health"
        const val KEY_IDENTITY = "identity"
        const val KEY_BIO = "bio"
        const val KEY_CREDENTIAL = "credential"
        const val KEY_ARCHIVES = "archives"
        const val KEY_SECURE_MIGRATED = "secure_storage_migrated"
        val SECURE_STORAGE_KEYS = listOf(
            KEY_LOGGED_IN,
            KEY_USER_ID,
            KEY_AUTH_TOKEN,
            KEY_TOKEN_EXPIRES_AT,
            KEY_NAME,
            KEY_PHONE,
            KEY_ORGANIZATION,
            KEY_HEALTH,
            KEY_IDENTITY,
            KEY_BIO,
            KEY_CREDENTIAL,
            KEY_ARCHIVES,
        )
    }
}
