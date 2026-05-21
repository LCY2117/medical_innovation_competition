package com.example.lifereflexarc.data

interface HealthSignalProvider {
    val providerName: String
    suspend fun readSummary(session: UserSession): HealthSignalSummary
}
class MockOppoHealthSignalProvider : HealthSignalProvider {
    override val providerName: String = "OPPO_HEALTH_MOCK"

    override suspend fun readSummary(session: UserSession): HealthSignalSummary {
        val now = System.currentTimeMillis()
        return when (session.healthCondition) {
            HealthCondition.CARDIAC_RISK -> HealthSignalSummary(
                source = "mock",
                authorizationStatus = "authorized",
                heartRateBpm = 118,
                bloodOxygenPercent = 92.0,
                pressureScore = 82,
                activityLevel = "low",
                sleepQuality = "poor",
                riskTags = listOf("tachycardia", "low_spo2", "high_pressure"),
                updatedTs = now,
                note = "OPPO Health mock fallback for high-risk patient demo",
            )

            HealthCondition.ATHLETIC -> HealthSignalSummary(
                source = "mock",
                authorizationStatus = "authorized",
                heartRateBpm = 84,
                bloodOxygenPercent = 99.0,
                pressureScore = 28,
                activityLevel = "high",
                sleepQuality = "good",
                updatedTs = now,
                note = "OPPO Health mock fallback for high-mobility responder",
            )

            HealthCondition.LIMITED_MOBILITY -> HealthSignalSummary(
                source = "mock",
                authorizationStatus = "authorized",
                heartRateBpm = 92,
                bloodOxygenPercent = 96.0,
                pressureScore = 58,
                activityLevel = "low",
                sleepQuality = "fair",
                riskTags = listOf("limited_mobility"),
                updatedTs = now,
                note = "OPPO Health mock fallback for limited mobility responder",
            )

            HealthCondition.GENERAL -> HealthSignalSummary(
                source = "mock",
                authorizationStatus = "authorized",
                heartRateBpm = if (session.professionIdentity == ProfessionIdentity.EMERGENCY_DOCTOR) 76 else 80,
                bloodOxygenPercent = 98.0,
                pressureScore = 35,
                activityLevel = "normal",
                sleepQuality = "good",
                updatedTs = now,
                note = "OPPO Health mock fallback for stable responder",
            )
        }
    }
}
