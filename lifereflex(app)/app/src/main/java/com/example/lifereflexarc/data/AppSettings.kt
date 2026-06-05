package com.example.lifereflexarc.data

data class AppSettings(
    val voiceGuidanceEnabled: Boolean = true,
    val vibrationAlertEnabled: Boolean = true,
    val demoSafetyAcknowledged: Boolean = true,
)
