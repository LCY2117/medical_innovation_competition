package com.example.lifereflexarc.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = RescueRed,
    onPrimary = CommandText,
    secondary = RunnerBlue,
    tertiary = GuideAmber,
    background = CommandBlack,
    onBackground = CommandText,
    surface = CommandSurface,
    onSurface = CommandText,
    surfaceVariant = CommandPanel,
    onSurfaceVariant = CommandMuted,
    outline = CommandBorder,
    error = RescueRedGlow,
    onError = CommandText,
)

private val LightColorScheme = lightColorScheme(
    primary = RescueRed,
    onPrimary = LightSurface,
    secondary = RunnerBlue,
    tertiary = GuideAmber,
    background = LightBackground,
    onBackground = LightText,
    surface = LightSurface,
    onSurface = LightText,
    surfaceVariant = LightPanel,
    onSurfaceVariant = CommandMuted,
    outline = CommandBorder,
    error = RescueRed,
    onError = LightSurface,
)

@Composable
fun LifeReflexArcTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content,
    )
}
