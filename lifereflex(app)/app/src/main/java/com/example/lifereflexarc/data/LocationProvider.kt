package com.example.lifereflexarc.data

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

enum class LocationProviderStatus {
    SYSTEM_LOCATION,
    PERMISSION_MISSING,
    PROVIDER_DISABLED,
    LAST_KNOWN_MISSING,
    UNAVAILABLE,
    beta_FALLBACK,
}

data class LocationProviderResult(
    val location: GeoPoint,
    val status: LocationProviderStatus,
    val message: String,
)

interface LocationProvider {
    suspend fun currentLocation(fallback: GeoPoint): LocationProviderResult
}

class betaLocationProvider : LocationProvider {
    override suspend fun currentLocation(fallback: GeoPoint): LocationProviderResult {
        return LocationProviderResult(
            location = fallback,
            status = LocationProviderStatus.beta_FALLBACK,
            message = "使用演示坐标",
        )
    }
}

class AndroidSystemLocationProvider(
    private val context: Context,
) : LocationProvider {

    override suspend fun currentLocation(fallback: GeoPoint): LocationProviderResult = withContext(Dispatchers.IO) {
        if (!hasLocationPermission()) {
            return@withContext fallbackResult(
                fallback = fallback,
                status = LocationProviderStatus.PERMISSION_MISSING,
                message = "未授予定位权限，继续使用演示坐标",
            )
        }

        val manager = context.getSystemService(Context.LOCATION_SERVICE) as? LocationManager
            ?: return@withContext fallbackResult(
                fallback = fallback,
                status = LocationProviderStatus.UNAVAILABLE,
                message = "系统定位服务不可用，继续使用演示坐标",
            )

        val providers = availableProviders(manager)
        if (providers.isEmpty()) {
            return@withContext fallbackResult(
                fallback = fallback,
                status = LocationProviderStatus.PROVIDER_DISABLED,
                message = "定位开关未开启，继续使用演示坐标",
            )
        }

        val latest = latestKnownLocation(manager, providers)
            ?: return@withContext fallbackResult(
                fallback = fallback,
                status = LocationProviderStatus.LAST_KNOWN_MISSING,
                message = "暂未取得最近定位，继续使用演示坐标",
            )

        val providerName = latest.provider.orEmpty().ifBlank { "system" }
        val label = when (providerName) {
            LocationManager.GPS_PROVIDER -> "系统 GPS 定位"
            LocationManager.NETWORK_PROVIDER -> "系统网络定位"
            LocationManager.PASSIVE_PROVIDER -> "系统被动定位"
            else -> "系统定位"
        }
        LocationProviderResult(
            location = GeoPoint(
                latitude = latest.latitude,
                longitude = latest.longitude,
                accuracyMeters = if (latest.hasAccuracy()) latest.accuracy.toDouble() else null,
                label = label,
                source = "android-$providerName",
                updatedTs = latest.time.takeIf { it > 0 } ?: System.currentTimeMillis(),
            ),
            status = LocationProviderStatus.SYSTEM_LOCATION,
            message = "$label 已同步",
        )
    }

    private fun hasLocationPermission(): Boolean {
        val fine = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION)
        val coarse = ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION)
        return fine == PackageManager.PERMISSION_GRANTED || coarse == PackageManager.PERMISSION_GRANTED
    }

    private fun availableProviders(manager: LocationManager): List<String> {
        return listOf(
            LocationManager.GPS_PROVIDER,
            LocationManager.NETWORK_PROVIDER,
            LocationManager.PASSIVE_PROVIDER,
        ).filter { provider ->
            try {
                manager.isProviderEnabled(provider)
            } catch (_: Exception) {
                false
            }
        }
    }

    @SuppressLint("MissingPermission")
    private fun latestKnownLocation(manager: LocationManager, providers: List<String>): Location? {
        return providers
            .mapNotNull { provider ->
                try {
                    manager.getLastKnownLocation(provider)
                } catch (_: SecurityException) {
                    null
                } catch (_: IllegalArgumentException) {
                    null
                }
            }
            .maxByOrNull { it.time }
    }

    private fun fallbackResult(
        fallback: GeoPoint,
        status: LocationProviderStatus,
        message: String,
    ): LocationProviderResult {
        return LocationProviderResult(
            location = fallback.copy(source = "app-beta-fallback"),
            status = status,
            message = message,
        )
    }
}
