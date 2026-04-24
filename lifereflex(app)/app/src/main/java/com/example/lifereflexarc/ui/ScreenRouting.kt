package com.example.lifereflexarc.ui

import com.example.lifereflexarc.data.IncidentState

enum class Role {
    PRIME,
    RUNNER,
    GUIDE,
}

sealed class PhoneScreen {
    data object SosCountdown : PhoneScreen()
    data object EmergencyAlert : PhoneScreen()
    data object PrimeNavigation : PhoneScreen()
    data object CprMetronome : PhoneScreen()
    data object RunnerIdle : PhoneScreen()
    data object AedDelivery : PhoneScreen()
    data object GuideIdle : PhoneScreen()
    data object GuideTask : PhoneScreen()
    data object HandoverArchive : PhoneScreen()
}

fun screenFor(state: IncidentState, role: Role): PhoneScreen {
    if (state.phase == "CREATED") {
        return PhoneScreen.SosCountdown
    }
    val status = when (role) {
        Role.PRIME -> state.roles.PRIME.status
        Role.RUNNER -> state.roles.RUNNER.status
        Role.GUIDE -> state.roles.GUIDE.status
    }
    return when (role) {
        Role.PRIME -> when (status) {
            "CPR_STARTED" -> PhoneScreen.CprMetronome
            "JOINED" -> PhoneScreen.PrimeNavigation
            else -> {
                if (state.phase == "HANDOVER") PhoneScreen.HandoverArchive else PhoneScreen.EmergencyAlert
            }
        }
        Role.RUNNER -> when (status) {
            "AED_PICKED", "AED_DELIVERED", "JOINED" -> PhoneScreen.AedDelivery
            else -> {
                if (state.phase == "HANDOVER") PhoneScreen.HandoverArchive else PhoneScreen.RunnerIdle
            }
        }
        Role.GUIDE -> when (status) {
            "AMBULANCE_ARRIVED", "JOINED" -> PhoneScreen.GuideTask
            else -> PhoneScreen.GuideIdle
        }
    }
}
