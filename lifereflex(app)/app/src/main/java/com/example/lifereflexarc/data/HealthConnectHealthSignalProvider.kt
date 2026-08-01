package com.example.lifereflexarc.data

import android.content.Context
import android.content.pm.PackageManager
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.HeartRateRecord
import androidx.health.connect.client.records.OxygenSaturationRecord
import androidx.health.connect.client.records.SleepSessionRecord
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Instant
import java.time.temporal.ChronoUnit
import kotlin.math.roundToInt

class HealthConnectHealthSignalProvider(
    private val context: Context,
) : HealthAuthorizationProvider {

    override val providerName: String = "HEALTH_CONNECT"

    override val requiredPermissions: Set<String> = setOf(
        HealthPermission.getReadPermission(HeartRateRecord::class),
        HealthPermission.getReadPermission(OxygenSaturationRecord::class),
        HealthPermission.getReadPermission(SleepSessionRecord::class),
        HealthPermission.getReadPermission(StepsRecord::class),
    )

    private val healthConnectClient: HealthConnectClient? by lazy {
        val status = try {
            HealthConnectClient.getSdkStatus(context, HEALTH_CONNECT_PACKAGE)
        } catch (_: Exception) {
            HealthConnectClient.SDK_UNAVAILABLE
        }
        if (status == HealthConnectClient.SDK_AVAILABLE) {
            try {
                HealthConnectClient.getOrCreate(context)
            } catch (_: Exception) {
                null
            }
        } else {
            null
        }
    }

    override fun readiness(): HealthIntegrationReadiness {
        val heytapHealthInstalled = isPackageInstalled("com.heytap.health")
        val sdkAvailable = healthConnectClient != null
        val statusText = when {
            sdkAvailable -> "Health Connect 已就绪"
            heytapHealthInstalled -> "欢太健康已安装，待接入"
            else -> "未检测到 Health Connect"
        }
        val detailText = when {
            sdkAvailable -> "真实健康数据已接入。请先完成授权，系统将读取心率、血氧、睡眠与步数。"
            heytapHealthInstalled -> "设备已安装欢太健康，但未安装 Health Connect；请在应用商店安装后重新进入。"
            else -> "未检测到 Health Connect；安装后即可读取真实健康数据，当前使用样例摘要。"
        }
        return HealthIntegrationReadiness(
            providerName = providerName,
            heytapHealthInstalled = heytapHealthInstalled,
            heytapMarketAvailable = isPackageInstalled("com.heytap.market") || isPackageInstalled("com.oppo.market"),
            realSdkAvailable = sdkAvailable,
            statusText = statusText,
            detailText = detailText,
        )
    }

    override suspend fun authorizationStatus(): String {
        val client = healthConnectClient ?: return "not_connected"
        return try {
            val granted = client.permissionController.getGrantedPermissions()
            if (granted.containsAll(requiredPermissions)) "authorized" else "pending"
        } catch (_: Exception) {
            "not_connected"
        }
    }

    override suspend fun readSummary(session: UserSession): HealthSignalSummary {
        val client = healthConnectClient ?: return sampleSummary(session, "not_connected")
        val granted = try {
            client.permissionController.getGrantedPermissions()
        } catch (_: Exception) {
            emptySet()
        }
        if (!granted.containsAll(requiredPermissions)) {
            return sampleSummary(session, "pending")
        }

        val now = Instant.now()
        val start = now.minus(7, ChronoUnit.DAYS)
        val timeFilter = TimeRangeFilter.between(start, now)

        var heartRateBpm: Int? = null
        var bloodOxygenPercent: Double? = null
        var sleepQuality: String? = null
        var stepsToday: Long? = null

        try {
            val hrRecords = client.readRecords(
                ReadRecordsRequest(recordType = HeartRateRecord::class, timeRangeFilter = timeFilter)
            ).records
            heartRateBpm = hrRecords
                .flatMap { it.samples }
                .filter { it.time >= now.minus(24, ChronoUnit.HOURS) }
                .maxByOrNull { it.time }
                ?.beatsPerMinute
                ?.toInt()
        } catch (_: Exception) {
        }

        try {
            val spo2Records = client.readRecords(
                ReadRecordsRequest(recordType = OxygenSaturationRecord::class, timeRangeFilter = timeFilter)
            ).records
            bloodOxygenPercent = spo2Records
                .filter { it.time >= now.minus(24, ChronoUnit.HOURS) }
                .maxByOrNull { it.time }
                ?.percentage
                ?.value
                ?.times(100.0)
        } catch (_: Exception) {
        }

        try {
            val sleepRecords = client.readRecords(
                ReadRecordsRequest(recordType = SleepSessionRecord::class, timeRangeFilter = timeFilter)
            ).records
            sleepQuality = sleepRecords
                .filter { it.endTime >= now.minus(24, ChronoUnit.HOURS) }
                .maxByOrNull { it.endTime }
                ?.let { session ->
                    val durationHours = (session.endTime.toEpochMilli() - session.startTime.toEpochMilli()) / 3_600_000.0
                    HealthSignalLogic.sleepQuality(durationHours)
                }
        } catch (_: Exception) {
        }

        try {
            val stepsRecords = client.readRecords(
                ReadRecordsRequest(recordType = StepsRecord::class, timeRangeFilter = TimeRangeFilter.between(start, now))
            ).records
            stepsToday = stepsRecords.sumOf { it.count }
        } catch (_: Exception) {
        }

        val riskTags = HealthSignalLogic.buildRiskTags(heartRateBpm, bloodOxygenPercent)
        val pressureScore = HealthSignalLogic.pressureScore(session.healthCondition)

        return HealthSignalSummary(
            source = "health_connect",
            authorizationStatus = "authorized",
            provider = providerName,
            heartRateBpm = heartRateBpm,
            bloodOxygenPercent = bloodOxygenPercent,
            pressureScore = pressureScore,
            activityLevel = HealthSignalLogic.activityLevel(stepsToday),
            sleepQuality = sleepQuality,
            riskTags = riskTags,
            updatedTs = System.currentTimeMillis(),
            note = "真实健康数据来自 Health Connect；未授权时回落为样例摘要。",
        )
    }

    private fun sampleSummary(session: UserSession, authStatus: String): HealthSignalSummary =
        HealthSignalLogic.fallbackSummary(session.healthCondition).copy(
            source = "health_connect",
            authorizationStatus = authStatus,
            provider = providerName,
            updatedTs = System.currentTimeMillis(),
            note = HealthSignalLogic.fallbackNote(authStatus),
        )

    private fun isPackageInstalled(packageName: String): Boolean {
        val packageManager = context.packageManager
        return try {
            packageManager.getPackageInfo(packageName, 0)
            true
        } catch (_: PackageManager.NameNotFoundException) {
            false
        }
    }

    private companion object {
        const val HEALTH_CONNECT_PACKAGE = "com.google.android.apps.healthdata"
    }
}
