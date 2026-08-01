package com.example.lifereflexarc.data

import android.content.Context
import android.content.pm.PackageManager

interface HealthSignalProvider {
    val providerName: String
    suspend fun readSummary(session: UserSession): HealthSignalSummary
    fun readiness(): HealthIntegrationReadiness = HealthIntegrationReadiness(providerName = providerName)
}

interface HealthAuthorizationProvider : HealthSignalProvider {
    val requiredPermissions: Set<String>
    suspend fun authorizationStatus(): String
}
class MockOppoHealthSignalProvider(
    private val context: Context? = null,
) : HealthSignalProvider {
    override val providerName: String = "OPPO_HEALTH_MOCK"

    override fun readiness(): HealthIntegrationReadiness {
        val heytapHealthInstalled = isPackageInstalled("com.heytap.health")
        val heytapMarketAvailable = isPackageInstalled("com.heytap.market") || isPackageInstalled("com.oppo.market")
        val statusText = if (heytapHealthInstalled) {
            "检测到欢太健康，当前为样例接入"
        } else {
            "健康摘要样例接入"
        }
        val detailText = if (heytapHealthInstalled) {
            "设备已安装健康应用；真实 OPPO 健康 SDK 授权仍需官方合作条件和用户授权页确认。"
        } else if (heytapMarketAvailable) {
            "设备可访问 OPPO/欢太应用市场；真实健康 SDK 接入前继续使用样例摘要。"
        } else {
            "未检测到欢太健康；当前仅使用样例摘要，不代表真实健康授权或临床监测。"
        }
        return HealthIntegrationReadiness(
            providerName = providerName,
            heytapHealthInstalled = heytapHealthInstalled,
            heytapMarketAvailable = heytapMarketAvailable,
            realSdkAvailable = false,
            statusText = statusText,
            detailText = detailText,
        )
    }

    override suspend fun readSummary(session: UserSession): HealthSignalSummary {
        val now = System.currentTimeMillis()
        return when (session.healthCondition) {
            HealthCondition.CARDIAC_RISK -> HealthSignalSummary(
                source = "mock",
                authorizationStatus = "sample",
                heartRateBpm = 118,
                bloodOxygenPercent = 92.0,
                pressureScore = 82,
                activityLevel = "low",
                sleepQuality = "poor",
                riskTags = listOf("tachycardia", "low_spo2", "high_pressure"),
                updatedTs = now,
                note = "健康摘要样例：高风险患者端",
            )

            HealthCondition.ATHLETIC -> HealthSignalSummary(
                source = "mock",
                authorizationStatus = "sample",
                heartRateBpm = 84,
                bloodOxygenPercent = 99.0,
                pressureScore = 28,
                activityLevel = "high",
                sleepQuality = "good",
                updatedTs = now,
                note = "健康摘要样例：高机动响应者",
            )

            HealthCondition.LIMITED_MOBILITY -> HealthSignalSummary(
                source = "mock",
                authorizationStatus = "sample",
                heartRateBpm = 92,
                bloodOxygenPercent = 96.0,
                pressureScore = 58,
                activityLevel = "low",
                sleepQuality = "fair",
                riskTags = listOf("limited_mobility"),
                updatedTs = now,
                note = "健康摘要样例：行动受限响应者",
            )

            HealthCondition.GENERAL -> HealthSignalSummary(
                source = "mock",
                authorizationStatus = "sample",
                heartRateBpm = if (session.professionIdentity == ProfessionIdentity.EMERGENCY_DOCTOR) 76 else 80,
                bloodOxygenPercent = 98.0,
                pressureScore = 35,
                activityLevel = "normal",
                sleepQuality = "good",
                updatedTs = now,
                note = "健康摘要样例：稳定响应者",
            )
        }
    }

    private fun isPackageInstalled(packageName: String): Boolean {
        val packageManager = context?.packageManager ?: return false
        return try {
            packageManager.getPackageInfo(packageName, 0)
            true
        } catch (_: PackageManager.NameNotFoundException) {
            false
        }
    }
}
