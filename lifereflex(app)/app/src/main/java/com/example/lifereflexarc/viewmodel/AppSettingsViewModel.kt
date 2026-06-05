package com.example.lifereflexarc.viewmodel

import android.app.Application
import android.content.Context
import androidx.lifecycle.AndroidViewModel
import com.example.lifereflexarc.data.AppSettings
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class AppSettingsViewModel(application: Application) : AndroidViewModel(application) {
    private val prefs = application.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    private val _settings = MutableStateFlow(loadSettings())
    val settings: StateFlow<AppSettings> = _settings.asStateFlow()

    fun setVoiceGuidanceEnabled(enabled: Boolean) {
        update(_settings.value.copy(voiceGuidanceEnabled = enabled))
    }

    fun setVibrationAlertEnabled(enabled: Boolean) {
        update(_settings.value.copy(vibrationAlertEnabled = enabled))
    }

    fun setbetaSafetyAcknowledged(enabled: Boolean) {
        update(_settings.value.copy(betaSafetyAcknowledged = enabled))
    }

    private fun update(next: AppSettings) {
        _settings.value = next
        prefs.edit()
            .putBoolean(KEY_VOICE, next.voiceGuidanceEnabled)
            .putBoolean(KEY_VIBRATION, next.vibrationAlertEnabled)
            .putBoolean(KEY_beta_SAFETY, next.betaSafetyAcknowledged)
            .apply()
    }

    private fun loadSettings(): AppSettings {
        return AppSettings(
            voiceGuidanceEnabled = prefs.getBoolean(KEY_VOICE, true),
            vibrationAlertEnabled = prefs.getBoolean(KEY_VIBRATION, true),
            betaSafetyAcknowledged = prefs.getBoolean(KEY_beta_SAFETY, true),
        )
    }

    private companion object {
        const val PREFS_NAME = "lra_app_settings"
        const val KEY_VOICE = "voice_guidance_enabled"
        const val KEY_VIBRATION = "vibration_alert_enabled"
        const val KEY_beta_SAFETY = "beta_safety_acknowledged"
    }
}
