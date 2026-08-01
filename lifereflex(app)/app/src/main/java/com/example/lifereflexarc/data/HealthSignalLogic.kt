package com.example.lifereflexarc.data

/**
 * Pure logic shared by [HealthConnectHealthSignalProvider] and covered by JVM unit tests.
 * Kept free of Android / Health Connect SDK references so it runs on the host JVM.
 */
object HealthSignalLogic {

    fun buildRiskTags(heartRateBpm: Int?, bloodOxygenPercent: Double?): List<String> =
        buildList {
            if (heartRateBpm != null) {
                if (heartRateBpm >= 100) add("tachycardia")
                if (heartRateBpm <= 60) add("bradycardia")
            }
            if (bloodOxygenPercent != null && bloodOxygenPercent < 95.0) {
                add("low_spo2")
            }
        }

    fun sleepQuality(durationHours: Double): String = when {
        durationHours >= 7.0 -> "good"
        durationHours >= 5.0 -> "fair"
        else -> "poor"
    }

    fun activityLevel(stepsToday: Long?): String? = when {
        stepsToday == null -> null
        stepsToday >= 10_000 -> "high"
        stepsToday >= 5_000 -> "normal"
        else -> "low"
    }

    fun pressureScore(condition: HealthCondition): Int = when (condition) {
        HealthCondition.CARDIAC_RISK -> 78
        HealthCondition.ATHLETIC -> 24
        HealthCondition.LIMITED_MOBILITY -> 55
        HealthCondition.GENERAL -> 30
    }

    fun fallbackSummary(condition: HealthCondition): HealthSignalSummary = when (condition) {
        HealthCondition.CARDIAC_RISK -> HealthSignalSummary(
            heartRateBpm = 118, bloodOxygenPercent = 92.0, pressureScore = 82,
            riskTags = listOf("tachycardia", "low_spo2"),
        )
        HealthCondition.ATHLETIC -> HealthSignalSummary(
            heartRateBpm = 84, bloodOxygenPercent = 99.0, pressureScore = 24,
            riskTags = emptyList(),
        )
        else -> HealthSignalSummary(
            heartRateBpm = 80, bloodOxygenPercent = 98.0, pressureScore = 35,
            riskTags = emptyList(),
        )
    }

    fun fallbackNote(authStatus: String): String = when (authStatus) {
        "pending" -> "Health Connect 已安装但未授权；请点击授权以读取真实健康数据。"
        else -> "未检测到 Health Connect；当前展示样例摘要。"
    }
}
